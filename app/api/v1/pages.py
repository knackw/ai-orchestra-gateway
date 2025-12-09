"""
Content API endpoints for Landing Pages.

Provides structured content for:
- Documentation
- Developer Portal
- Changelog
- Contact
- Help Center
- System Status
- Blog
"""

import logging
from datetime import datetime, date
from typing import Any

from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel

from app.core.i18n import Language, t

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Pages"])


# ============================================================================
# Response Models
# ============================================================================

class DocSection(BaseModel):
    """Documentation section."""
    id: str
    title: str
    content: str
    code_example: str | None = None
    language: str = "python"


class DocCategory(BaseModel):
    """Documentation category."""
    id: str
    title: str
    description: str
    icon: str
    sections: list[DocSection]


class ChangelogEntry(BaseModel):
    """Changelog entry."""
    version: str
    date: str
    title: str
    description: str
    changes: list[dict[str, str]]
    breaking_changes: list[str] = []


class FAQItem(BaseModel):
    """FAQ item."""
    id: str
    question: str
    answer: str
    category: str


class StatusComponent(BaseModel):
    """System status component."""
    name: str
    status: str  # operational, degraded, outage, maintenance
    description: str | None = None
    uptime_percent: float = 100.0


class BlogPost(BaseModel):
    """Blog post summary."""
    id: str
    slug: str
    title: str
    excerpt: str
    author: str
    published_at: str
    tags: list[str]
    read_time_minutes: int


# ============================================================================
# Documentation Endpoint (PAGE-001a)
# ============================================================================

@router.get("/documentation")
async def get_documentation(
    lang: str = "en",
) -> dict[str, Any]:
    """
    Get documentation content.

    Args:
        lang: Language code (en, de, fr, es)

    Returns:
        Structured documentation content
    """
    categories = [
        DocCategory(
            id="getting-started",
            title="Getting Started",
            description="Quick start guide to integrate AI Orchestra Gateway",
            icon="rocket",
            sections=[
                DocSection(
                    id="introduction",
                    title="Introduction",
                    content="""
AI Orchestra Gateway is an enterprise-grade middleware for AI integration.
It provides privacy protection, multi-tenant billing, and intelligent failover
between AI providers.

Key features:
- **Privacy Shield**: Automatic PII detection and redaction
- **Multi-tenant Billing**: Credit-based billing with atomic deduction
- **Provider Failover**: Automatic failover between AI providers
- **Response Caching**: Reduce costs with intelligent caching
- **Rate Limiting**: Protect your API from abuse
""",
                ),
                DocSection(
                    id="quick-start",
                    title="Quick Start",
                    content="""
Get started with AI Orchestra Gateway in 3 simple steps:

1. **Get your API key** - Sign up and create a license key
2. **Make your first request** - Send a request to the API
3. **View your usage** - Monitor credits and analytics
""",
                    code_example="""
import httpx

response = httpx.post(
    "https://api.ai-gateway.example.com/v1/generate",
    headers={"X-License-Key": "your-license-key"},
    json={"prompt": "Hello, world!"}
)
print(response.json())
""",
                    language="python",
                ),
                DocSection(
                    id="authentication",
                    title="Authentication",
                    content="""
All API requests require authentication using a license key.
Include your license key in the `X-License-Key` header.

Your license key is tied to your tenant and determines:
- Available credits
- Rate limits
- Allowed IP addresses (optional)
""",
                    code_example="""
curl -X POST https://api.ai-gateway.example.com/v1/generate \\
  -H "X-License-Key: your-license-key" \\
  -H "Content-Type: application/json" \\
  -d '{"prompt": "Hello!"}'
""",
                    language="bash",
                ),
            ],
        ),
        DocCategory(
            id="api-reference",
            title="API Reference",
            description="Complete API documentation",
            icon="code",
            sections=[
                DocSection(
                    id="generate",
                    title="Generate Endpoint",
                    content="""
**POST /v1/generate**

Generate AI responses using configured providers.

**Request Body:**
- `prompt` (string, required): The input prompt
- `provider` (string, optional): Specific provider to use
- `max_tokens` (integer, optional): Maximum tokens in response

**Response:**
- `content`: Generated text
- `tokens_used`: Number of tokens consumed
- `provider`: Provider that handled the request
- `cached`: Whether response was from cache
""",
                    code_example="""
{
    "prompt": "Explain quantum computing",
    "provider": "anthropic",
    "max_tokens": 500
}
""",
                    language="json",
                ),
                DocSection(
                    id="health",
                    title="Health Endpoint",
                    content="""
**GET /health**

Check API health and status.

Returns status of all system components including:
- Database connectivity
- Cache availability
- Provider status
""",
                ),
            ],
        ),
        DocCategory(
            id="privacy",
            title="Privacy & Security",
            description="Privacy Shield and security features",
            icon="shield",
            sections=[
                DocSection(
                    id="privacy-shield",
                    title="Privacy Shield",
                    content="""
The Privacy Shield automatically detects and redacts PII before
sending data to AI providers. This ensures GDPR compliance and
protects sensitive information.

**Detected PII types:**
- Email addresses
- Phone numbers
- IBAN numbers
- IP addresses
- Credit card numbers

PII is replaced with placeholders like `[EMAIL_REDACTED]`.
""",
                ),
                DocSection(
                    id="ip-whitelist",
                    title="IP Whitelisting",
                    content="""
Restrict API access to specific IP addresses for enhanced security.

Configure allowed IPs in your tenant settings. Supports:
- Individual IPs (e.g., `192.168.1.1`)
- CIDR notation (e.g., `10.0.0.0/8`)
""",
                ),
            ],
        ),
        DocCategory(
            id="billing",
            title="Billing & Credits",
            description="Understand billing and credit system",
            icon="credit-card",
            sections=[
                DocSection(
                    id="credits",
                    title="Credit System",
                    content="""
AI Orchestra Gateway uses a credit-based billing system.

**How it works:**
1. Purchase credits in advance
2. Credits are deducted per API request
3. Cost depends on tokens used
4. Monitor usage in real-time

**Credit deduction formula:**
`credits = ceil(tokens_used * rate)`
""",
                ),
                DocSection(
                    id="invoices",
                    title="Invoices",
                    content="""
Invoices are automatically generated for credit purchases.

**Invoice details include:**
- Invoice number (INV-YYYY-NNNNN)
- Credits purchased
- Tax calculation
- Payment status
- Due date

Download invoices as PDF from the admin dashboard.
""",
                ),
            ],
        ),
    ]

    return {
        "categories": [cat.model_dump() for cat in categories],
        "last_updated": "2025-12-01",
        "version": "1.0",
    }


