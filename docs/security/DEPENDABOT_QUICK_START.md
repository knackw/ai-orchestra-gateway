# Dependabot Quick Start Guide

## Overview

Automated dependency security scanning for the AI Orchestra Gateway project.

## What's Configured

### 1. Automatic Updates
- **Python (pip):** Weekly scans of `requirements.txt`
- **npm (Frontend):** Weekly scans of `frontend/package.json`
- **GitHub Actions:** Weekly updates for workflow actions
- **Docker:** Weekly scans of base images

### 2. Security Scanning
- **pip-audit:** Python vulnerability scanning
- **npm audit:** JavaScript vulnerability scanning
- **Trivy:** Docker image vulnerability scanning
- **Dependency Review:** PR-based dependency analysis

### 3. Auto-Merge
- **Patch updates:** Auto-approved and auto-merged
- **Minor updates:** Auto-approved, manual merge
- **Major updates:** Manual review required

## Quick Actions

### View Dependabot Alerts
```
GitHub → Security tab → Dependabot alerts
```

### Manually Trigger Update Check
```
GitHub → Insights → Dependency graph → Dependabot → Check for updates
```

### Review Security PRs
```bash
# List all Dependabot PRs
gh pr list --author "app/dependabot"

# Review a specific PR
gh pr view <PR_NUMBER>

# Approve and merge
gh pr review <PR_NUMBER> --approve
gh pr merge <PR_NUMBER> --squash
```

## PR Labels

| Label | Meaning |
|-------|---------|
| `dependencies` | Dependency update |
| `python` | Python package update |
| `npm` | npm package update |
| `frontend` | Frontend dependency |
| `security` | Security patch |
| `github-actions` | GitHub Actions update |
| `docker` | Docker image update |

## Update Schedule

All updates run **weekly on Monday at 06:00 CET**.

## Auto-Merge Behavior

| Update Type | Auto-Approve | Auto-Merge | CI Required |
|-------------|--------------|------------|-------------|
| Patch (1.2.3 → 1.2.4) | ✅ | ✅ | ✅ |
| Minor (1.2.3 → 1.3.0) | ✅ | ❌ | ✅ |
| Major (1.2.3 → 2.0.0) | ❌ | ❌ | ✅ |
| Security (any) | ⚠️ | ⚠️ | ✅ |

## Common Tasks

### Merge a Dependabot PR
1. Check CI/CD status (all green)
2. Review the changes
3. Approve the PR
4. Merge with squash

### Handle Security Alert
1. GitHub will create a PR automatically
2. Review the vulnerability details
3. Test the update
4. Merge immediately if safe

### Ignore a Dependency
Edit `.github/dependabot.yml`:
```yaml
ignore:
  - dependency-name: "package-name"
    versions: ["1.x", "2.x"]
```

### Change Update Frequency
Edit `.github/dependabot.yml`:
```yaml
schedule:
  interval: "daily"  # or "weekly", "monthly"
```

## Troubleshooting

### No PRs Created
- Check: Settings → Security → Dependabot alerts (enabled?)
- Wait 24 hours after enabling
- Manually trigger update check

### Auto-Merge Not Working
- Check: Settings → General → Allow auto-merge (enabled?)
- Check: Branch protection rules configured?
- Check: CI/CD passing?

### Too Many PRs
- Merge or close stale PRs
- Reduce `open-pull-requests-limit` in config
- Enable grouping for related updates

## Files Reference

| File | Purpose |
|------|---------|
| `.github/dependabot.yml` | Main configuration |
| `.github/workflows/dependency-review.yml` | PR dependency scanning |
| `.github/workflows/dependabot-auto-merge.yml` | Auto-merge automation |
| `.github/workflows/ci-cd.yaml` | CI/CD with security scans |
| `docs/security/SEC-014_Dependabot_Setup.md` | Full documentation |

## Support

For detailed documentation, see:
- [SEC-014 Full Documentation](./SEC-014_Dependabot_Setup.md)
- [GitHub Dependabot Docs](https://docs.github.com/en/code-security/dependabot)

---

**Last Updated:** 2025-12-08
