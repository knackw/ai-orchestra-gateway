# Commit and Push Workflow for AI Legal Ops

**Version:** 2.0

---

## Workflow Steps

### 1. Verify Status
- Tests: `pytest` (Must pass)
- Linting: `ruff check .` (Must pass)

### 2. Stage Changes
- `git add <files>`

### 3. Write Commit Message
Format: `<type>(<scope>): <subject> (<TASK-ID>)`

**Types:**
- `feat`: New feature (e.g., Privacy Shield)
- `fix`: Bug fix (e.g., Billing calculation)
- `docs`: Documentation
- `test`: Adding tests
- `chore`: Maintenance

**Example:**
```text
feat(privacy): implement email redaction (PRIVACY-001)

- Add regex pattern for email detection
- Implement DataPrivacyShield.sanitize method
- Add unit tests for email redaction

Unblocks: PRIVACY-002
```

### 4. Update CHANGELOG.md
- Add entry under `[Unreleased]`.

### 5. Push
- `git push origin main`

---

## Best Practices
- **Atomic Commits:** One task per commit.
- **No Secrets:** Check `.env` is ignored.
- **Reference Tasks:** Always include Task ID (e.g., `PRIVACY-001`).