# ============================================================================
# Developer Portal Endpoint (PAGE-001b)
# ============================================================================

@router.get("/developers")
async def get_developer_portal(
    lang: str = "en",
) -> dict[str, Any]:
    """
    Get developer portal content.

    Args:
        lang: Language code

    Returns:
        Developer resources and SDK information
    """
    return {
        "sdks": [
            {
                "name": "Python SDK",
                "language": "python",
                "version": "1.0.0",
                "install": "pip install ai-orchestra-gateway",
                "docs_url": "/docs/sdk/python",
                "github_url": "https://github.com/example/ai-gateway-python",
            },
            {
                "name": "Node.js SDK",
                "language": "javascript",
                "version": "1.0.0",
                "install": "npm install @ai-orchestra/gateway",
                "docs_url": "/docs/sdk/nodejs",
                "github_url": "https://github.com/example/ai-gateway-node",
            },
            {
                "name": "Go SDK",
                "language": "go",
                "version": "1.0.0",
                "install": "go get github.com/example/ai-gateway-go",
                "docs_url": "/docs/sdk/go",
                "github_url": "https://github.com/example/ai-gateway-go",
            },
        ],
        "code_examples": [
            {
                "title": "Basic Request",
                "description": "Make a simple API request",
                "language": "python",
                "code": """
from ai_orchestra import Client

client = Client(api_key="your-license-key")
response = client.generate("Hello, world!")
print(response.content)
""",
            },
            {
                "title": "Streaming Response",
                "description": "Stream responses for long outputs",
                "language": "python",
                "code": """
from ai_orchestra import Client

client = Client(api_key="your-license-key")
for chunk in client.generate_stream("Write a story"):
    print(chunk, end="", flush=True)
""",
            },
            {
                "title": "Error Handling",
                "description": "Handle API errors gracefully",
                "language": "python",
                "code": """
from ai_orchestra import Client, APIError, RateLimitError

client = Client(api_key="your-license-key")
try:
    response = client.generate("Hello!")
except RateLimitError:
    print("Rate limited, please retry")
except APIError as e:
    print(f"API error: {e}")
""",
            },
        ],
        "api_reference": {
            "openapi_url": "/openapi.json",
            "postman_collection": "/assets/postman-collection.json",
            "base_url": "https://api.ai-gateway.example.com",
        },
        "resources": [
            {
                "title": "API Status",
                "description": "Check current API status and uptime",
                "url": "/status",
                "icon": "activity",
            },
            {
                "title": "Changelog",
                "description": "View recent updates and changes",
                "url": "/changelog",
                "icon": "git-commit",
            },
            {
                "title": "Community",
                "description": "Join our developer community",
                "url": "https://discord.gg/example",
                "icon": "users",
            },
        ],
    }


