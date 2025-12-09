"""
UI Helper API endpoints.

Provides:
- Autosave state management
- Feedback widget
- Accessibility configuration
- UI state persistence
"""

import logging
from datetime import datetime, timezone
from typing import Any, Optional
from enum import Enum

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from app.core.security import get_current_license, LicenseInfo

logger = logging.getLogger(__name__)

router = APIRouter(tags=["UI"])


# ============================================================================
# Enums
# ============================================================================

class AutosaveStatus(str, Enum):
    """Autosave status values."""
    IDLE = "idle"
    SAVING = "saving"
    SAVED = "saved"
    ERROR = "error"
    CONFLICT = "conflict"


class FeedbackType(str, Enum):
    """Feedback types."""
    BUG = "bug"
    FEATURE = "feature"
    IMPROVEMENT = "improvement"
    QUESTION = "question"
    PRAISE = "praise"
    OTHER = "other"


class FeedbackPriority(str, Enum):
    """Feedback priority levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class FeedbackStatus(str, Enum):
    """Feedback status."""
    NEW = "new"
    ACKNOWLEDGED = "acknowledged"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


# ============================================================================
# Request/Response Models
# ============================================================================

class AutosaveState(BaseModel):
    """Autosave state."""
    status: AutosaveStatus = AutosaveStatus.IDLE
    last_saved_at: Optional[str] = None
    pending_changes: bool = False
    conflict_detected: bool = False
    retry_count: int = 0
    error_message: Optional[str] = None


class AutosaveConfig(BaseModel):
    """Autosave configuration."""
    enabled: bool = True
    interval_seconds: int = Field(default=30, ge=5, le=300)
    max_retries: int = Field(default=3, ge=1, le=10)
    show_indicator: bool = True
    indicator_position: str = "bottom-right"  # bottom-right, bottom-left, top-right, top-left
    save_on_blur: bool = True


class AutosaveRequest(BaseModel):
    """Request to update autosave data."""
    entity_type: str = Field(..., min_length=1, max_length=50)
    entity_id: str = Field(..., min_length=1, max_length=100)
    data: dict[str, Any]
    version: int = Field(..., ge=0)


class AutosaveResponse(BaseModel):
    """Response from autosave operation."""
    status: AutosaveStatus
    saved_at: str
    version: int
    conflict_data: Optional[dict[str, Any]] = None


class FeedbackCreate(BaseModel):
    """Request model for submitting feedback."""
    type: FeedbackType
    title: str = Field(..., min_length=1, max_length=200)
    description: str = Field(..., min_length=10, max_length=5000)
    priority: FeedbackPriority = FeedbackPriority.MEDIUM
    page_url: Optional[str] = None
    user_agent: Optional[str] = None
    screenshot_url: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None
    allow_contact: bool = True


class FeedbackResponse(BaseModel):
    """Response model for feedback."""
    id: str
    type: FeedbackType
    title: str
    description: str
    priority: FeedbackPriority
    status: FeedbackStatus
    page_url: Optional[str]
    created_at: str
    updated_at: str
    response: Optional[str] = None
    response_at: Optional[str] = None


class FeedbackListResponse(BaseModel):
    """Response model for feedback list."""
    feedback: list[FeedbackResponse]
    total: int
    has_more: bool


class AccessibilityConfig(BaseModel):
    """Accessibility configuration."""
    high_contrast: bool = False
    large_text: bool = False
    reduce_motion: bool = False
    screen_reader_optimized: bool = False
    keyboard_navigation: bool = True
    focus_indicators: bool = True
    color_blind_mode: Optional[str] = None  # protanopia, deuteranopia, tritanopia
    font_size_scale: float = Field(default=1.0, ge=0.5, le=2.0)
    line_height_scale: float = Field(default=1.0, ge=1.0, le=2.0)
    letter_spacing: float = Field(default=0.0, ge=0.0, le=0.5)


class UIState(BaseModel):
    """UI state persistence."""
    sidebar_collapsed: bool = False
    active_theme: str = "system"
    table_density: str = "normal"  # compact, normal, comfortable
    dashboard_layout: Optional[dict[str, Any]] = None
    pinned_items: list[str] = Field(default_factory=list)
    recent_items: list[str] = Field(default_factory=list)
    tour_completed: bool = False
    onboarding_step: int = 0


# ============================================================================
# In-Memory Storage (Mock for demo)
# ============================================================================

_autosave_store: dict[str, dict] = {}  # entity_key -> {data, version, saved_at}
_autosave_config_store: dict[str, AutosaveConfig] = {}
_feedback_store: dict[str, list[dict]] = {}  # tenant_id -> [feedback]
_accessibility_store: dict[str, AccessibilityConfig] = {}
_ui_state_store: dict[str, UIState] = {}

import secrets


def _get_entity_key(tenant_id: str, entity_type: str, entity_id: str) -> str:
    """Generate unique key for autosave entity."""
    return f"{tenant_id}:{entity_type}:{entity_id}"


# ============================================================================
# Autosave Endpoints
# ============================================================================

@router.get("/autosave/config", response_model=AutosaveConfig)
async def get_autosave_config(
    license: LicenseInfo = Depends(get_current_license),
) -> AutosaveConfig:
    """Get autosave configuration."""
    return _autosave_config_store.get(
        license.tenant_id,
        AutosaveConfig()
    )


@router.put("/autosave/config", response_model=AutosaveConfig)
async def update_autosave_config(
    config: AutosaveConfig,
    license: LicenseInfo = Depends(get_current_license),
) -> AutosaveConfig:
    """Update autosave configuration."""
    valid_positions = ["bottom-right", "bottom-left", "top-right", "top-left"]
    if config.indicator_position not in valid_positions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid indicator position. Choose from: {valid_positions}"
        )

    _autosave_config_store[license.tenant_id] = config
    logger.info(f"Updated autosave config for tenant {license.tenant_id}")

    return config


@router.post("/autosave", response_model=AutosaveResponse)
async def autosave(
    request: AutosaveRequest,
    license: LicenseInfo = Depends(get_current_license),
) -> AutosaveResponse:
    """
    Save data automatically.

    Uses optimistic locking with version numbers to detect conflicts.
    """
    entity_key = _get_entity_key(
        license.tenant_id,
        request.entity_type,
        request.entity_id
    )

    now = datetime.now(timezone.utc)
    existing = _autosave_store.get(entity_key)

    # Check for version conflict
    if existing and existing["version"] != request.version:
        logger.warning(f"Autosave conflict for {entity_key}")
        return AutosaveResponse(
            status=AutosaveStatus.CONFLICT,
            saved_at=existing["saved_at"],
            version=existing["version"],
            conflict_data=existing["data"],
        )

    # Save
    new_version = request.version + 1
    _autosave_store[entity_key] = {
        "data": request.data,
        "version": new_version,
        "saved_at": now.isoformat(),
    }

    logger.info(f"Autosaved {entity_key} (v{new_version})")

    return AutosaveResponse(
        status=AutosaveStatus.SAVED,
        saved_at=now.isoformat(),
        version=new_version,
    )


@router.get("/autosave/{entity_type}/{entity_id}", response_model=AutosaveResponse)
async def get_autosave(
    entity_type: str,
    entity_id: str,
    license: LicenseInfo = Depends(get_current_license),
) -> AutosaveResponse:
    """Get autosaved data for an entity."""
    entity_key = _get_entity_key(license.tenant_id, entity_type, entity_id)

    existing = _autosave_store.get(entity_key)

    if not existing:
        raise HTTPException(status_code=404, detail="No autosave data found")

    return AutosaveResponse(
        status=AutosaveStatus.SAVED,
        saved_at=existing["saved_at"],
        version=existing["version"],
        conflict_data=existing["data"],
    )


@router.delete("/autosave/{entity_type}/{entity_id}", status_code=204)
async def clear_autosave(
    entity_type: str,
    entity_id: str,
    license: LicenseInfo = Depends(get_current_license),
) -> None:
    """Clear autosaved data for an entity."""
    entity_key = _get_entity_key(license.tenant_id, entity_type, entity_id)

    if entity_key in _autosave_store:
        del _autosave_store[entity_key]
        logger.info(f"Cleared autosave for {entity_key}")


# ============================================================================
# Feedback Widget Endpoints
# ============================================================================

@router.post("/feedback", response_model=FeedbackResponse, status_code=201)
async def submit_feedback(
    feedback: FeedbackCreate,
    license: LicenseInfo = Depends(get_current_license),
) -> FeedbackResponse:
    """Submit user feedback."""
    now = datetime.now(timezone.utc)

    feedback_record = {
        "id": secrets.token_hex(16),
        "type": feedback.type,
        "title": feedback.title,
        "description": feedback.description,
        "priority": feedback.priority,
        "status": FeedbackStatus.NEW,
        "page_url": feedback.page_url,
        "user_agent": feedback.user_agent,
        "screenshot_url": feedback.screenshot_url,
        "metadata": feedback.metadata,
        "allow_contact": feedback.allow_contact,
        "tenant_id": license.tenant_id,
        "created_at": now.isoformat(),
        "updated_at": now.isoformat(),
        "response": None,
        "response_at": None,
    }

    if license.tenant_id not in _feedback_store:
        _feedback_store[license.tenant_id] = []
    _feedback_store[license.tenant_id].append(feedback_record)

    logger.info(f"Received feedback {feedback_record['id']} from tenant {license.tenant_id}")

    return FeedbackResponse(
        id=feedback_record["id"],
        type=feedback.type,
        title=feedback.title,
        description=feedback.description,
        priority=feedback.priority,
        status=FeedbackStatus.NEW,
        page_url=feedback.page_url,
        created_at=feedback_record["created_at"],
        updated_at=feedback_record["updated_at"],
    )


@router.get("/feedback", response_model=FeedbackListResponse)
async def list_feedback(
    type: Optional[FeedbackType] = None,
    status: Optional[FeedbackStatus] = None,
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    license: LicenseInfo = Depends(get_current_license),
) -> FeedbackListResponse:
    """List user's submitted feedback."""
    all_feedback = _feedback_store.get(license.tenant_id, [])

    # Filter
    filtered = all_feedback
    if type:
        filtered = [f for f in filtered if f["type"] == type]
    if status:
        filtered = [f for f in filtered if f["status"] == status]

    # Sort by created_at desc
    filtered.sort(key=lambda x: x["created_at"], reverse=True)

    # Paginate
    total = len(filtered)
    paginated = filtered[offset:offset + limit]

    return FeedbackListResponse(
        feedback=[
            FeedbackResponse(
                id=f["id"],
                type=f["type"],
                title=f["title"],
                description=f["description"],
                priority=f["priority"],
                status=f["status"],
                page_url=f.get("page_url"),
                created_at=f["created_at"],
                updated_at=f["updated_at"],
                response=f.get("response"),
                response_at=f.get("response_at"),
            )
            for f in paginated
        ],
        total=total,
        has_more=offset + limit < total,
    )


