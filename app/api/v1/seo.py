"""
SEO and Meta Information API endpoints.

Provides:
- robots.txt generation
- sitemap.xml generation
- Open Graph meta data
- JSON-LD structured data
"""

import logging
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Request, Response
from fastapi.responses import PlainTextResponse

from app.core.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(tags=["SEO"])


# Configuration
SEO_CONFIG = {
    "site_name": "AI Orchestra Gateway",
    "site_description": "Enterprise AI Gateway with Privacy Shield, Multi-tenant Billing, and Provider Failover",
    "site_url": "https://ai-gateway.example.com",
    "site_language": "en",
    "twitter_handle": "@ai_orchestra",
    "logo_url": "/static/images/logo.png",
    "contact_email": "contact@example.com",
}


@router.get("/robots.txt", response_class=PlainTextResponse)
async def robots_txt() -> str:
    """
    Generate robots.txt for search engine crawlers.

    Returns:
        robots.txt content
    """
    content = """# AI Orchestra Gateway robots.txt
# https://ai-gateway.example.com/robots.txt

User-agent: *
Allow: /
Allow: /docs
Allow: /developers
Allow: /changelog
Allow: /help
Allow: /status
Allow: /blog

# Disallow admin and API endpoints
Disallow: /admin/
Disallow: /api/
Disallow: /v1/

# Disallow auth pages
Disallow: /login
Disallow: /register
Disallow: /forgot-password

# Sitemap location
Sitemap: https://ai-gateway.example.com/sitemap.xml

# Crawl delay for polite crawling
Crawl-delay: 1
"""
    return content


@router.get("/sitemap.xml", response_class=Response)
async def sitemap_xml() -> Response:
    """
    Generate sitemap.xml for search engines.

    Returns:
        XML sitemap
    """
    base_url = SEO_CONFIG["site_url"]
    now = datetime.now().strftime("%Y-%m-%d")

    # Define pages with their priorities and change frequencies
    pages = [
        {"loc": "/", "priority": "1.0", "changefreq": "weekly"},
        {"loc": "/docs", "priority": "0.9", "changefreq": "weekly"},
        {"loc": "/developers", "priority": "0.9", "changefreq": "weekly"},
        {"loc": "/pricing", "priority": "0.8", "changefreq": "monthly"},
        {"loc": "/changelog", "priority": "0.7", "changefreq": "weekly"},
        {"loc": "/help", "priority": "0.7", "changefreq": "monthly"},
        {"loc": "/status", "priority": "0.6", "changefreq": "daily"},
        {"loc": "/blog", "priority": "0.7", "changefreq": "daily"},
        {"loc": "/contact", "priority": "0.5", "changefreq": "yearly"},
        {"loc": "/privacy", "priority": "0.3", "changefreq": "yearly"},
        {"loc": "/terms", "priority": "0.3", "changefreq": "yearly"},
    ]

    xml_content = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_content += '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'

    for page in pages:
        xml_content += "  <url>\n"
        xml_content += f"    <loc>{base_url}{page['loc']}</loc>\n"
        xml_content += f"    <lastmod>{now}</lastmod>\n"
        xml_content += f"    <changefreq>{page['changefreq']}</changefreq>\n"
        xml_content += f"    <priority>{page['priority']}</priority>\n"
        xml_content += "  </url>\n"

    xml_content += "</urlset>"

    return Response(
        content=xml_content,
        media_type="application/xml",
    )


