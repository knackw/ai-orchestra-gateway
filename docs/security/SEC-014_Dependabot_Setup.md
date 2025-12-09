# SEC-014: Dependabot Dependency Scanning

## Overview

This document describes the Dependabot setup for automated dependency security scanning and updates in the AI Orchestra Gateway project.

**Status:** Implemented
**Version:** 1.0
**Date:** 2025-12-08

## Table of Contents

- [Configuration Files](#configuration-files)
- [Scanning Coverage](#scanning-coverage)
- [Update Strategy](#update-strategy)
- [Auto-Merge Policy](#auto-merge-policy)
- [Security Review Process](#security-review-process)
- [Setup Instructions](#setup-instructions)
- [Troubleshooting](#troubleshooting)

## Configuration Files

### 1. `.github/dependabot.yml`

Main Dependabot configuration file that defines:
- Update schedules
- Package ecosystems (pip, npm, GitHub Actions, Docker)
- Grouping strategies
- Reviewers and labels
- Commit message prefixes

### 2. `.github/workflows/dependency-review.yml`

GitHub Actions workflow that runs on every PR to:
- Review dependency changes
- Scan for vulnerabilities with pip-audit
- Audit npm packages with npm audit
- Scan Docker images with Trivy
- Check license compliance

### 3. `.github/workflows/dependabot-auto-merge.yml`

Automated approval and merge workflow for Dependabot PRs:
- Auto-approves patch and minor updates
- Auto-merges patch updates only
- Comments on major updates (manual review required)

### 4. `.github/workflows/ci-cd.yaml` (Updated)

Enhanced CI/CD pipeline with integrated security scanning:
- pip-audit for Python dependencies
- Trivy for Docker image scanning
- Uploads security reports to GitHub Security tab

## Scanning Coverage

### Python (pip)

**Location:** `/requirements.txt`
**Schedule:** Weekly (Monday 06:00 CET)
**Tool:** pip-audit
**Scope:**
- All Python dependencies
- Transitive dependencies
- Security vulnerabilities from PyPI Advisory Database

**Grouping:**
- Minor/patch updates grouped together
- Security updates separate (individual PRs)

### npm (Frontend)

**Location:** `/frontend/package.json`
**Schedule:** Weekly (Monday 06:00 CET)
**Tool:** npm audit
**Scope:**
- All npm dependencies (production + dev)
- Transitive dependencies
- Security vulnerabilities from npm registry

**Grouping:**
- React ecosystem grouped
- Radix UI components grouped
- Other minor/patch updates grouped
- Security updates separate

### GitHub Actions

**Location:** `/.github/workflows/*.yml`
**Schedule:** Weekly (Monday 06:00 CET)
**Scope:**
- All GitHub Actions workflows
- Action version updates

**Grouping:**
- All actions grouped together

### Docker Base Images

**Location:** `/Dockerfile`
**Schedule:** Weekly (Monday 06:00 CET)
**Tool:** Trivy
**Scope:**
- Python base image
- Security vulnerabilities in base image layers

**Policy:**
- Only patch updates (no major/minor for Python image)

## Update Strategy

### Semantic Versioning

Dependabot follows semantic versioning (semver) for updates:

| Update Type | Example | Auto-Merge | Review Required |
|-------------|---------|------------|-----------------|
| **Patch** | 1.2.3 → 1.2.4 | ✅ Yes | ❌ No |
| **Minor** | 1.2.3 → 1.3.0 | ❌ No | ✅ Yes |
| **Major** | 1.2.3 → 2.0.0 | ❌ No | ✅ Yes (Breaking) |
| **Security** | Any version | ⚠️ Context | ✅ Always |

### Grouping Strategy

**Benefits:**
- Reduces PR noise
- Easier to review related updates together
- Maintains CI/CD stability

**Groups:**
- `python-dependencies`: All Python minor/patch updates
- `npm-dependencies`: All npm minor/patch updates
- `react-dependencies`: React, Next.js, React types
- `radix-dependencies`: Radix UI components
- `github-actions`: All GitHub Actions updates

**Not Grouped:**
- Security updates (separate PRs for visibility)
- Major version updates (breaking changes)

## Auto-Merge Policy

### Safe Auto-Merge Conditions

Auto-merge is enabled for:

1. **Patch Updates Only**
   - Version changes: x.x.X
   - Examples: 1.2.3 → 1.2.4
   - Reason: Bug fixes and security patches

2. **Must Pass CI/CD**
   - All tests pass
   - Linting passes
   - Security scans pass
   - No vulnerabilities introduced

3. **Dependabot PRs Only**
   - Actor must be `dependabot[bot]`
   - Prevents unauthorized auto-merges

### Manual Review Required

Manual review is required for:

1. **Minor Updates**
   - New features added
   - Backward compatible
   - May affect behavior

2. **Major Updates**
   - Breaking changes
   - API changes
   - Requires code updates

3. **Security Updates with High Severity**
   - Critical/High vulnerabilities
   - May require application changes
   - Need verification

## Security Review Process

### For All PRs

1. **Automated Scanning**
   - Dependency Review action runs
   - pip-audit scans Python dependencies
   - npm audit scans npm dependencies
   - Trivy scans Docker images (if changed)

2. **Results Reporting**
   - Comments posted on PR with findings
   - Artifacts uploaded for detailed review
   - Security tab updated with SARIF results

3. **License Compliance**
   - Allowed licenses checked
   - Denied licenses flagged
   - Reports generated

### For Security Updates

1. **Priority Review**
   - Security PRs labeled with `security`
   - Not grouped (separate PRs)
   - Immediate attention required

2. **Impact Assessment**
   - Check CVSS score
   - Review affected components
   - Assess application impact

3. **Testing**
   - All automated tests must pass
   - Manual testing for critical paths
   - Verify fix resolves vulnerability

4. **Documentation**
   - Update CHANGELOG.md
   - Document breaking changes
   - Update dependency notes

## Setup Instructions

### Prerequisites

1. **GitHub Repository Settings**
   ```
   Settings → General → Allow auto-merge ✅
   ```

2. **Branch Protection Rules**
   ```
   Settings → Branches → Add rule for 'master'/'main'

   ✅ Require status checks to pass before merging
   ✅ Require branches to be up to date before merging
   ✅ Status checks required:
      - Security Scan
      - Quality Check
      - Build & Scan Docker
   ```

3. **GitHub Security Settings**
   ```
   Settings → Security → Code security and analysis

   ✅ Dependency graph
   ✅ Dependabot alerts
   ✅ Dependabot security updates
   ```

### Configuration Steps

1. **Enable Dependabot**
   - Configuration is already in `.github/dependabot.yml`
   - GitHub automatically detects and starts scanning
   - First scan runs within 24 hours

2. **Configure Reviewers**
   - Update `.github/dependabot.yml`
   - Replace `ai-legal-ops-team` with actual GitHub usernames or team
   ```yaml
   reviewers:
     - "username1"
     - "username2"
   # OR
   reviewers:
     - "org/team-name"
   ```

3. **Configure Notifications**
   - Go to your GitHub notification settings
   - Enable notifications for:
     - Dependabot security alerts
     - Pull request reviews
     - Dependabot PRs

4. **Test the Setup**
   - Wait for first Dependabot run (Monday 06:00 CET)
   - Or manually trigger: Settings → Security → Dependabot alerts → Check for updates
   - Verify PRs are created
   - Check CI/CD workflows run

### Customization

#### Change Update Schedule

Edit `.github/dependabot.yml`:
```yaml
schedule:
  interval: "daily"  # or "weekly", "monthly"
  day: "monday"
  time: "06:00"
  timezone: "Europe/Berlin"
```

#### Add/Remove Package Ecosystems

Add new ecosystem in `.github/dependabot.yml`:
```yaml
- package-ecosystem: "gomod"  # for Go projects
  directory: "/"
  schedule:
    interval: "weekly"
```

#### Ignore Specific Dependencies

Add to the package ecosystem section:
```yaml
ignore:
  - dependency-name: "package-name"
    versions: ["1.x", "2.x"]
  - dependency-name: "another-package"
    update-types: ["version-update:semver-major"]
```

## Troubleshooting

### Issue: Dependabot Not Creating PRs

**Possible Causes:**
1. Repository is private and Dependabot is not enabled
2. No updates available
3. Open PR limit reached

**Solutions:**
- Check Settings → Security → Dependabot alerts
- Manually trigger: Check for updates
- Close stale Dependabot PRs
- Increase `open-pull-requests-limit` in config

### Issue: Auto-Merge Not Working

**Possible Causes:**
1. Auto-merge not enabled in repository settings
2. Branch protection rules not configured
3. CI/CD checks failing

**Solutions:**
- Enable auto-merge: Settings → General
- Configure branch protection rules
- Check CI/CD workflow logs
- Verify `dependabot-auto-merge.yml` workflow runs

### Issue: Too Many PRs Created

**Possible Causes:**
1. Many outdated dependencies
2. Grouping not configured correctly
3. Open PR limit too high

**Solutions:**
- Review and merge existing PRs
- Configure grouping in `.github/dependabot.yml`
- Lower `open-pull-requests-limit`
- Consider manual updates for major versions

### Issue: Security Scan Failing

**Possible Causes:**
1. Vulnerabilities detected
2. pip-audit/npm audit unavailable
3. Trivy scanner issues

**Solutions:**
- Review security scan output
- Update dependencies to patched versions
- Check tool availability
- Review `.github/workflows/dependency-review.yml`

## Best Practices

### 1. Regular Review Schedule

- Check Dependabot PRs weekly
- Don't let PRs accumulate
- Merge or close outdated PRs

### 2. Security Priority

- Always review security updates first
- Test security patches thoroughly
- Document security fixes in CHANGELOG

### 3. Batch Updates

- Group related updates together
- Test grouped updates as a unit
- Merge during low-traffic periods

### 4. Version Pinning

- Pin major versions in requirements
- Use compatible release specifiers
  ```
  fastapi>=0.100.0,<1.0.0  # Pin major version
  ```

### 5. Testing Strategy

- Automated tests must cover critical paths
- Add integration tests for dependencies
- Monitor production after updates

### 6. Communication

- Notify team of major updates
- Document breaking changes
- Update deployment runbooks

## Metrics and Monitoring

### Key Metrics

- **Time to Update:** Target < 7 days for security patches
- **PR Merge Rate:** Target > 80% of Dependabot PRs merged
- **Vulnerability Age:** Target 0 critical/high older than 14 days

### Monitoring

- GitHub Security tab for vulnerability dashboard
- Dependabot alerts in repository insights
- Weekly security scan reports in CI/CD artifacts

## References

- [Dependabot Documentation](https://docs.github.com/en/code-security/dependabot)
- [Dependency Review Action](https://github.com/actions/dependency-review-action)
- [pip-audit](https://github.com/pypa/pip-audit)
- [Trivy](https://github.com/aquasecurity/trivy)
- [GitHub Security Best Practices](https://docs.github.com/en/code-security/getting-started/securing-your-repository)

## Changelog

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-12-08 | Initial Dependabot setup with SEC-014 |

---

**Maintained by:** AI Legal Ops Security Team
**Last Updated:** 2025-12-08