@router.get("/feedback/{feedback_id}", response_model=FeedbackResponse)
async def get_feedback(
    feedback_id: str,
    license: LicenseInfo = Depends(get_current_license),
) -> FeedbackResponse:
    """Get specific feedback item."""
    all_feedback = _feedback_store.get(license.tenant_id, [])

    for f in all_feedback:
        if f["id"] == feedback_id:
            return FeedbackResponse(
                id=f["id"],
                type=f["type"],
                title=f["title"],
                description=f["description"],
                priority=f["priority"],
                status=f["status"],
                page_url=f.get("page_url"),
                created_at=f["created_at"],
                updated_at=f["updated_at"],
                response=f.get("response"),
                response_at=f.get("response_at"),
            )

    raise HTTPException(status_code=404, detail="Feedback not found")


# ============================================================================
# Accessibility Endpoints
# ============================================================================

@router.get("/accessibility", response_model=AccessibilityConfig)
async def get_accessibility_config(
    license: LicenseInfo = Depends(get_current_license),
) -> AccessibilityConfig:
    """Get accessibility configuration."""
    return _accessibility_store.get(
        license.tenant_id,
        AccessibilityConfig()
    )


@router.put("/accessibility", response_model=AccessibilityConfig)
async def update_accessibility_config(
    config: AccessibilityConfig,
    license: LicenseInfo = Depends(get_current_license),
) -> AccessibilityConfig:
    """Update accessibility configuration."""
    valid_color_blind_modes = [None, "protanopia", "deuteranopia", "tritanopia"]
    if config.color_blind_mode not in valid_color_blind_modes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid color blind mode. Choose from: {valid_color_blind_modes}"
        )

    _accessibility_store[license.tenant_id] = config
    logger.info(f"Updated accessibility config for tenant {license.tenant_id}")

    return config