@router.get("/meta")
async def get_meta_info(
    path: str = "/",
    lang: str = "en",
) -> dict[str, Any]:
    """
    Get SEO meta information for a page.

    Args:
        path: Page path (e.g., "/docs", "/pricing")
        lang: Language code

    Returns:
        Meta information including Open Graph and Twitter cards
    """
    # Page-specific meta data
    page_meta = {
        "/": {
            "title": "AI Orchestra Gateway - Enterprise AI Integration",
            "description": "Secure, scalable AI gateway with privacy protection, multi-tenant billing, and intelligent failover. Integrate AI into your applications with confidence.",
            "keywords": "AI gateway, AI integration, privacy shield, multi-tenant, API gateway, Claude API, AI orchestration",
        },
        "/docs": {
            "title": "Documentation - AI Orchestra Gateway",
            "description": "Comprehensive documentation for AI Orchestra Gateway. Learn how to integrate, configure, and optimize your AI workflows.",
            "keywords": "AI gateway documentation, API reference, integration guide, tutorials",
        },
        "/developers": {
            "title": "Developer Portal - AI Orchestra Gateway",
            "description": "Resources for developers building with AI Orchestra Gateway. API references, SDKs, code examples, and best practices.",
            "keywords": "developer portal, API SDK, code examples, AI development",
        },
        "/pricing": {
            "title": "Pricing - AI Orchestra Gateway",
            "description": "Transparent pricing for AI Orchestra Gateway. Pay per credit, no hidden fees. Start free and scale as you grow.",
            "keywords": "AI gateway pricing, API pricing, usage-based pricing",
        },
        "/changelog": {
            "title": "Changelog - AI Orchestra Gateway",
            "description": "Latest updates, features, and improvements to AI Orchestra Gateway. Stay informed about new capabilities.",
            "keywords": "changelog, release notes, updates, new features",
        },
        "/help": {
            "title": "Help Center - AI Orchestra Gateway",
            "description": "Get help with AI Orchestra Gateway. FAQs, troubleshooting guides, and support resources.",
            "keywords": "help center, FAQ, support, troubleshooting",
        },
        "/status": {
            "title": "System Status - AI Orchestra Gateway",
            "description": "Real-time status of AI Orchestra Gateway services. View uptime, incidents, and maintenance schedules.",
            "keywords": "system status, uptime, service health, incidents",
        },
        "/blog": {
            "title": "Blog - AI Orchestra Gateway",
            "description": "Insights, tutorials, and news about AI integration, privacy, and enterprise AI solutions.",
            "keywords": "AI blog, AI insights, tutorials, enterprise AI",
        },
        "/contact": {
            "title": "Contact Us - AI Orchestra Gateway",
            "description": "Get in touch with the AI Orchestra Gateway team. Sales inquiries, support, and partnerships.",
            "keywords": "contact, sales, support, partnership",
        },
    }

    # Get meta for requested path or use defaults
    meta = page_meta.get(path, {
        "title": f"AI Orchestra Gateway",
        "description": SEO_CONFIG["site_description"],
        "keywords": "AI gateway, API integration",
    })

    # Build full meta response
    full_title = meta["title"]
    if path != "/":
        full_title = f"{meta['title']}"

    return {
        "title": full_title,
        "meta": {
            "description": meta["description"],
            "keywords": meta["keywords"],
            "author": SEO_CONFIG["site_name"],
            "robots": "index, follow",
            "language": lang,
        },
        "openGraph": {
            "type": "website",
            "site_name": SEO_CONFIG["site_name"],
            "title": full_title,
            "description": meta["description"],
            "url": f"{SEO_CONFIG['site_url']}{path}",
            "image": f"{SEO_CONFIG['site_url']}{SEO_CONFIG['logo_url']}",
            "locale": f"{lang}_{'DE' if lang == 'de' else 'US'}",
        },
        "twitter": {
            "card": "summary_large_image",
            "site": SEO_CONFIG["twitter_handle"],
            "title": full_title,
            "description": meta["description"],
            "image": f"{SEO_CONFIG['site_url']}{SEO_CONFIG['logo_url']}",
        },
        "canonical": f"{SEO_CONFIG['site_url']}{path}",
    }


@router.get("/structured-data")
async def get_structured_data(
    page_type: str = "organization",
) -> dict[str, Any]:
    """
    Get JSON-LD structured data for SEO.

    Args:
        page_type: Type of structured data (organization, software, faq)

    Returns:
        JSON-LD structured data
    """
    base_url = SEO_CONFIG["site_url"]

    if page_type == "organization":
        return {
            "@context": "https://schema.org",
            "@type": "Organization",
            "name": SEO_CONFIG["site_name"],
            "description": SEO_CONFIG["site_description"],
            "url": base_url,
            "logo": f"{base_url}{SEO_CONFIG['logo_url']}",
            "contactPoint": {
                "@type": "ContactPoint",
                "email": SEO_CONFIG["contact_email"],
                "contactType": "customer service",
            },
            "sameAs": [
                f"https://twitter.com/{SEO_CONFIG['twitter_handle'].replace('@', '')}",
            ],
        }

    elif page_type == "software":
        return {
            "@context": "https://schema.org",
            "@type": "SoftwareApplication",
            "name": SEO_CONFIG["site_name"],
            "description": SEO_CONFIG["site_description"],
            "applicationCategory": "DeveloperApplication",
            "operatingSystem": "Cross-platform",
            "offers": {
                "@type": "Offer",
                "price": "0",
                "priceCurrency": "EUR",
                "description": "Free tier available",
            },
            "featureList": [
                "Privacy Shield for PII protection",
                "Multi-tenant billing",
                "Provider failover",
                "Response caching",
                "Rate limiting",
            ],
        }

    elif page_type == "faq":
        return {
            "@context": "https://schema.org",
            "@type": "FAQPage",
            "mainEntity": [
                {
                    "@type": "Question",
                    "name": "What is AI Orchestra Gateway?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "AI Orchestra Gateway is an enterprise-grade middleware for AI integration, providing privacy protection, multi-tenant billing, and intelligent provider failover.",
                    },
                },
                {
                    "@type": "Question",
                    "name": "How does the Privacy Shield work?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "The Privacy Shield automatically detects and redacts personally identifiable information (PII) from requests before sending them to AI providers, ensuring GDPR compliance.",
                    },
                },
                {
                    "@type": "Question",
                    "name": "What AI providers are supported?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "AI Orchestra Gateway supports multiple providers including Anthropic Claude and Scaleway, with automatic failover between providers.",
                    },
                },
                {
                    "@type": "Question",
                    "name": "How is billing handled?",
                    "acceptedAnswer": {
                        "@type": "Answer",
                        "text": "Billing is credit-based with atomic deduction per request. You can purchase credits and track usage through the admin dashboard.",
                    },
                },
            ],
        }

    elif page_type == "breadcrumb":
        return {
            "@context": "https://schema.org",
            "@type": "BreadcrumbList",
            "itemListElement": [
                {
                    "@type": "ListItem",
                    "position": 1,
                    "name": "Home",
                    "item": base_url,
                },
                {
                    "@type": "ListItem",
                    "position": 2,
                    "name": "Documentation",
                    "item": f"{base_url}/docs",
                },
            ],
        }

    else:
        return {
            "@context": "https://schema.org",
            "@type": "WebPage",
            "name": SEO_CONFIG["site_name"],
            "description": SEO_CONFIG["site_description"],
            "url": base_url,
        }