# ============================================================================
# Changelog Endpoint (PAGE-002)
# ============================================================================

@router.get("/changelog")
async def get_changelog(
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """
    Get changelog entries.

    Args:
        limit: Maximum entries to return
        offset: Offset for pagination

    Returns:
        List of changelog entries
    """
    entries = [
        ChangelogEntry(
            version="0.3.0",
            date="2025-12-07",
            title="Phase 4 & 5 Features",
            description="Major release with enterprise features and landing pages",
            changes=[
                {"type": "feature", "text": "Role-Based Access Control (RBAC)"},
                {"type": "feature", "text": "Multi-language support (i18n)"},
                {"type": "feature", "text": "Invoice generation with PDF export"},
                {"type": "feature", "text": "Response caching with Redis"},
                {"type": "feature", "text": "Provider failover and retry logic"},
                {"type": "feature", "text": "SEO optimization endpoints"},
                {"type": "improvement", "text": "Optimized Docker image size"},
            ],
        ),
        ChangelogEntry(
            version="0.2.1",
            date="2025-12-05",
            title="Admin Dashboard & Billing",
            description="Complete tenant and license management API",
            changes=[
                {"type": "feature", "text": "Tenant management API"},
                {"type": "feature", "text": "License CRUD operations"},
                {"type": "feature", "text": "App management endpoints"},
                {"type": "feature", "text": "Analytics dashboard API"},
                {"type": "fix", "text": "Fixed RLS policy for service role"},
            ],
        ),
        ChangelogEntry(
            version="0.2.0",
            date="2025-12-03",
            title="Database Schema & Billing",
            description="Complete database schema and billing system",
            changes=[
                {"type": "feature", "text": "Complete database schema"},
                {"type": "feature", "text": "Atomic credit deduction"},
                {"type": "feature", "text": "RLS tenant isolation"},
                {"type": "feature", "text": "Analytics views"},
            ],
        ),
        ChangelogEntry(
            version="0.1.0",
            date="2025-12-01",
            title="Initial Release",
            description="First release with core functionality",
            changes=[
                {"type": "feature", "text": "AI Gateway with provider abstraction"},
                {"type": "feature", "text": "Privacy Shield for PII redaction"},
                {"type": "feature", "text": "Anthropic provider integration"},
                {"type": "feature", "text": "Scaleway provider integration"},
                {"type": "feature", "text": "License-based authentication"},
            ],
        ),
    ]

    return {
        "entries": [e.model_dump() for e in entries[offset:offset + limit]],
        "total": len(entries),
        "has_more": offset + limit < len(entries),
    }


# ============================================================================
# Contact Endpoint (PAGE-003)
# ============================================================================

@router.get("/contact")
async def get_contact_info() -> dict[str, Any]:
    """
    Get contact information.

    Returns:
        Contact details and form configuration
    """
    return {
        "email": "contact@ai-gateway.example.com",
        "support_email": "support@ai-gateway.example.com",
        "sales_email": "sales@ai-gateway.example.com",
        "security_email": "security@ai-gateway.example.com",
        "address": {
            "company": "AI Orchestra Gateway GmbH",
            "street": "Example Street 123",
            "city": "Berlin",
            "postal_code": "10115",
            "country": "Germany",
        },
        "social": {
            "twitter": "https://twitter.com/ai_orchestra",
            "github": "https://github.com/ai-orchestra",
            "linkedin": "https://linkedin.com/company/ai-orchestra",
            "discord": "https://discord.gg/ai-orchestra",
        },
        "form_fields": [
            {"name": "name", "label": "Name", "type": "text", "required": True},
            {"name": "email", "label": "Email", "type": "email", "required": True},
            {"name": "company", "label": "Company", "type": "text", "required": False},
            {"name": "subject", "label": "Subject", "type": "select", "required": True,
             "options": ["Sales Inquiry", "Technical Support", "Partnership", "Other"]},
            {"name": "message", "label": "Message", "type": "textarea", "required": True},
        ],
    }


# ============================================================================
# Help Center Endpoint (PAGE-004)
# ============================================================================

@router.get("/help")
async def get_help_center(
    category: str | None = None,
    search: str | None = None,
) -> dict[str, Any]:
    """
    Get help center content.

    Args:
        category: Filter by category
        search: Search term

    Returns:
        FAQ items and help topics
    """
    faqs = [
        FAQItem(
            id="faq-1",
            question="How do I get started with AI Orchestra Gateway?",
            answer="Sign up for an account, create a license key, and make your first API request. Check our Quick Start guide for detailed instructions.",
            category="getting-started",
        ),
        FAQItem(
            id="faq-2",
            question="What AI providers are supported?",
            answer="Currently we support Anthropic Claude and Scaleway AI. More providers will be added based on demand.",
            category="features",
        ),
        FAQItem(
            id="faq-3",
            question="How does the Privacy Shield work?",
            answer="The Privacy Shield automatically detects PII (emails, phone numbers, IBANs) in your requests and redacts them before sending to AI providers.",
            category="privacy",
        ),
        FAQItem(
            id="faq-4",
            question="How is billing calculated?",
            answer="Billing is credit-based. Credits are deducted based on tokens used in each request. You can view your usage in the dashboard.",
            category="billing",
        ),
        FAQItem(
            id="faq-5",
            question="What happens if an AI provider is down?",
            answer="Our failover system automatically switches to a backup provider. You can configure primary and secondary providers in settings.",
            category="features",
        ),
        FAQItem(
            id="faq-6",
            question="Can I restrict API access by IP address?",
            answer="Yes, IP whitelisting is available. Configure allowed IPs in your tenant settings to restrict access.",
            category="security",
        ),
        FAQItem(
            id="faq-7",
            question="How do I get support?",
            answer="Contact us at support@ai-gateway.example.com or visit our Discord community for help.",
            category="support",
        ),
        FAQItem(
            id="faq-8",
            question="Is there a rate limit?",
            answer="Yes, rate limits depend on your plan. Default is 100 requests per minute. Contact sales for higher limits.",
            category="features",
        ),
    ]

    # Filter by category
    if category:
        faqs = [f for f in faqs if f.category == category]

    # Search
    if search:
        search_lower = search.lower()
        faqs = [f for f in faqs if search_lower in f.question.lower() or search_lower in f.answer.lower()]

    categories = [
        {"id": "getting-started", "name": "Getting Started", "icon": "play"},
        {"id": "features", "name": "Features", "icon": "zap"},
        {"id": "billing", "name": "Billing", "icon": "credit-card"},
        {"id": "privacy", "name": "Privacy", "icon": "shield"},
        {"id": "security", "name": "Security", "icon": "lock"},
        {"id": "support", "name": "Support", "icon": "headphones"},
    ]

    return {
        "faqs": [f.model_dump() for f in faqs],
        "categories": categories,
        "total": len(faqs),
    }


# ============================================================================
# System Status Endpoint (PAGE-005)
# ============================================================================

@router.get("/status")
async def get_system_status() -> dict[str, Any]:
    """
    Get system status information.

    Returns:
        Status of all system components
    """
    components = [
        StatusComponent(
            name="API",
            status="operational",
            description="Core API endpoints",
            uptime_percent=99.99,
        ),
        StatusComponent(
            name="Database",
            status="operational",
            description="Supabase PostgreSQL",
            uptime_percent=99.95,
        ),
        StatusComponent(
            name="Cache",
            status="operational",
            description="Redis cache layer",
            uptime_percent=99.90,
        ),
        StatusComponent(
            name="Anthropic Provider",
            status="operational",
            description="Claude API integration",
            uptime_percent=99.80,
        ),
        StatusComponent(
            name="Scaleway Provider",
            status="operational",
            description="Scaleway AI integration",
            uptime_percent=99.75,
        ),
    ]

    # Calculate overall status
    statuses = [c.status for c in components]
    if "outage" in statuses:
        overall_status = "outage"
    elif "degraded" in statuses:
        overall_status = "degraded"
    elif "maintenance" in statuses:
        overall_status = "maintenance"
    else:
        overall_status = "operational"

    incidents = [
        {
            "id": "inc-001",
            "title": "Scheduled Maintenance",
            "status": "resolved",
            "impact": "minor",
            "created_at": "2025-12-01T02:00:00Z",
            "resolved_at": "2025-12-01T04:00:00Z",
            "updates": [
                {"time": "2025-12-01T04:00:00Z", "message": "Maintenance completed successfully"},
                {"time": "2025-12-01T02:00:00Z", "message": "Starting scheduled maintenance"},
            ],
        },
    ]

    return {
        "status": overall_status,
        "components": [c.model_dump() for c in components],
        "incidents": incidents,
        "last_updated": datetime.now().isoformat() + "Z",
    }


# ============================================================================
# Blog Endpoint (PAGE-006)
# ============================================================================

@router.get("/blog")
async def get_blog_posts(
    search: str | None = None,
    tag: str | None = None,
    limit: int = Query(10, ge=1, le=50),
    offset: int = Query(0, ge=0),
) -> dict[str, Any]:
    """
    Get blog posts.

    Args:
        search: Search term
        tag: Filter by tag
        limit: Maximum posts to return
        offset: Offset for pagination

    Returns:
        List of blog posts
    """
    posts = [
        BlogPost(
            id="post-1",
            slug="introducing-ai-orchestra-gateway",
            title="Introducing AI Orchestra Gateway",
            excerpt="Learn about our new enterprise-grade AI gateway with privacy protection and intelligent failover.",
            author="AI Orchestra Team",
            published_at="2025-12-01",
            tags=["announcement", "product"],
            read_time_minutes=5,
        ),
        BlogPost(
            id="post-2",
            slug="privacy-first-ai-integration",
            title="Privacy-First AI Integration: How Our Privacy Shield Works",
            excerpt="Deep dive into our Privacy Shield technology that automatically protects PII in AI requests.",
            author="Security Team",
            published_at="2025-12-03",
            tags=["privacy", "security", "gdpr"],
            read_time_minutes=8,
        ),
        BlogPost(
            id="post-3",
            slug="building-resilient-ai-applications",
            title="Building Resilient AI Applications with Provider Failover",
            excerpt="How to ensure your AI applications stay available even when providers experience issues.",
            author="Engineering Team",
            published_at="2025-12-05",
            tags=["engineering", "resilience", "failover"],
            read_time_minutes=10,
        ),
        BlogPost(
            id="post-4",
            slug="credit-based-billing-explained",
            title="Credit-Based Billing Explained",
            excerpt="Understanding how our credit system works and how to optimize your AI costs.",
            author="Product Team",
            published_at="2025-12-06",
            tags=["billing", "costs", "optimization"],
            read_time_minutes=6,
        ),
    ]

    # Filter by tag
    if tag:
        posts = [p for p in posts if tag in p.tags]

    # Search
    if search:
        search_lower = search.lower()
        posts = [p for p in posts if search_lower in p.title.lower() or search_lower in p.excerpt.lower()]

    # Get all unique tags
    all_tags = set()
    for post in posts:
        all_tags.update(post.tags)

    return {
        "posts": [p.model_dump() for p in posts[offset:offset + limit]],
        "total": len(posts),
        "has_more": offset + limit < len(posts),
        "tags": sorted(list(all_tags)),
    }


@router.get("/blog/{slug}")
async def get_blog_post(slug: str) -> dict[str, Any]:
    """
    Get a single blog post by slug.

    Args:
        slug: Post slug

    Returns:
        Full blog post content
    """
    # In a real implementation, this would fetch from database
    posts = {
        "introducing-ai-orchestra-gateway": {
            "id": "post-1",
            "slug": "introducing-ai-orchestra-gateway",
            "title": "Introducing AI Orchestra Gateway",
            "content": """
# Introducing AI Orchestra Gateway

We're excited to announce the launch of AI Orchestra Gateway, an enterprise-grade
middleware for AI integration.

## Key Features

### Privacy Shield
Automatically detect and redact PII before sending to AI providers.

### Multi-tenant Billing
Credit-based billing with atomic deduction for accurate cost tracking.

### Provider Failover
Intelligent failover between AI providers for maximum uptime.

## Getting Started

Visit our [documentation](/docs) to get started.
""",
            "author": "AI Orchestra Team",
            "published_at": "2025-12-01",
            "tags": ["announcement", "product"],
            "read_time_minutes": 5,
        },
    }

    post = posts.get(slug)
    if not post:
        raise HTTPException(status_code=404, detail="Blog post not found")

    return post