@router.get("/accessibility/presets")
async def get_accessibility_presets() -> dict[str, AccessibilityConfig]:
    """Get predefined accessibility presets."""
    return {
        "default": AccessibilityConfig(),
        "low_vision": AccessibilityConfig(
            high_contrast=True,
            large_text=True,
            font_size_scale=1.5,
            line_height_scale=1.5,
            focus_indicators=True,
        ),
        "motor_impairment": AccessibilityConfig(
            keyboard_navigation=True,
            focus_indicators=True,
            reduce_motion=True,
        ),
        "screen_reader": AccessibilityConfig(
            screen_reader_optimized=True,
            reduce_motion=True,
            keyboard_navigation=True,
        ),
        "color_blind_protanopia": AccessibilityConfig(
            color_blind_mode="protanopia",
        ),
        "color_blind_deuteranopia": AccessibilityConfig(
            color_blind_mode="deuteranopia",
        ),
        "dyslexia_friendly": AccessibilityConfig(
            large_text=True,
            font_size_scale=1.2,
            line_height_scale=1.5,
            letter_spacing=0.1,
        ),
    }


# ============================================================================
# UI State Persistence Endpoints
# ============================================================================

@router.get("/state", response_model=UIState)
async def get_ui_state(
    license: LicenseInfo = Depends(get_current_license),
) -> UIState:
    """Get persisted UI state."""
    return _ui_state_store.get(license.tenant_id, UIState())