@router.get("/security.txt", response_class=PlainTextResponse)
async def security_txt() -> str:
    """
    Generate security.txt for security researchers.

    Returns:
        security.txt content
    """
    return f"""# AI Orchestra Gateway Security Policy
# https://ai-gateway.example.com/.well-known/security.txt

Contact: mailto:security@example.com
Expires: 2026-12-31T23:59:59.000Z
Encryption: https://ai-gateway.example.com/pgp-key.txt
Preferred-Languages: en, de
Canonical: https://ai-gateway.example.com/.well-known/security.txt
Policy: https://ai-gateway.example.com/security-policy

# We appreciate responsible disclosure of security vulnerabilities.
# Please report any security issues to {SEO_CONFIG['contact_email']}
"""


@router.get("/humans.txt", response_class=PlainTextResponse)
async def humans_txt() -> str:
    """
    Generate humans.txt for human visitors.

    Returns:
        humans.txt content
    """
    return """/* TEAM */
    Developer: AI Orchestra Team
    Contact: contact@example.com
    Location: Germany

/* SITE */
    Last update: 2025/12/01
    Language: English, German, French, Spanish
    Standards: HTML5, CSS3, ES2022
    Components: FastAPI, Supabase, Redis
    Software: Python 3.12

/* THANKS */
    Anthropic for Claude API
    The open source community
"""


@router.get("/llms.txt", response_class=PlainTextResponse)
async def llms_txt() -> str:
    """
    Generate llms.txt for LLM/AI crawlers and agents.

    This file provides structured information about the API
    for AI assistants and LLM-based tools to understand
    how to interact with the service.

    See: https://llmstxt.org/

    Returns:
        llms.txt content
    """
    return f"""# {SEO_CONFIG['site_name']}

> {SEO_CONFIG['site_description']}

## Overview

AI Orchestra Gateway is an enterprise-grade middleware for integrating AI capabilities
into applications. It provides privacy protection, multi-tenant billing, and intelligent
provider failover.

## Core Features

- **Privacy Shield**: Automatic PII detection and redaction (Email, Phone, IBAN)
- **Multi-Provider Support**: Anthropic Claude, Scaleway AI with automatic failover
- **Credit-Based Billing**: Atomic credit deduction per request
- **Rate Limiting**: Configurable per-tenant rate limits
- **Response Caching**: Redis-based caching for repeated queries
- **Multi-Language**: Supports EN, DE, FR, ES

## API Endpoints

### Generate Text
- `POST /v1/generate` - Generate AI text response
  - Headers: `X-License-Key` (required)
  - Body: `{{"prompt": "Your prompt", "provider": "anthropic"}}`
  - Returns: `{{"content": "...", "tokens_used": 123, "credits_deducted": 1}}`

### Health Check
- `GET /health` - Check service health and database connectivity

### Admin Endpoints (requires X-Admin-Key)
- `GET /admin/tenants` - List tenants
- `POST /admin/tenants` - Create tenant
- `GET /admin/licenses` - List licenses
- `POST /admin/licenses` - Create license

## Authentication

All API requests require a valid license key passed via the `X-License-Key` header.
Admin operations require the `X-Admin-Key` header.

## Rate Limits

- Default: 100 requests per minute per license
- Configurable per tenant

## Pricing

Credit-based pricing:
- 1 credit = 1 token (approximately)
- Free tier: 1000 credits
- Credits never expire

## Documentation

- API Docs: {SEO_CONFIG['site_url']}/docs
- Developer Portal: {SEO_CONFIG['site_url']}/developers
- OpenAPI Spec: {SEO_CONFIG['site_url']}/openapi.json

## Contact

- Support: {SEO_CONFIG['contact_email']}
- Security: security@example.com
- Twitter: {SEO_CONFIG['twitter_handle']}

## Legal

- Privacy Policy: {SEO_CONFIG['site_url']}/privacy
- Terms of Service: {SEO_CONFIG['site_url']}/terms
- GDPR Compliant: Yes
"""