@router.put("/state", response_model=UIState)
async def update_ui_state(
    state: UIState,
    license: LicenseInfo = Depends(get_current_license),
) -> UIState:
    """Update UI state."""
    valid_densities = ["compact", "normal", "comfortable"]
    if state.table_density not in valid_densities:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid table density. Choose from: {valid_densities}"
        )

    valid_themes = ["light", "dark", "system"]
    if state.active_theme not in valid_themes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid theme. Choose from: {valid_themes}"
        )

    _ui_state_store[license.tenant_id] = state
    logger.info(f"Updated UI state for tenant {license.tenant_id}")

    return state


@router.patch("/state", response_model=UIState)
async def patch_ui_state(
    updates: dict[str, Any],
    license: LicenseInfo = Depends(get_current_license),
) -> UIState:
    """Partially update UI state."""
    current = _ui_state_store.get(license.tenant_id, UIState())
    current_dict = current.model_dump()

    # Apply updates
    for key, value in updates.items():
        if key in current_dict:
            current_dict[key] = value

    updated = UIState(**current_dict)
    _ui_state_store[license.tenant_id] = updated

    return updated


@router.post("/state/pin/{item_id}", status_code=204)
async def pin_item(
    item_id: str,
    license: LicenseInfo = Depends(get_current_license),
) -> None:
    """Pin an item to the dashboard."""
    state = _ui_state_store.get(license.tenant_id, UIState())

    if item_id not in state.pinned_items:
        state.pinned_items.append(item_id)
        # Keep max 10 pinned items
        state.pinned_items = state.pinned_items[-10:]

    _ui_state_store[license.tenant_id] = state


@router.delete("/state/pin/{item_id}", status_code=204)
async def unpin_item(
    item_id: str,
    license: LicenseInfo = Depends(get_current_license),
) -> None:
    """Unpin an item from the dashboard."""
    state = _ui_state_store.get(license.tenant_id, UIState())

    if item_id in state.pinned_items:
        state.pinned_items.remove(item_id)

    _ui_state_store[license.tenant_id] = state


@router.post("/state/recent/{item_id}", status_code=204)
async def add_recent_item(
    item_id: str,
    license: LicenseInfo = Depends(get_current_license),
) -> None:
    """Add item to recent items list."""
    state = _ui_state_store.get(license.tenant_id, UIState())

    # Remove if exists (to move to front)
    if item_id in state.recent_items:
        state.recent_items.remove(item_id)

    # Add to front
    state.recent_items.insert(0, item_id)

    # Keep max 20 recent items
    state.recent_items = state.recent_items[:20]

    _ui_state_store[license.tenant_id] = state
