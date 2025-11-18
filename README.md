# Marketing Agent System Specification - Update Summary

## Version 1.1 (2025-11-13)

### Major Changes

## 1. Image Generation: Imagen 3 → Gemini 2.5 Flash

**What Changed:**
- Replaced all references to Google Imagen 3 with Google Gemini 2.5 Flash
- Updated API integration from Vertex AI to Gemini API

**Why:**
- You're already using Gemini 2.5 Flash and happy with the results
- Simpler integration (single API vs separate Vertex AI setup)
- Potentially better pricing (~$0.01-0.02 per image vs $0.04)
- Native image generation within Gemini model

**Technical Updates:**
- **Dependency change**: `google-cloud-aiplatform` → `google-generativeai==0.3.0`
- **Tool name**: `imagen_generate` → `gemini_generate`
- **Content Agent**: Now uses Gemini 2.5 Flash API for both text prompts and image generation
- **Environment variables**: `GOOGLE_CLOUD_PROJECT` and `GOOGLE_APPLICATION_CREDENTIALS` → `GOOGLE_API_KEY`

**Cost Impact:**
- Per campaign: $0.75-0.85 → **$0.62-0.70** (about 15% cheaper)
- Image generation: $0.16-0.24 → **$0.04-0.12**

---

## 2. Storage Strategy: Added Local Development Support

**What Changed:**
- Added comprehensive local development setup using filesystem storage
- Created storage abstraction layer that works for both local and production
- Updated all storage references to support both environments

**New Capabilities:**

### Development Environment (Local)
```bash
# Zero cloud costs!
- PostgreSQL: Docker/local install ($0)
- Redis: Docker/local install ($0)
- File Storage: Local filesystem ($0)
- Only pay for API calls
```

### Production Environment (AWS)
```bash
# Scalable cloud infrastructure
- PostgreSQL: AWS RDS ($25/month)
- Redis: AWS ElastiCache ($15/month)
- File Storage: AWS S3 ($2.30/month)
```

### Storage Abstraction Layer
Added complete Python code examples for:
- `StorageBackend` abstract class
- `LocalStorage` implementation
- `S3Storage` implementation
- Factory function `get_storage()`

**Key Features:**
- ✅ **Zero code changes** when moving from dev to production
- ✅ **Environment variable driven** - just change `.env` file
- ✅ **Fast local development** - no AWS setup required
- ✅ **Easy testing** - run entire system locally
- ✅ **Gradual migration** - can mix local + cloud (e.g., local DB + S3)

**Environment Configuration:**

Development (.env.development):
```bash
DATABASE_URL=postgresql://user:pass@localhost:5432/marketing_agents
STORAGE_TYPE=local
LOCAL_STORAGE_PATH=./storage
```

Production (.env.production):
```bash
DATABASE_URL=postgresql://user:pass@rds-endpoint:5432/marketing_agents
STORAGE_TYPE=s3
S3_BUCKET=marketing-agents-production
AWS_REGION=eu-west-2
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
```

---

## Summary of File Changes

### Updated Sections:
1. **Architecture Diagram** (lines 84, 99)
   - Content Agent now shows "+ Gemini 2.5"
   - External Services box updated

2. **Content Agent Specification** (lines 295-366)
   - Responsibilities mention Gemini 2.5 Flash
   - Tools updated to `gemini_generate`
   - Image generation details updated

3. **Tech Stack** (line 1587)
   - Dependency: `google-generativeai==0.3.0`

4. **Storage Section** (line 1609)
   - Added note about local vs production

5. **New Section: Storage Strategy** (after line 1679)
   - **~150 lines of new content**
   - Complete abstraction layer code
   - Environment configuration examples
   - Migration strategy

6. **External Services** (line 1684)
   - Updated to list Gemini 2.5 Flash
   - Added local/production notes for storage and database

7. **Environment Variables** (lines 2532-2561)
   - Split into two sections: Development and Production
   - Updated Google credentials to use GOOGLE_API_KEY
   - Added STORAGE_TYPE configuration
   - Added local storage path options

8. **Cost Estimates** (lines 2456-2461)
   - Image generation: $0.16-0.24 → **$0.04-0.12**
   - Total per campaign: $0.75-0.85 → **$0.62-0.70**

9. **Infrastructure Costs** (lines 2476-2495)
   - Added "Development Environment" section ($0/month)
   - Updated API costs with Gemini pricing
   - 100 campaigns: $187 → **$172/month**
   - 1000 campaigns: $952 → **$802/month**

10. **Implementation Flow** (line 1514)
    - Updated to "Call Gemini 2.5 Flash API"

11. **Phase 1 Deliverables** (lines 2311, 2317)
    - Tech setup mentions Gemini integration
    - Deliverables mention Gemini images

12. **Document Version** (bottom)
    - Updated to v1.1 with changelog

---

## Benefits Summary

### Cost Savings
- **~15% cheaper** per campaign ($0.13 savings per campaign)
- At 1000 campaigns/month: **$150/month savings** ($1,800/year)
- Zero infrastructure costs during development

### Development Experience
- **No AWS account needed** for development
- **Faster iteration** - no network latency for files
- **Easier onboarding** - just Docker Compose
- **Simpler debugging** - everything local

### Production
- **Same infrastructure** as before (AWS RDS + S3)
- **No code changes** needed for deployment
- **Better API integration** - single Gemini API vs multiple Google services

---

## Migration Path

### For Existing Development
If you've already started:
1. Install new dependency: `pip install google-generativeai==0.3.0`
2. Remove old: `pip uninstall google-cloud-aiplatform`
3. Update imports in Content Agent
4. Add `GOOGLE_API_KEY` to `.env`
5. Add storage abstraction layer code

### For New Development
Start fresh with local setup:
1. Run `docker-compose up` (Postgres + Redis)
2. Set `STORAGE_TYPE=local` in `.env`
3. Set `LOCAL_STORAGE_PATH=./storage`
4. No AWS setup needed!

### For Production Deployment
When ready to deploy:
1. Set up AWS RDS + S3
2. Update `.env.production` with AWS credentials
3. Set `STORAGE_TYPE=s3`
4. Deploy - code works unchanged!

---

## Next Steps

1. ✅ Review this update summary
2. ⏭️ Update any existing code to use Gemini 2.5 Flash
3. ⏭️ Implement storage abstraction layer
4. ⏭️ Test locally with filesystem storage
5. ⏭️ Proceed with Phase 1 development


# Multi-Agent Marketing System
## Childrenswear Category Page Content Generation Platform

---

## Executive Summary

An intelligent multi-agent system designed to automate the creation of comprehensive marketing campaigns for category pages in an online childrenswear retail business. The system uses specialized AI agents coordinated by an orchestrator to produce research-backed content, social media posts, performance marketing plans, CRM campaigns with HTML emails, and post-launch analytics.

**Target Users:** Marketing team members who manage category pages and campaigns

**Input:** Category URL from existing website

**Output:** Complete marketing campaign package including content, images, social posts, PPC plans, and email HTML

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Technical Architecture](#technical-architecture)
3. [Agent Specifications](#agent-specifications)
4. [Implementation Flow](#implementation-flow)
5. [Tech Stack](#tech-stack)
6. [Frontend Interface](#frontend-interface)
7. [Data Flow](#data-flow)
8. [Implementation Phases](#implementation-phases)
9. [Cost & Performance Estimates](#cost--performance-estimates)

---

## System Overview

### Business Context

The system serves an online childrenswear retailer (baby to 16 years old) that creates sophisticated category pages combining:
- Product listings
- Expert advice and helpful content
- Feature callouts (e.g., "temperature-regulating fabric", "easy nappy change design")
- Educational content for parents
- SEO-optimized copy

### Core Problem Being Solved

Creating comprehensive, research-backed marketing campaigns for category pages is time-consuming and requires coordination across multiple disciplines (content, social media, PPC, CRM, analytics). This system automates 80% of this work while maintaining quality and consistency.

### Key Differentiators

1. **Research-First Approach:** Deep analysis of existing products and parent needs before content creation
2. **Multi-Channel Output:** Single input generates assets for web, social, ads, and email
3. **HTML Email Generation:** Produces production-ready, responsive email HTML
4. **Post-Launch Learning:** Analyst agent provides optimization recommendations based on real performance data

---

## Technical Architecture

### High-Level Architecture

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                   React Frontend                        â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚  Input Form | Progress Dashboard | Review Screens â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                         â”‚ HTTP/WebSocket
                         â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                   Python Backend                        â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚              FastAPI Application                   â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚            LangGraph Orchestration                 â”‚  â”‚
â”‚  â”‚                                                     â”‚  â”‚
â”‚  â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚  â”‚
â”‚  â”‚  â”‚         Overlord Agent                       â”‚ â”‚  â”‚
â”‚  â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚  â”‚
â”‚  â”‚                     â”‚                              â”‚  â”‚
â”‚  â”‚     â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”         â”‚  â”‚
â”‚  â”‚     â†“               â†“                   â†“         â”‚  â”‚
â”‚  â”‚  Research      Content Agent       Social        â”‚  â”‚
â”‚  â”‚  Agent         (+ Imagen 3)        Media         â”‚  â”‚
â”‚  â”‚                                                    â”‚  â”‚
â”‚  â”‚     â†“               â†“                   â†“         â”‚  â”‚
â”‚  â”‚  Performance    CRM Agent          Analyst       â”‚  â”‚
â”‚  â”‚  Marketing      (HTML emails)      Agent         â”‚  â”‚
â”‚  â”‚  Agent                              (post-launch) â”‚  â”‚
â”‚  â”‚                                                    â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                         â”‚
                         â†“
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              External Services & Storage                â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â” â”‚
â”‚  â”‚ Claude  â”‚  â”‚ Google   â”‚  â”‚ Redis   â”‚  â”‚ Postgres â”‚ â”‚
â”‚  â”‚ API     â”‚  â”‚ Imagen 3 â”‚  â”‚ Queue   â”‚  â”‚ Database â”‚ â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜ â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### State Management

Using LangGraph's StateGraph for agent coordination:

```python
from typing import TypedDict, Dict, List, Optional

class MarketingCampaignState(TypedDict):
    # Input
    category_url: str
    category_name: str
    user_inputs: Dict  # budget, launch_date, etc.
    
    # Research Phase
    research_data: Dict  # products, features, parent_questions
    
    # Content Phase
    content_outputs: Dict  # hero, features, seo, image_prompts
    generated_images: List[str]  # URLs to generated images
    
    # Marketing Channels
    social_media_plan: Dict  # 3-5 key posts
    ppc_campaign: Dict  # keywords, ad copy, budget plan
    crm_plan: Dict  # emails with HTML
    
    # Post-Launch
    analyst_insights: Optional[Dict]  # only when BI report uploaded
    
    # System
    final_campaign: Dict  # consolidated output
    errors: List[str]
    current_step: str
    progress_percentage: int
```

---

## Agent Specifications

### 1. Overlord Agent (Orchestrator)

**Role:** Master coordinator that manages the entire workflow

**Responsibilities:**
- Receives category URL and user inputs from frontend
- Validates inputs and initializes campaign state
- Creates execution plan and determines agent sequence
- Routes information between agents
- Handles errors and retry logic
- Consolidates all outputs into final deliverable
- Reports progress to frontend via WebSocket

**Tools:**
- None (uses LangGraph's built-in orchestration)

**Input:**
```python
{
    "category_url": "https://yourstore.com/baby-sleepsuits",
    "budget": 5000,  # optional
    "launch_date": "2025-12-01"  # optional
}
```

**Output:**
```python
{
    "campaign_id": "uuid",
    "status": "completed",
    "agents_executed": ["research", "content", "social", "ppc", "crm"],
    "execution_time": "4m 32s",
    "final_package": { ... }
}
```

**Decision Logic:**
- Always runs Research Agent first
- Runs Content, Social Media, Performance Marketing, CRM in parallel after Research completes
- Analyst Agent only runs when user uploads BI report post-launch
- If any agent fails, logs error and continues with others (graceful degradation)

---

### 2. Research Agent

**Role:** Deep researcher gathering product intelligence and parent insights

**Responsibilities:**
1. **Scrape & analyze category page:**
   - Extract all products in category
   - Parse product details (materials, features, prices, sizes)
   - Identify common attributes and unique selling points
   - Generate product feature matrix

2. **Search parent questions:**
   - Research common questions about this product category
   - Check forums (Mumsnet, Reddit r/parenting, What to Expect)
   - Identify pain points and concerns
   - Find trending topics and seasonal considerations

3. **Competitor analysis:**
   - Search for similar category pages from competitors
   - Identify content gaps and opportunities
   - Note effective messaging and positioning

4. **SEO research:**
   - Identify primary and secondary keywords
   - Search intent analysis
   - Related search queries

**Tools:**
- `web_fetch` - scrape category page HTML
- `web_search` - search for parent questions and competitor pages
- BeautifulSoup4 - parse HTML and extract product data
- Custom product parser - structure product information

**LLM Configuration:**
- Model: Claude Sonnet 4.5
- Temperature: 0.3 (factual, consistent)
- Max tokens: 4000

**Output Structure:**
```python
{
    "products": [
        {
            "name": "Organic Cotton Sleepsuit",
            "price": 12.99,
            "sizes": ["0-3m", "3-6m", "6-9m"],
            "materials": ["100% organic cotton"],
            "key_features": ["temperature regulating", "zip closure", "soft seams"],
            "url": "..."
        }
    ],
    "category_insights": {
        "total_products": 45,
        "price_range": {"min": 8.99, "max": 24.99, "avg": 14.50},
        "common_features": [
            "Temperature regulation (67% of products)",
            "Easy nappy change design (54% of products)",
            "Soft seam construction (89% of products)"
        ],
        "unique_selling_points": [
            "Organic cotton options",
            "Wide size range (premature to 24 months)",
            "Award-winning designs"
        ]
    },
    "parent_questions": [
        {
            "question": "How do I know what TOG rating my baby needs?",
            "frequency": "very common",
            "source": "multiple parenting forums"
        },
        {
            "question": "Should sleepsuits have feet or be footless?",
            "frequency": "common",
            "source": "Mumsnet, Reddit"
        }
    ],
    "competitor_insights": {
        "effective_messaging": [
            "Safety certifications prominently displayed",
            "Size guides with age ranges",
            "Fabric care instructions upfront"
        ],
        "content_gaps": [
            "Limited information on seasonal guidance",
            "No comparison tools"
        ]
    },
    "seo_keywords": {
        "primary": ["baby sleepsuits", "infant sleepsuits"],
        "secondary": ["organic baby sleepsuit", "newborn sleepsuit", "zip baby sleepsuit"],
        "long_tail": ["best baby sleepsuit for summer", "how to choose baby sleepsuit size"]
    }
}
```

**Execution Time:** ~2-3 minutes

---

### 3. Content Agent

**Role:** Creates all written content and image generation prompts

**Responsibilities:**
1. Generate hero section content (headline, subheadline, CTA)
2. Create 3-5 key feature callouts with benefit-focused copy
3. Write category description (SEO-optimized, 2-3 paragraphs)
4. Generate image prompts for Google Imagen 3
5. Create SEO meta title and description
6. Generate alt text for all images

**Tools:**
- `imagen_generate` - Google Imagen 3 via Vertex AI
- SEO optimization knowledge

**LLM Configuration:**
- Model: Claude Sonnet 4.5
- Temperature: 0.7 (creative but controlled)
- Max tokens: 3000

**Input:**
- Complete research_data from Research Agent

**Output Structure:**
```python
{
    "hero_section": {
        "headline": "Sleep Easy with Our Award-Winning Baby Sleepsuits",
        "subheadline": "Temperature-regulating designs that keep your baby comfortable all night long",
        "cta_text": "Shop the Collection",
        "image_prompt": "A peaceful sleeping newborn baby wearing a soft white organic cotton sleepsuit, lying in a natural-lit nursery with soft neutral tones, close-up shot showing the gentle fabric texture and comfortable fit, professional product photography style, warm and calming atmosphere",
        "generated_image_url": "gs://bucket/hero-image.jpg"
    },
    "key_features": [
        {
            "title": "Temperature Regulation",
            "description": "Our breathable fabrics help regulate your baby's temperature throughout the night, reducing the risk of overheating. Perfect for any season.",
            "benefit": "Better sleep for baby, peace of mind for you",
            "icon_prompt": "Simple line icon of a thermometer with a comfortable temperature indicator, minimal design suitable for web",
            "image_prompt": "Close-up macro photography of premium baby sleepsuit fabric showing breathable weave texture, soft focus with natural lighting, professional textile photography",
            "generated_icon_url": "gs://bucket/temp-icon.jpg",
            "generated_image_url": "gs://bucket/temp-feature.jpg"
        },
        {
            "title": "Easy Nappy Changes",
            "description": "Strategic zip placement means you can change nappies quickly without fully undressing your baby - keeping them cozy and settled.",
            "benefit": "Faster changes, less disruption to sleep",
            "icon_prompt": "Simple line icon of a zipper, minimal clean design",
            "image_prompt": "Detail shot of baby sleepsuit showing easy-access zip design, hands gently opening the zipper, soft natural lighting, lifestyle photography style showing the practical benefit",
            "generated_icon_url": "gs://bucket/zip-icon.jpg",
            "generated_image_url": "gs://bucket/zip-feature.jpg"
        }
    ],
    "category_description": {
        "paragraph_1": "Finding the perfect baby sleepsuit is about more than just cute designs. Our carefully curated collection features sleepsuits that combine comfort, safety, and practicality - because we know what matters most to parents. From organic cotton options to innovative temperature-regulating fabrics, each sleepsuit is chosen with your baby's wellbeing in mind.",
        "paragraph_2": "Whether you're preparing for your first baby or stocking up for your growing little one, our range covers premature sizes through to 24 months. Every sleepsuit features thoughtful design elements like soft seams to prevent irritation, secure fastenings for safety, and easy-care fabrics that stand up to frequent washing.",
        "paragraph_3": "Many of our sleepsuits have earned awards and recognition from parenting experts, and thousands of parents trust us to keep their babies comfortable night after night. Browse our collection to find the perfect sleepsuit for your little one."
    },
    "seo_meta": {
        "title": "Baby Sleepsuits | Organic & Temperature-Regulating Designs | YourStore",
        "description": "Shop our award-winning baby sleepsuits with temperature-regulating fabrics and easy-change designs. Sizes premature to 24 months. Free UK delivery over Â£30.",
        "keywords": "baby sleepsuits, infant sleepsuits, organic baby sleepsuit, newborn sleepsuit"
    },
    "image_alt_texts": {
        "hero": "Peaceful newborn baby sleeping in white organic cotton sleepsuit",
        "feature_1": "Close-up of breathable baby sleepsuit fabric texture",
        "feature_2": "Baby sleepsuit showing easy-access zip design for nappy changes"
    }
}
```

**Image Generation Details:**
- Uses Google Imagen 3 via Vertex AI
- Generates 1 hero image + 2-5 feature images
- Style: Professional, clean, parent-friendly
- Aspect ratios: Hero (16:9), Features (4:3 or 1:1)
- Resolution: High (1024x1024 minimum)

**Execution Time:** ~3-4 minutes (including image generation)

---

### 4. Social Media Agent

**Role:** Creates 3-5 high-impact social media posts

**Responsibilities:**
1. Analyze content for social-worthy angles
2. Select best platforms for each post
3. Write platform-optimized copy
4. Recommend post formats (carousel, single, reel, story)
5. Generate strategic hashtags
6. Provide posting time recommendations
7. Create image/video briefs

**Tools:**
- None (uses Claude's knowledge of social media best practices)

**LLM Configuration:**
- Model: Claude Sonnet 4.5
- Temperature: 0.8 (creative)
- Max tokens: 2500

**Input:**
- content_outputs from Content Agent
- research_data from Research Agent (for parent questions)

**Output Structure:**
```python
{
    "social_posts": [
        {
            "post_id": 1,
            "platform": "Instagram",
            "post_type": "Carousel (5 slides)",
            "objective": "Education + Product awareness",
            "target_audience": "New and expecting parents",
            "hook": "5 things every new parent should know about baby sleepsuits ðŸ‘¶",
            "slides": [
                {
                    "slide_number": 1,
                    "content": "Temperature Regulation = Better Sleep",
                    "description": "Did you know overheating is a risk factor for SIDS? Our sleepsuits use breathable fabrics that help regulate temperature naturally.",
                    "visual_brief": "Close-up of baby sleeping peacefully with text overlay"
                },
                {
                    "slide_number": 2,
                    "content": "Easy Nappy Changes Save Sanity",
                    "description": "Strategic zip placement means less fuss during 3am changes. Keep baby cozy and settled.",
                    "visual_brief": "Hands demonstrating easy zip access"
                }
            ],
            "caption": "Shopping for baby sleepsuits? Here's what actually matters (beyond cute prints!)\n\nSwipe to learn what parents wish they knew before buying â†’\n\nWhich feature surprises you most? Comment below! ðŸ’¬",
            "hashtags": [
                "#newparent",
                "#babysleep",
                "#parentingtips",
                "#newbornessentials",
                "#babyclothes",
                "#mumtobe",
                "#parenthood",
                "#babyshopping"
            ],
            "cta": "Shop our expert-approved collection (link in bio)",
            "best_posting_time": "Tuesday 7-9pm (highest engagement for parent audience)",
            "estimated_reach": "Medium-High (educational content performs well)"
        },
        {
            "post_id": 2,
            "platform": "Facebook",
            "post_type": "Single image with link",
            "objective": "Drive traffic + conversions",
            "target_audience": "Parents actively shopping",
            "headline": "The Baby Sleepsuit Collection Parents Are Raving About â­",
            "body": "\"Game-changer for bedtime!\" - Sarah, mum of 2\n\nOur customers love:\nâœ“ Temperature-regulating fabrics\nâœ“ Award-winning designs\nâœ“ Easy care (because who has time for hand-washing?)\nâœ“ Sizes from premature to 24 months\n\nSee why 1000s of parents choose us for better baby sleep ðŸ‘‰",
            "image_brief": "Collage of 3-4 sleepsuits in different colors/styles with customer review quote overlay",
            "link_text": "Shop Now - Free UK Delivery Over Â£30",
            "hashtags": ["#babysleepsuits", "#newparent", "#babyshopping"],
            "best_posting_time": "Wednesday 8-10am (commute/coffee time)",
            "estimated_reach": "High (promotional content with social proof)"
        },
        {
            "post_id": 3,
            "platform": "Pinterest",
            "post_type": "Vertical pin",
            "objective": "SEO + long-term discovery",
            "target_audience": "Parents planning and researching",
            "pin_title": "Baby Sleepsuit Buying Guide: What New Parents Need to Know",
            "pin_description": "Choosing the right baby sleepsuit can feel overwhelming! Here's what actually matters: temperature regulation, easy nappy access, soft seams, and the right size. Our expert-approved collection takes the guesswork out of baby sleep.",
            "image_brief": "Vertical infographic (2:3 ratio) with key buying tips, feature icons, and product images. Pinterest-optimized with readable text and brand colors",
            "link_destination": "Category landing page",
            "board_suggestions": ["Baby Essentials", "Newborn Must-Haves", "Baby Sleep Tips"],
            "hashtags": ["#babysleepsuit", "#newbornessentials", "#babylayering"],
            "best_posting_time": "Anytime (Pinterest is search-based)",
            "estimated_reach": "Very High (evergreen content with search potential)"
        }
    ],
    "posting_strategy": {
        "launch_week": "Post 1 (Instagram) on Tuesday, Post 2 (Facebook) on Wednesday, Post 3 (Pinterest) immediately",
        "frequency": "3 posts across 3 platforms for category launch, then monitor engagement",
        "repurposing": "Carousel content can be broken into individual stories, Pinterest pin drives long-term traffic"
    }
}
```

**Execution Time:** ~1-2 minutes

---

### 5. Performance Marketing Agent

**Role:** Creates Google Ads campaign plan (manual upload, no API)

**Responsibilities:**
1. Keyword research and grouping
2. CPC estimates from industry knowledge
3. Campaign structure design
4. Ad copy creation (RSA format)
5. Budget allocation recommendations
6. Landing page optimization checklist
7. Conversion tracking setup guide

**Tools:**
- None (uses Claude's marketing knowledge and provided research data)

**LLM Configuration:**
- Model: Claude Sonnet 4.5
- Temperature: 0.4 (structured, strategic)
- Max tokens: 3500

**Input:**
- research_data (for keywords)
- content_outputs (for ad copy inspiration)
- user_inputs (budget if provided)

**Output Structure:**
```python
{
    "campaign_overview": {
        "campaign_name": "Baby Sleepsuits - Category Launch",
        "campaign_type": "Search",
        "daily_budget": 50,  # Â£
        "estimated_daily_clicks": 25,
        "estimated_cpc": 2.00,
        "target_cpa": 15.00,
        "expected_conversions_per_day": 3.3
    },
    "campaign_structure": {
        "ad_group_1": {
            "name": "Baby Sleepsuits - Generic",
            "budget_allocation": "40%",
            "keywords": [
                {"keyword": "baby sleepsuits", "match_type": "phrase", "estimated_cpc": 2.10, "search_volume": "high"},
                {"keyword": "infant sleepsuits", "match_type": "phrase", "estimated_cpc": 1.90, "search_volume": "medium"},
                {"keyword": "newborn sleepsuits", "match_type": "phrase", "estimated_cpc": 2.20, "search_volume": "high"},
                {"keyword": "[baby sleepsuit]", "match_type": "exact", "estimated_cpc": 2.50, "search_volume": "high"}
            ],
            "negative_keywords": ["free", "pattern", "diy", "second hand", "used"],
            "ad_copy": {
                "headlines": [
                    "Baby Sleepsuits from Â£8.99",
                    "Award-Winning Sleepsuit Range",
                    "Free UK Delivery Over Â£30",
                    "Temperature-Regulating Fabric",
                    "Sizes Premature to 24 Months",
                    "Easy Nappy Change Design",
                    "Organic Cotton Options",
                    "Trusted by 1000s of Parents",
                    "Shop Baby Sleepsuits Now",
                    "Breathable & Comfortable",
                    "Safe Sleep for Your Baby",
                    "Quality Baby Sleepwear",
                    "Free Returns & Exchanges",
                    "Expert-Approved Designs",
                    "Soft Seam Construction"
                ],
                "descriptions": [
                    "Shop our collection of award-winning baby sleepsuits. Temperature-regulating fabrics for safe, comfortable sleep. Free UK delivery over Â£30.",
                    "From organic cotton to innovative designs, find the perfect sleepsuit for your baby. Easy care, soft seams, trusted by parents.",
                    "Browse sleepsuits from premature to 24 months. Easy nappy change zips, breathable fabrics, and quality you can trust.",
                    "Expert-approved baby sleepsuits designed for comfort and safety. Shop now for free delivery and hassle-free returns."
                ],
                "path_1": "Sleepsuits",
                "path_2": "Baby"
            }
        },
        "ad_group_2": {
            "name": "Baby Sleepsuits - Feature Specific",
            "budget_allocation": "35%",
            "keywords": [
                {"keyword": "organic baby sleepsuit", "match_type": "phrase", "estimated_cpc": 2.30, "search_volume": "medium"},
                {"keyword": "zip baby sleepsuit", "match_type": "phrase", "estimated_cpc": 1.80, "search_volume": "low-medium"},
                {"keyword": "temperature regulating baby clothes", "match_type": "phrase", "estimated_cpc": 2.60, "search_volume": "low"}
            ],
            "ad_copy": {
                "headlines": [
                    "Organic Cotton Sleepsuits",
                    "Temperature-Regulating Design",
                    "Easy Zip Access for Changes",
                    "Breathable Baby Sleepsuits",
                    "Eco-Friendly Baby Sleepwear",
                    "Premium Quality Sleepsuits",
                    "Gentle on Sensitive Skin",
                    "Certified Organic Cotton",
                    "Safe & Comfortable Sleep",
                    "Shop Organic Baby Range",
                    "From Â£12.99",
                    "Award-Winning Designs",
                    "Free UK Delivery Over Â£30",
                    "Sustainable Baby Clothes",
                    "Soft & Breathable Fabric"
                ],
                "descriptions": [
                    "100% organic cotton sleepsuits that are gentle on baby's skin. Temperature-regulating & breathable for safe sleep. Shop now.",
                    "Discover our eco-friendly sleepsuit collection. Easy-access zips, soft seams, and sustainable materials. Free delivery over Â£30.",
                    "Premium organic baby sleepsuits designed for comfort. Breathable fabrics help regulate temperature naturally.",
                    "Shop certified organic sleepsuits. Features parents love: easy zips, soft construction, temperature control."
                ]
            }
        },
        "ad_group_3": {
            "name": "Baby Sleepsuits - Problem Solving",
            "budget_allocation": "25%",
            "keywords": [
                {"keyword": "best baby sleepsuit", "match_type": "phrase", "estimated_cpc": 2.40, "search_volume": "medium"},
                {"keyword": "comfortable baby sleepsuit", "match_type": "phrase", "estimated_cpc": 1.70, "search_volume": "low"},
                {"keyword": "baby sleepsuit tog rating", "match_type": "phrase", "estimated_cpc": 1.60, "search_volume": "low"},
                {"keyword": "how to choose baby sleepsuit", "match_type": "phrase", "estimated_cpc": 1.50, "search_volume": "low"}
            ],
            "ad_copy": {
                "headlines": [
                    "Find the Perfect Sleepsuit",
                    "Expert-Approved Baby Sleep",
                    "Comfortable All Night Long",
                    "Temperature Control Built-In",
                    "Award-Winning Designs",
                    "Trusted by Parenting Experts",
                    "Easy Size Guide Included",
                    "Free Returns & Exchanges",
                    "Quality You Can Trust",
                    "Shop with Confidence",
                    "Better Sleep for Baby",
                    "From Â£8.99",
                    "1000s of 5-Star Reviews",
                    "Help Your Baby Sleep Well",
                    "Safe & Comfortable Choice"
                ],
                "descriptions": [
                    "Struggling to choose the right sleepsuit? Our expert-approved range makes it easy. Temperature control, easy changes, sizes premature-24m.",
                    "Find sleepsuits parents love. Features that matter: breathable fabrics, easy zips, soft seams. Free size guide & advice included.",
                    "Shop award-winning baby sleepsuits designed for comfort and safe sleep. Helpful size guides and free delivery over Â£30.",
                    "Not sure what to look for? Our collection features the must-have elements for comfortable, safe baby sleep. Shop now."
                ]
            }
        }
    },
    "budget_breakdown": {
        "total_monthly_budget": 1500,
        "daily_budget": 50,
        "ad_group_allocations": {
            "Generic": 20,  # Â£ per day
            "Feature Specific": 17.50,
            "Problem Solving": 12.50
        },
        "estimated_performance": {
            "monthly_clicks": 750,
            "monthly_conversions": 100,
            "cost_per_conversion": 15.00,
            "expected_revenue": 3250  # assuming Â£32.50 AOV
        }
    },
    "landing_page_checklist": [
        "âœ“ Hero image with clear value proposition",
        "âœ“ Key features prominently displayed above fold",
        "âœ“ Size guide easily accessible",
        "âœ“ Customer reviews visible",
        "âœ“ Trust signals (awards, certifications)",
        "âœ“ Clear CTAs throughout page",
        "âœ“ Mobile-optimized design",
        "âœ“ Fast page load speed (<3 seconds)",
        "âœ“ Breadcrumb navigation",
        "âœ“ Filter options for products"
    ],
    "tracking_setup": {
        "conversion_actions": [
            {
                "name": "Purchase - Baby Sleepsuits",
                "type": "Purchase",
                "value": "transaction_value",
                "counting": "every"
            },
            {
                "name": "Add to Cart - Baby Sleepsuits",
                "type": "Add to Cart",
                "value": "0",
                "counting": "one"
            }
        ],
        "url_parameters": "?utm_source=google&utm_medium=cpc&utm_campaign=baby_sleepsuits",
        "remarketing_tag": "Required on category page and thank you page"
    },
    "implementation_steps": [
        "1. Copy campaign structure to Google Ads",
        "2. Upload keyword list (CSV provided)",
        "3. Set up ad groups with budget allocations",
        "4. Create Responsive Search Ads using provided headlines/descriptions",
        "5. Add negative keywords to each ad group",
        "6. Set up conversion tracking",
        "7. Add URL parameters to destination URLs",
        "8. Set campaign to 'Paused' for review",
        "9. Launch when category page is live"
    ],
    "export_files": {
        "keywords_csv": "baby_sleepsuits_keywords.csv",
        "ad_copy_csv": "baby_sleepsuits_ads.csv",
        "campaign_structure_xlsx": "baby_sleepsuits_campaign_structure.xlsx"
    }
}
```

**Export Format:**
- CSV for keyword import
- CSV for ad copy import
- Excel file with complete campaign structure
- PDF with setup instructions

**Execution Time:** ~2-3 minutes

---

### 6. CRM Agent

**Role:** Creates email campaigns with production-ready HTML

**Responsibilities:**
1. Design broadcast email sequence (3-4 emails)
2. Design automation triggers (3-5)
3. Generate responsive HTML using MJML
4. Create plain text versions
5. Include personalization merge tags
6. Add tracking parameters
7. Provide send time recommendations
8. Create segment targeting suggestions

**Tools:**
- `mjml` Python library - for responsive email HTML generation
- Email best practices knowledge

**LLM Configuration:**
- Model: Claude Sonnet 4.5
- Temperature: 0.6 (creative but structured)
- Max tokens: 4000

**Input:**
- content_outputs (for email content)
- research_data (for parent insights)

**MJML Framework:**
```xml
<mjml>
  <mj-head>
    <mj-attributes>
      <mj-all font-family="Arial, sans-serif" />
      <mj-text font-size="14px" color="#333333" line-height="20px" />
      <mj-button background-color="#FF6B6B" color="#ffffff" />
    </mj-attributes>
  </mj-head>
  <mj-body background-color="#f4f4f4">
    <!-- Email content here -->
  </mj-body>
</mjml>
```

**Output Structure:**
```python
{
    "broadcast_campaigns": [
        {
            "sequence_position": 1,
            "email_name": "Category Launch Announcement",
            "send_timing": "Day 0 - Launch day, 10am",
            "subject_line": "Introducing Our New Baby Sleepsuit Collection ðŸ‘¶",
            "preview_text": "Temperature-regulating designs that parents are loving",
            "from_name": "Your Store Name",
            "from_email": "hello@yourstore.com",
            "reply_to": "customercare@yourstore.com",
            "target_segment": {
                "description": "All subscribers with babies 0-12 months OR pregnant",
                "estimated_size": "~15,000 contacts"
            },
            "personalization": {
                "merge_tags": ["{{first_name}}", "{{baby_age_months}}"],
                "dynamic_content": "Show different products based on baby age"
            },
            "mjml_code": """
<mjml>
  <mj-head>
    <mj-title>New Baby Sleepsuit Collection</mj-title>
    <mj-preview>Temperature-regulating designs that parents are loving</mj-preview>
    <mj-attributes>
      <mj-all font-family="'Helvetica Neue', Helvetica, Arial, sans-serif"/>
      <mj-text font-size="16px" color="#333333" line-height="24px"/>
      <mj-button background-color="#4A90E2" border-radius="4px" font-size="16px" font-weight="bold"/>
    </mj-attributes>
  </mj-head>
  
  <mj-body background-color="#F5F5F5">
    <!-- Header -->
    <mj-section background-color="#ffffff" padding="20px">
      <mj-column>
        <mj-image src="{{logo_url}}" alt="Your Store" width="150px" align="center"/>
      </mj-column>
    </mj-section>
    
    <!-- Hero Section -->
    <mj-section background-color="#ffffff" padding="0px">
      <mj-column>
        <mj-image src="{{hero_image_url}}" alt="Baby Sleepsuit Collection" fluid-on-mobile="true"/>
      </mj-column>
    </mj-section>
    
    <!-- Main Content -->
    <mj-section background-color="#ffffff" padding="40px 25px">
      <mj-column>
        <mj-text align="center" font-size="28px" font-weight="bold" color="#2C3E50" padding="0 0 20px 0">
          Sleep Easy, {{first_name}}
        </mj-text>
        
        <mj-text align="center" font-size="18px" color="#555555" padding="0 0 30px 0">
          Introducing our award-winning sleepsuit collection designed for better baby sleep
        </mj-text>
        
        <mj-button href="{{category_url}}?utm_source=email&utm_campaign=sleepsuit_launch" align="center">
          Shop the Collection
        </mj-button>
      </mj-column>
    </mj-section>
    
    <!-- Features Section -->
    <mj-section background-color="#F9F9F9" padding="40px 25px">
      <mj-column>
        <mj-text align="center" font-size="22px" font-weight="bold" color="#2C3E50" padding="0 0 30px 0">
          Why Parents Love These Sleepsuits
        </mj-text>
      </mj-column>
    </mj-section>
    
    <!-- Feature 1 -->
    <mj-section background-color="#F9F9F9" padding="0px 25px 30px 25px">
      <mj-column width="30%">
        <mj-image src="{{feature_1_icon_url}}" width="80px" align="center"/>
      </mj-column>
      <mj-column width="70%">
        <mj-text font-size="18px" font-weight="bold" color="#2C3E50" padding="0 0 10px 0">
          Temperature Regulation
        </mj-text>
        <mj-text font-size="14px" color="#555555">
          Breathable fabrics help regulate your baby's temperature throughout the night, reducing overheating risk.
        </mj-text>
      </mj-column>
    </mj-section>
    
    <!-- Feature 2 -->
    <mj-section background-color="#F9F9F9" padding="0px 25px 30px 25px">
      <mj-column width="30%">
        <mj-image src="{{feature_2_icon_url}}" width="80px" align="center"/>
      </mj-column>
      <mj-column width="70%">
        <mj-text font-size="18px" font-weight="bold" color="#2C3E50" padding="0 0 10px 0">
          Easy Nappy Changes
        </mj-text>
        <mj-text font-size="14px" color="#555555">
          Strategic zip placement for quick changes without fully undressing - keeping baby cozy and settled.
        </mj-text>
      </mj-column>
    </mj-section>
    
    <!-- Feature 3 -->
    <mj-section background-color="#F9F9F9" padding="0px 25px 40px 25px">
      <mj-column width="30%">
        <mj-image src="{{feature_3_icon_url}}" width="80px" align="center"/>
      </mj-column>
      <mj-column width="70%">
        <mj-text font-size="18px" font-weight="bold" color="#2C3E50" padding="0 0 10px 0">
          Soft Seam Construction
        </mj-text>
        <mj-text font-size="14px" color="#555555">
          Gentle on delicate skin with carefully positioned seams that prevent irritation and rubbing.
        </mj-text>
      </mj-column>
    </mj-section>
    
    <!-- CTA Section -->
    <mj-section background-color="#ffffff" padding="40px 25px">
      <mj-column>
        <mj-text align="center" font-size="20px" color="#333333" padding="0 0 20px 0">
          From Â£8.99 | Free UK Delivery Over Â£30
        </mj-text>
        <mj-button href="{{category_url}}?utm_source=email&utm_campaign=sleepsuit_launch" align="center">
          Start Shopping
        </mj-button>
      </mj-column>
    </mj-section>
    
    <!-- Footer -->
    <mj-section background-color="#2C3E50" padding="30px 25px">
      <mj-column>
        <mj-text align="center" color="#ffffff" font-size="12px">
          You're receiving this email because you subscribed to our newsletter.
        </mj-text>
        <mj-text align="center" color="#ffffff" font-size="12px">
          <a href="{{unsubscribe_url}}" style="color: #4A90E2; text-decoration: none;">Unsubscribe</a> | 
          <a href="{{preferences_url}}" style="color: #4A90E2; text-decoration: none;">Update Preferences</a>
        </mj-text>
        <mj-social mode="horizontal" align="center" icon-size="30px" padding="20px 0 0 0">
          <mj-social-element name="facebook" href="{{facebook_url}}"/>
          <mj-social-element name="instagram" href="{{instagram_url}}"/>
          <mj-social-element name="pinterest" href="{{pinterest_url}}"/>
        </mj-social>
      </mj-column>
    </mj-section>
  </mj-body>
</mjml>
            """,
            "html_compiled": "<!-- Full compiled HTML with inline CSS -->",
            "plain_text": """
Hi {{first_name}},

Sleep Easy - Our New Baby Sleepsuit Collection

We're excited to introduce our award-winning sleepsuit collection designed for better baby sleep.

Why Parents Love These Sleepsuits:

â­ Temperature Regulation
Breathable fabrics help regulate your baby's temperature throughout the night, reducing overheating risk.

â­ Easy Nappy Changes
Strategic zip placement for quick changes without fully undressing - keeping baby cozy and settled.

â­ Soft Seam Construction
Gentle on delicate skin with carefully positioned seams that prevent irritation and rubbing.

From Â£8.99 | Free UK Delivery Over Â£30

Shop now: {{category_url}}?utm_source=email&utm_campaign=sleepsuit_launch

---
Unsubscribe: {{unsubscribe_url}}
Update Preferences: {{preferences_url}}
            """,
            "design_notes": [
                "Mobile-optimized with single column layout",
                "Hero image should be high quality lifestyle shot",
                "Feature icons should be simple line illustrations",
                "CTA buttons use primary brand color",
                "All images have alt text for accessibility"
            ],
            "a_b_test_suggestions": [
                "Subject line: test emoji vs no emoji",
                "CTA text: 'Shop Now' vs 'Browse Collection' vs 'See Sleepsuits'",
                "Hero image: baby sleeping vs product flat lay"
            ]
        },
        {
            "sequence_position": 2,
            "email_name": "Feature Spotlight - Temperature Regulation",
            "send_timing": "Day 3 - 3 days after launch",
            "subject_line": "The #1 thing parents worry about at bedtime",
            "preview_text": "How our sleepsuits help regulate baby's temperature",
            # ... similar structure ...
        },
        {
            "sequence_position": 3,
            "email_name": "Social Proof & Reviews",
            "send_timing": "Day 7 - One week after launch",
            "subject_line": "What parents are saying about our sleepsuits â­â­â­â­â­",
            "preview_text": "Real reviews from real parents",
            # ... similar structure ...
        }
    ],
    "automation_triggers": [
        {
            "trigger_name": "Category Browse Abandonment",
            "trigger_description": "User viewed category page but didn't add to cart",
            "trigger_conditions": {
                "event": "viewed_category",
                "category": "baby-sleepsuits",
                "no_purchase": true,
                "time_delay": "2 hours"
            },
            "email": {
                "subject_line": "Still looking for the perfect sleepsuit? ðŸ‘¶",
                "preview_text": "Let us help you choose",
                "mjml_code": "<!-- Similar structure to broadcast -->",
                "html_compiled": "<!-- Compiled HTML -->",
                "plain_text": "<!-- Plain text version -->",
                "personalization": {
                    "show_recently_viewed": true,
                    "include_size_guide_link": true
                }
            },
            "performance_notes": "Expect 8-12% conversion rate on this automation"
        },
        {
            "trigger_name": "Cart Abandonment - Sleepsuit Products",
            "trigger_description": "User added sleepsuit to cart but didn't complete purchase",
            "trigger_conditions": {
                "event": "added_to_cart",
                "product_category": "baby-sleepsuits",
                "no_purchase": true,
                "time_delay": "1 hour"
            },
            "email": {
                "subject_line": "{{first_name}}, you left something behind ðŸ›’",
                "preview_text": "Complete your order - Free delivery over Â£30",
                "mjml_code": "<!-- Cart items dynamically inserted -->",
                "html_compiled": "<!-- Compiled HTML -->",
                "plain_text": "<!-- Plain text version -->",
                "personalization": {
                    "show_cart_items": true,
                    "include_discount_if_available": true,
                    "show_urgency_timer": true
                }
            },
            "performance_notes": "Expect 15-20% recovery rate"
        },
        {
            "trigger_name": "Post-Purchase Care Guide",
            "trigger_description": "Educational email sent 2 days after purchase",
            "trigger_conditions": {
                "event": "purchase_complete",
                "product_category": "baby-sleepsuits",
                "time_delay": "2 days"
            },
            "email": {
                "subject_line": "How to care for your new sleepsuit (plus sleep tips!)",
                "preview_text": "Get the most from your purchase",
                "content_focus": [
                    "Washing instructions",
                    "Storage tips",
                    "Sleep safety guidelines",
                    "When to size up",
                    "Cross-sell related products"
                ],
                "performance_notes": "Builds loyalty and reduces returns"
            }
        },
        {
            "trigger_name": "Size-Up Reminder",
            "trigger_description": "Remind parents when baby may need next size",
            "trigger_conditions": {
                "event": "purchase_complete",
                "product_category": "baby-sleepsuits",
                "purchased_size": "{{size}}",
                "time_delay": "calculate based on size (e.g., 3 months for 0-3m)"
            },
            "email": {
                "subject_line": "Time for a bigger sleepsuit? ðŸ‘¶",
                "preview_text": "Your baby is growing fast!",
                "content_focus": [
                    "Signs baby needs next size",
                    "Recommend next size up",
                    "Special offer for repeat customers",
                    "Size guide reference"
                ],
                "performance_notes": "High conversion, drives repeat purchases"
            }
        }
    ],
    "segmentation_strategy": {
        "segments": [
            {
                "name": "Expecting Parents (Due in 0-3 months)",
                "criteria": "Pregnant, due date within 3 months",
                "messaging_angle": "Preparation and essentials",
                "products_to_highlight": "Newborn and 0-3m sizes"
            },
            {
                "name": "New Parents (Baby 0-6 months)",
                "criteria": "Baby age 0-6 months",
                "messaging_angle": "Sleep problems and solutions",
                "products_to_highlight": "Full size range, focus on features"
            },
            {
                "name": "Returning Customers",
                "criteria": "Previous purchase in last 12 months",
                "messaging_angle": "New arrivals and loyalty",
                "products_to_highlight": "What's new, size-up options"
            }
        ]
    },
    "push_notification_plan": {
        "notifications": [
            {
                "name": "Launch Announcement",
                "timing": "Launch day, 11am",
                "title": "New arrivals: Baby sleepsuits ðŸ‘¶",
                "message": "Discover our award-winning collection",
                "deep_link": "app://category/baby-sleepsuits",
                "audience": "All app users with baby 0-12m"
            },
            {
                "name": "Flash Sale Reminder",
                "timing": "If running promotion",
                "title": "Last chance: 20% off sleepsuits",
                "message": "Sale ends tonight at midnight",
                "deep_link": "app://category/baby-sleepsuits?sale=true",
                "audience": "Users who viewed category in last 7 days"
            }
        ]
    },
    "export_files": {
        "email_html_files": [
            "email_1_launch.html",
            "email_2_feature_spotlight.html",
            "email_3_social_proof.html",
            "automation_browse_abandonment.html",
            "automation_cart_abandonment.html",
            "automation_post_purchase.html",
            "automation_size_up.html"
        ],
        "email_plain_text_files": [
            "email_1_launch.txt",
            # etc...
        ],
        "setup_guide": "crm_implementation_guide.pdf"
    }
}
```

**Technical Implementation:**
```python
# Convert MJML to HTML
import mjml

def compile_email(mjml_code):
    result = mjml.mjml2html(mjml_code)
    return result['html']

# Each email includes:
# 1. Responsive design (mobile-first)
# 2. Inline CSS for email client compatibility
# 3. Fallback fonts
# 4. Alt text on all images
# 5. Accessible semantic HTML
# 6. Tracking pixels and UTM parameters
# 7. Personalization merge tags
```

**Execution Time:** ~3-4 minutes

---

### 7. Analyst Agent (Post-Launch Only)

**Role:** Analyzes performance data and provides optimization recommendations

**Activation:** Only runs when user uploads BI report after category goes live

**Responsibilities:**
1. Parse uploaded BI report (CSV/Excel)
2. Compare metrics against benchmarks
3. Identify top/bottom performing content sections
4. Statistical significance testing
5. Generate specific A/B test recommendations
6. Suggest content optimizations
7. Identify product range gaps

**Tools:**
- `pandas` - data manipulation
- `scipy.stats` - statistical testing
- Report parsing utilities

**LLM Configuration:**
- Model: Claude Sonnet 4.5
- Temperature: 0.2 (analytical, precise)
- Max tokens: 3000

**Input:**
```python
# User uploads CSV/Excel with:
{
    "report_type": "category_performance",
    "date_range": "2025-11-01 to 2025-11-30",
    "metrics": {
        "sessions": 12500,
        "users": 9800,
        "pageviews": 18700,
        "bounce_rate": 41.2,  # %
        "avg_time_on_page": 128,  # seconds
        "conversion_rate": 2.6,  # %
        "transactions": 325,
        "revenue": 10562.50,
        "aov": 32.50
    },
    "section_engagement": {
        "hero_section": {"views": 12500, "clicks": 2875, "ctr": 23.0},
        "feature_1_temp_regulation": {"views": 8375, "clicks": 1005, "ctr": 12.0},
        "feature_2_easy_change": {"views": 7800, "clicks": 780, "ctr": 10.0},
        "feature_3_soft_seams": {"views": 7200, "clicks": 504, "ctr": 7.0},
        "size_guide": {"views": 5625, "clicks": 788, "ctr": 14.0},
        "customer_reviews": {"views": 6250, "clicks": 438, "ctr": 7.0}
    },
    "traffic_sources": {
        "organic": 4500,
        "paid_search": 3200,
        "direct": 2100,
        "email": 1800,
        "social": 900
    },
    "top_products": [
        {"name": "Organic Cotton Sleepsuit - White", "views": 450, "purchases": 45},
        {"name": "Zip Sleepsuit - Blue", "views": 380, "purchases": 32}
    ],
    "benchmark_comparison": {
        "avg_conversion_rate_other_categories": 2.3,
        "avg_bounce_rate_other_categories": 45.0,
        "avg_time_on_page_other_categories": 95
    }
}
```

**Output Structure:**
```python
{
    "analysis_date": "2025-12-01",
    "report_period": "November 2025 (30 days)",
    
    "executive_summary": {
        "overall_performance": "Strong - Outperforming category benchmarks",
        "key_wins": [
            "Conversion rate +13% above average (2.6% vs 2.3%)",
            "Time on page +35% above average (128s vs 95s)",
            "Bounce rate 8.4% better than average (41.2% vs 45%)"
        ],
        "areas_for_improvement": [
            "Feature 3 (soft seams) has lowest engagement",
            "Customer reviews section underperforming",
            "Social traffic significantly lower than other sources"
        ]
    },
    
    "statistical_analysis": {
        "conversion_rate": {
            "current": 2.6,
            "benchmark": 2.3,
            "difference": "+0.3 percentage points",
            "relative_improvement": "+13%",
            "statistical_significance": "Yes (p < 0.05)",
            "interpretation": "The improvement is statistically significant and unlikely due to chance"
        },
        "bounce_rate": {
            "current": 41.2,
            "benchmark": 45.0,
            "difference": "-3.8 percentage points",
            "relative_improvement": "-8.4%",
            "statistical_significance": "Yes (p < 0.05)",
            "interpretation": "Significantly lower bounce rate indicates better content engagement"
        },
        "time_on_page": {
            "current": 128,
            "benchmark": 95,
            "difference": "+33 seconds",
            "relative_improvement": "+35%",
            "statistical_significance": "Yes (p < 0.001)",
            "interpretation": "Users are spending much more time engaging with content"
        }
    },
    
    "content_performance": {
        "top_performing": [
            {
                "section": "Hero Section",
                "metric": "23% CTR",
                "insight": "Strong value proposition and clear CTA driving clicks",
                "action": "Maintain current approach"
            },
            {
                "section": "Size Guide",
                "metric": "14% CTR despite lower visibility",
                "insight": "High engagement suggests this is critical info for purchase decisions",
                "action": "Move higher on page or make more prominent"
            },
            {
                "section": "Temperature Regulation Feature",
                "metric": "12% CTR, 67% of visitors reached this section",
                "insight": "Most engaged-with feature content",
                "action": "Consider as hero message in future campaigns"
            }
        ],
        "underperforming": [
            {
                "section": "Soft Seams Feature",
                "metric": "7% CTR, only 58% reach this section",
                "insight": "Lowest engagement, position on page may be issue",
                "action": "Consider removing or repositioning, test different messaging"
            },
            {
                "section": "Customer Reviews",
                "metric": "7% CTR",
                "insight": "Social proof not driving expected engagement",
                "action": "Add customer photos, increase review count, or change format"
            }
        ]
    },
    
    "optimization_recommendations": [
        {
            "priority": "High",
            "recommendation": "Reorder features based on engagement",
            "rationale": "Temperature regulation (67% engagement) is currently feature #1, but size guide (14% CTR) is buried lower. Users are clearly seeking sizing info.",
            "implementation": "Move size guide higher, potentially as feature #2",
            "expected_impact": "+5-8% conversion rate improvement",
            "effort": "Low - content reordering only",
            "test_duration": "2-3 weeks"
        },
        {
            "priority": "High",
            "recommendation": "A/B test hero CTA copy",
            "rationale": "Hero has strong engagement (23% CTR) but we can optimize further",
            "implementation": {
                "variant_a": "Shop Now (current)",
                "variant_b": "Find the Right Size",
                "variant_c": "Browse Collection"
            },
            "hypothesis": "'Find the Right Size' may convert better given high size guide engagement",
            "expected_impact": "+2-4% CTR improvement",
            "effort": "Low",
            "test_duration": "1-2 weeks"
        },
        {
            "priority": "Medium",
            "recommendation": "Replace or remove Soft Seams feature",
            "rationale": "Lowest engagement (7% CTR), not differentiating enough",
            "implementation": "Test replacing with 'Award-Winning Designs' or 'Trusted by 10,000+ Parents'",
            "expected_impact": "+1-3% overall engagement",
            "effort": "Medium - requires new content and images",
            "test_duration": "2-3 weeks"
        },
        {
            "priority": "Medium",
            "recommendation": "Enhance customer reviews section",
            "rationale": "Social proof underperforming expectations",
            "implementation": [
                "Add customer photos with reviews",
                "Increase number of reviews shown from 3 to 6",
                "Add video testimonials",
                "Highlight specific benefits in review excerpts"
            ],
            "expected_impact": "+3-5% conversion rate",
            "effort": "Medium - requires review collection and formatting",
            "test_duration": "3-4 weeks"
        },
        {
            "priority": "Low",
            "recommendation": "Add product comparison tool",
            "rationale": "Multiple product views suggest users are comparing options",
            "implementation": "Create side-by-side comparison widget for similar products",
            "expected_impact": "+2-3% conversion, reduced cart abandonment",
            "effort": "High - requires development",
            "test_duration": "4-6 weeks"
        }
    ],
    
    "ab_test_ideas": [
        {
            "test_name": "Hero CTA Optimization",
            "hypothesis": "Action-oriented CTAs will outperform generic 'Shop Now'",
            "variants": [
                {"variant": "A (control)", "cta_text": "Shop Now"},
                {"variant": "B", "cta_text": "Find the Right Size"},
                {"variant": "C", "cta_text": "Browse Collection"}
            ],
            "success_metric": "Click-through rate to products",
            "minimum_sample_size": 1200,  # visitors per variant
            "estimated_test_duration": "7-10 days",
            "implementation_complexity": "Low"
        },
        {
            "test_name": "Feature Order Optimization",
            "hypothesis": "Prioritizing most-engaged features will increase overall engagement",
            "variants": [
                {"variant": "A (control)", "order": ["Temp Reg", "Easy Change", "Soft Seams"]},
                {"variant": "B", "order": ["Temp Reg", "Soft Seams", "Easy Change"]},
                {"variant": "C", "order": ["Easy Change", "Temp Reg", "Soft Seams"]}
            ],
            "success_metric": "Overall feature engagement rate + conversion",
            "minimum_sample_size": 2000,
            "estimated_test_duration": "14-21 days",
            "implementation_complexity": "Low"
        },
        {
            "test_name": "Social Proof Format",
            "hypothesis": "Visual social proof will outperform text-only reviews",
            "variants": [
                {"variant": "A (control)", "format": "Text reviews only"},
                {"variant": "B", "format": "Text reviews + customer photos"},
                {"variant": "C", "format": "Video testimonials + text reviews"}
            ],
            "success_metric": "Time spent in reviews section + conversion rate",
            "minimum_sample_size": 1500,
            "estimated_test_duration": "14-21 days",
            "implementation_complexity": "Medium"
        }
    ],
    
    "product_insights": {
        "bestsellers": [
            {
                "product": "Organic Cotton Sleepsuit - White",
                "insight": "10% conversion rate from views - significantly above average",
                "action": "Feature more prominently, ensure always in stock, consider expanding color range"
            },
            {
                "product": "Zip Sleepsuit - Blue",
                "insight": "8.4% conversion rate - strong performer",
                "action": "Highlight zip feature more in category messaging"
            }
        ],
        "range_gaps": [
            {
                "gap": "Limited organic options in larger sizes",
                "evidence": "Organic cotton searches drop off after 6-9m size",
                "recommendation": "Expand organic range to 12-18m and 18-24m"
            },
            {
                "gap": "No premium/luxury tier",
                "evidence": "25% of visitors spending 3+ minutes suggest research-intensive buyers",
                "recommendation": "Consider adding premium sleepsuit range at Â£25-35"
            }
        ]
    },
    
    "channel_performance": {
        "paid_search": {
            "performance": "Strong - 26% of traffic, 3.1% conversion rate",
            "action": "Maintain current investment, test expanding to additional keywords"
        },
        "organic": {
            "performance": "Excellent - 36% of traffic, 2.8% conversion rate",
            "action": "SEO strategy working well, continue content optimization"
        },
        "email": {
            "performance": "Good - 14% of traffic, 3.4% conversion rate (highest)",
            "action": "Email audience highly engaged, consider increasing send frequency"
        },
        "social": {
            "performance": "Weak - only 7% of traffic, 1.8% conversion rate",
            "action": "Increase social investment, review content strategy, test more video content"
        }
    },
    
    "next_steps": {
        "immediate_actions": [
            "1. Implement hero CTA A/B test (can launch today)",
            "2. Move size guide higher on page (can implement this week)",
            "3. Collect more customer photo reviews"
        ],
        "short_term": [
            "1. Test feature reordering (2-3 weeks)",
            "2. Launch enhanced reviews section (3-4 weeks)",
            "3. Increase social media investment and content frequency"
        ],
        "long_term": [
            "1. Develop product comparison tool (6-8 weeks)",
            "2. Expand organic cotton range (product development required)",
            "3. Explore premium product tier"
        ]
    },
    
    "export_files": {
        "detailed_report_pdf": "category_analysis_november_2025.pdf",
        "ab_test_plan_xlsx": "ab_test_roadmap.xlsx",
        "optimization_checklist": "optimization_actions.pdf"
    }
}
```

**Execution Time:** ~2-3 minutes (depending on report size)

---

## Implementation Flow

### Sequence Diagram

```
User                Frontend            Backend/Overlord        Research        Content         Other Agents
 |                     |                      |                    |               |                 |
 |--Category URL------>|                      |                    |               |                 |
 |                     |--POST /campaign----->|                    |               |                 |
 |                     |                      |--Initialize------->|               |                 |
 |                     |                      |    State           |               |                 |
 |                     |<--WebSocket Open-----|                    |               |                 |
 |<--"Starting..."-----|                      |                    |               |                 |
 |                     |                      |                    |               |                 |
 |                     |                      |--Run Research----->|               |                 |
 |                     |                      |                    |--Scrape------>|                 |
 |                     |                      |                    |--Search------>|                 |
 |<--"Research 50%"----|<--Progress Update----|                    |               |                 |
 |                     |                      |<--Research Data----|               |                 |
 |<--"Research Done"---|<--Progress Update----|                    |               |                 |
 |                     |                      |                    |               |                 |
 |                     |                      |--------Run Content Agents--------->|                 |
 |                     |                      |                    |               |--Generate------>|
 |                     |                      |                    |               |  Images         |
 |<--"Content 70%"-----|<--Progress Update----|                    |               |                 |
 |                     |                      |                    |               |                 |
 |                     |                      |--------Run Marketing Agents--------|---------------->|
 |                     |                      |                    |               |                 |
 |<--"Marketing 90%"---|<--Progress Update----|                    |               |                 |
 |                     |                      |                    |               |                 |
 |                     |                      |<--------All Agents Complete--------|-----------------|
 |                     |                      |--Consolidate------>|               |                 |
 |                     |                      |                    |               |                 |
 |                     |<--Campaign Package---|                    |               |                 |
 |<--Display Results---|                      |                    |               |                 |
 |                     |                      |                    |               |                 |
```

### Execution Steps

1. **User Input** (Frontend)
   - User enters category URL
   - Optional: budget, launch date
   - Submits form

2. **Initialization** (Backend)
   - Validate URL
   - Create campaign ID
   - Initialize LangGraph state
   - Open WebSocket for progress updates

3. **Research Phase** (Research Agent)
   - Scrape category page
   - Parse product data
   - Search parent questions
   - Competitor analysis
   - Update state with research_data
   - Progress: 0% â†’ 30%

4. **Content Generation Phase** (Content Agent)
   - Generate hero content
   - Create feature callouts
   - Generate image prompts
   - Call Imagen 3 API
   - Wait for image generation
   - Update state with content_outputs
   - Progress: 30% â†’ 60%

5. **Marketing Phase** (Parallel execution)
   - **Social Media Agent**: Create 3-5 posts
   - **Performance Marketing Agent**: Build PPC plan
   - **CRM Agent**: Generate emails with HTML
   - All agents run simultaneously
   - Progress: 60% â†’ 90%

6. **Consolidation** (Overlord Agent)
   - Collect all agent outputs
   - Create final package
   - Generate export files
   - Progress: 90% â†’ 100%

7. **Delivery** (Backend â†’ Frontend)
   - Send complete package via WebSocket
   - Frontend displays results in tabbed interface
   - User reviews and exports

8. **Post-Launch** (Later - Analyst Agent)
   - User uploads BI report
   - Analyst Agent processes data
   - Returns optimization recommendations

### Error Handling

```python
# Graceful degradation
if research_agent_fails:
    log_error()
    use_minimal_research_data()
    continue_with_other_agents()

if content_agent_fails:
    log_error()
    skip_image_generation()
    continue_with_text_only()

if single_marketing_agent_fails:
    log_error()
    continue_with_other_marketing_agents()

# Always return partial results
return {
    "status": "partial_success",
    "completed_agents": ["research", "content", "social"],
    "failed_agents": ["ppc", "crm"],
    "errors": [...]
}
```

---

## Tech Stack

### Backend

```python
# Core Framework
fastapi==0.104.1              # API server
uvicorn==0.24.0               # ASGI server
websockets==12.0              # Real-time updates

# Agent Orchestration
langchain==0.1.0              # LLM framework
langgraph==0.0.20             # Agent workflow graphs
anthropic==0.8.0              # Claude API

# Google Cloud
google-cloud-aiplatform==1.38.0  # Vertex AI / Imagen 3

# Email Generation
mjml==4.14.0                  # Responsive email HTML

# Web Scraping & Search
beautifulsoup4==4.12.0        # HTML parsing
requests==2.31.0              # HTTP client
playwright==1.40.0            # JavaScript rendering (if needed)

# Data Processing
pandas==2.1.4                 # Data analysis (Analyst Agent)
scipy==1.11.4                 # Statistical testing
openpyxl==3.1.2              # Excel file handling

# Database & Queue
sqlalchemy==2.0.23           # ORM
alembic==1.13.0              # Database migrations
redis==5.0.1                 # Queue & caching
celery==5.3.4                # Async task queue

# Storage
boto3==1.34.0                # AWS S3 for file storage

# Utilities
python-dotenv==1.0.0         # Environment variables
pydantic==2.5.0              # Data validation
```

### Frontend

```javascript
// Core Framework
"react": "^18.2.0"
"react-dom": "^18.2.0"
"next.js": "^14.0.4"        // or create-react-app

// State Management
"zustand": "^4.4.7"          // Lightweight state management
// or
"redux": "^5.0.0"
"@reduxjs/toolkit": "^2.0.0"

// UI Components
"@mui/material": "^5.15.0"   // Material UI
// or
"@chakra-ui/react": "^2.8.2" // Chakra UI
// or
"antd": "^5.12.0"            // Ant Design

// Forms
"react-hook-form": "^7.49.0"
"zod": "^3.22.4"             // Validation

// Communication
"axios": "^1.6.2"            // HTTP client
"socket.io-client": "^4.7.0" // WebSocket

// File Handling
"file-saver": "^2.0.5"       // Download files
"react-dropzone": "^14.2.0"  // File upload

// Visualization
"recharts": "^2.10.0"        // Charts for analyst dashboard

// Utilities
"date-fns": "^3.0.0"         // Date formatting
"clsx": "^2.0.0"             // Conditional classes
```

### Infrastructure

```yaml
# Docker Compose (Development)
services:
  backend:
    image: python:3.11
    ports: ["8000:8000"]
    
  frontend:
    image: node:20
    ports: ["3000:3000"]
    
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: marketing_agents
      
  redis:
    image: redis:7
    ports: ["6379:6379"]
```

### External Services

- **Claude API** (Anthropic) - LLM for all agents
- **Google Vertex AI** - Imagen 3 image generation
- **AWS S3** - File storage for generated assets
- **PostgreSQL** - Campaign data, user inputs, results
- **Redis** - Queue management, caching

---

## Frontend Interface

### Screen Flow

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚     1. Input Screen                 â”‚
â”‚                                     â”‚
â”‚  Enter Category URL:                â”‚
â”‚  [https://store.com/category]       â”‚
â”‚                                     â”‚
â”‚  Optional Settings:                 â”‚
â”‚  Budget: [Â£5000]                    â”‚
â”‚  Launch Date: [2025-12-01]          â”‚
â”‚                                     â”‚
â”‚  [Generate Campaign] button         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                  â”‚
                  â†“ (WebSocket starts)
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚     2. Progress Dashboard           â”‚
â”‚                                     â”‚
â”‚  â–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–ˆâ–‘â–‘â–‘â–‘â–‘â–‘â–‘â–‘ 60%               â”‚
â”‚                                     â”‚
â”‚  âœ“ Research Agent (completed)       â”‚
â”‚  âœ“ Content Agent (completed)        â”‚
â”‚  â†’ Social Media Agent (running...)  â”‚
â”‚  â³ Performance Marketing (queued)   â”‚
â”‚  â³ CRM Agent (queued)               â”‚
â”‚                                     â”‚
â”‚  Logs:                              â”‚
â”‚  [14:32] Research: Found 45 productsâ”‚
â”‚  [14:33] Content: Generated hero    â”‚
â”‚  [14:34] Content: Images generating â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                  â”‚
                  â†“ (Completion)
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚     3. Review Interface (Tabs)      â”‚
â”‚                                     â”‚
â”‚  [Research] [Content] [Social]      â”‚
â”‚  [PPC] [CRM] [Export]               â”‚
â”‚                                     â”‚
â”‚  Currently viewing: Content         â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”  â”‚
â”‚  â”‚ Hero Section                  â”‚  â”‚
â”‚  â”‚ Headline: "Sleep Easy..."     â”‚  â”‚
â”‚  â”‚ [Edit] [Regenerate]           â”‚  â”‚
â”‚  â”‚                               â”‚  â”‚
â”‚  â”‚ [Preview Image]               â”‚  â”‚
â”‚  â”‚                               â”‚  â”‚
â”‚  â”‚ Features:                     â”‚  â”‚
â”‚  â”‚ 1. Temperature Regulation     â”‚  â”‚
â”‚  â”‚    [Edit] [Preview Image]     â”‚  â”‚
â”‚  â”‚ 2. Easy Nappy Changes         â”‚  â”‚
â”‚  â”‚    [Edit] [Preview Image]     â”‚  â”‚
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜  â”‚
â”‚                                     â”‚
â”‚  [Export All] [Save Draft]          â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

### Key Components

#### 1. Input Form Component

```tsx
interface CategoryInputProps {
  onSubmit: (data: CampaignInput) => void;
}

const CategoryInputForm: React.FC<CategoryInputProps> = ({ onSubmit }) => {
  const [url, setUrl] = useState('');
  const [budget, setBudget] = useState<number>();
  const [launchDate, setLaunchDate] = useState<Date>();

  return (
    <form onSubmit={handleSubmit}>
      <TextField
        label="Category URL"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
        required
        placeholder="https://yourstore.com/baby-sleepsuits"
      />
      
      <TextField
        label="Budget (optional)"
        type="number"
        value={budget}
        onChange={(e) => setBudget(Number(e.target.value))}
      />
      
      <DatePicker
        label="Launch Date (optional)"
        value={launchDate}
        onChange={setLaunchDate}
      />
      
      <Button type="submit">Generate Campaign</Button>
    </form>
  );
};
```

#### 2. Progress Dashboard Component

```tsx
interface ProgressDashboardProps {
  progress: number;
  currentStep: string;
  agentStatuses: AgentStatus[];
  logs: LogEntry[];
}

const ProgressDashboard: React.FC<ProgressDashboardProps> = ({
  progress,
  currentStep,
  agentStatuses,
  logs
}) => {
  return (
    <div>
      <LinearProgress value={progress} />
      <Typography>{currentStep}</Typography>
      
      <AgentStatusList>
        {agentStatuses.map(agent => (
          <AgentStatusItem
            key={agent.name}
            name={agent.name}
            status={agent.status} // completed | running | queued | failed
            icon={getStatusIcon(agent.status)}
          />
        ))}
      </AgentStatusList>
      
      <LogViewer logs={logs} />
    </div>
  );
};
```

#### 3. Review Tabs Component

```tsx
const ReviewInterface: React.FC<{ campaign: Campaign }> = ({ campaign }) => {
  const [activeTab, setActiveTab] = useState('content');
  
  return (
    <Tabs value={activeTab} onChange={setActiveTab}>
      <Tab label="Research" value="research">
        <ResearchView data={campaign.research_data} />
      </Tab>
      
      <Tab label="Content" value="content">
        <ContentView 
          content={campaign.content_outputs}
          onEdit={handleEdit}
        />
      </Tab>
      
      <Tab label="Social Media" value="social">
        <SocialMediaView posts={campaign.social_media_plan} />
      </Tab>
      
      <Tab label="PPC" value="ppc">
        <PPCView 
          campaign={campaign.ppc_campaign}
          onDownloadCSV={handleDownloadPPC}
        />
      </Tab>
      
      <Tab label="CRM" value="crm">
        <CRMView 
          emails={campaign.crm_plan}
          onPreviewEmail={handlePreviewEmail}
          onDownloadHTML={handleDownloadHTML}
        />
      </Tab>
      
      <Tab label="Export" value="export">
        <ExportOptions campaign={campaign} />
      </Tab>
    </Tabs>
  );
};
```

#### 4. Content Review Component

```tsx
const ContentView: React.FC<ContentViewProps> = ({ content, onEdit }) => {
  return (
    <div>
      <Section title="Hero Section">
        <EditableText
          label="Headline"
          value={content.hero_section.headline}
          onSave={(val) => onEdit('hero.headline', val)}
        />
        <EditableText
          label="Subheadline"
          value={content.hero_section.subheadline}
          onSave={(val) => onEdit('hero.subheadline', val)}
        />
        <ImagePreview 
          src={content.hero_section.generated_image_url}
          alt="Hero image"
        />
        <Button onClick={() => regenerateImage('hero')}>
          Regenerate Image
        </Button>
      </Section>
      
      <Section title="Key Features">
        {content.key_features.map((feature, idx) => (
          <FeatureCard
            key={idx}
            feature={feature}
            onEdit={(field, val) => onEdit(`feature.${idx}.${field}`, val)}
          />
        ))}
      </Section>
      
      <Section title="SEO">
        <EditableText
          label="Meta Title"
          value={content.seo_meta.title}
          maxLength={60}
        />
        <EditableText
          label="Meta Description"
          value={content.seo_meta.description}
          maxLength={160}
        />
      </Section>
    </div>
  );
};
```

#### 5. Email Preview Component

```tsx
const EmailPreview: React.FC<{ email: Email }> = ({ email }) => {
  const [previewMode, setPreviewMode] = useState<'desktop' | 'mobile'>('desktop');
  
  return (
    <div>
      <div>
        <strong>Subject:</strong> {email.subject_line}
      </div>
      <div>
        <strong>Preview Text:</strong> {email.preview_text}
      </div>
      
      <ButtonGroup>
        <Button onClick={() => setPreviewMode('desktop')}>Desktop</Button>
        <Button onClick={() => setPreviewMode('mobile')}>Mobile</Button>
      </ButtonGroup>
      
      <iframe
        srcDoc={email.html_compiled}
        style={{
          width: previewMode === 'desktop' ? '600px' : '375px',
          height: '800px',
          border: '1px solid #ccc'
        }}
      />
      
      <Button onClick={() => downloadHTML(email)}>
        Download HTML
      </Button>
      <Button onClick={() => sendTestEmail(email)}>
        Send Test Email
      </Button>
    </div>
  );
};
```

#### 6. Post-Launch Analyst Upload

```tsx
const AnalystUpload: React.FC = () => {
  const [file, setFile] = useState<File | null>(null);
  const [analysis, setAnalysis] = useState<AnalysisResult | null>(null);
  
  const handleUpload = async () => {
    const formData = new FormData();
    formData.append('bi_report', file);
    
    const result = await fetch('/api/analyze', {
      method: 'POST',
      body: formData
    });
    
    setAnalysis(await result.json());
  };
  
  return (
    <div>
      <Typography variant="h5">Upload BI Report</Typography>
      
      <Dropzone onDrop={(files) => setFile(files[0])}>
        {file ? file.name : 'Drop CSV or Excel file here'}
      </Dropzone>
      
      <Button onClick={handleUpload} disabled={!file}>
        Analyze Performance
      </Button>
      
      {analysis && (
        <AnalysisResults data={analysis} />
      )}
    </div>
  );
};
```

### WebSocket Communication

```typescript
// Frontend WebSocket client
const ws = new WebSocket('ws://localhost:8000/ws/campaign/{campaignId}');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  switch(data.type) {
    case 'progress':
      updateProgress(data.percentage, data.message);
      break;
    case 'agent_complete':
      markAgentComplete(data.agent_name);
      break;
    case 'error':
      showError(data.message);
      break;
    case 'complete':
      showResults(data.campaign);
      break;
  }
};
```

---

## Data Flow

### Database Schema

```sql
-- Campaigns table
CREATE TABLE campaigns (
    id UUID PRIMARY KEY,
    user_id UUID NOT NULL,
    category_url TEXT NOT NULL,
    category_name TEXT,
    status VARCHAR(50), -- pending, running, completed, failed
    created_at TIMESTAMP DEFAULT NOW(),
    completed_at TIMESTAMP,
    budget DECIMAL(10,2),
    launch_date DATE
);

-- Agent executions
CREATE TABLE agent_executions (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    agent_name VARCHAR(100),
    status VARCHAR(50),
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    output JSONB,
    errors JSONB
);

-- Generated assets
CREATE TABLE assets (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    asset_type VARCHAR(50), -- image, html, csv, pdf
    file_url TEXT,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Campaign results
CREATE TABLE campaign_results (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    research_data JSONB,
    content_outputs JSONB,
    social_media_plan JSONB,
    ppc_campaign JSONB,
    crm_plan JSONB,
    analyst_insights JSONB
);

-- BI reports (for analyst agent)
CREATE TABLE bi_reports (
    id UUID PRIMARY KEY,
    campaign_id UUID REFERENCES campaigns(id),
    file_url TEXT,
    upload_date TIMESTAMP DEFAULT NOW(),
    analysis_result JSONB
);
```

### File Storage Structure

```
s3://marketing-agents-bucket/
â”œâ”€â”€ campaigns/
â”‚   â””â”€â”€ {campaign_id}/
â”‚       â”œâ”€â”€ images/
â”‚       â”‚   â”œâ”€â”€ hero.jpg
â”‚       â”‚   â”œâ”€â”€ feature_1.jpg
â”‚       â”‚   â”œâ”€â”€ feature_2.jpg
â”‚       â”‚   â””â”€â”€ icons/
â”‚       â”‚       â”œâ”€â”€ icon_1.png
â”‚       â”‚       â””â”€â”€ icon_2.png
â”‚       â”œâ”€â”€ emails/
â”‚       â”‚   â”œâ”€â”€ launch_announcement.html
â”‚       â”‚   â”œâ”€â”€ launch_announcement.txt
â”‚       â”‚   â”œâ”€â”€ feature_spotlight.html
â”‚       â”‚   â””â”€â”€ ...
â”‚       â”œâ”€â”€ exports/
â”‚       â”‚   â”œâ”€â”€ ppc_keywords.csv
â”‚       â”‚   â”œâ”€â”€ ppc_ads.csv
â”‚       â”‚   â”œâ”€â”€ campaign_structure.xlsx
â”‚       â”‚   â””â”€â”€ complete_package.zip
â”‚       â””â”€â”€ reports/
â”‚           â”œâ”€â”€ bi_report.csv
â”‚           â””â”€â”€ analysis_report.pdf
```

---

## Implementation Phases

### Phase 1: MVP (3-4 weeks)
**Goal:** Prove concept with core functionality

**Features:**
- âœ… Overlord Agent orchestration
- âœ… Research Agent (scraping + search)
- âœ… Content Agent (text + image generation)
- âœ… Basic React frontend (input + progress + results)
- âœ… PostgreSQL database
- âœ… File storage (S3)

**Tech Setup:**
- FastAPI backend
- LangGraph for agent coordination
- Claude API integration
- Google Imagen 3 integration
- Basic React UI (no fancy styling)

**Deliverables:**
- Working end-to-end flow
- Research â†’ Content generation
- Generated images via Imagen 3
- Simple results display
- Export content as JSON

**Success Criteria:**
- Can input category URL
- Research completes in <3 min
- Content generated with images
- Results viewable in UI

---

### Phase 2: Marketing Agents (4-5 weeks)
**Goal:** Add marketing channel capabilities

**Features:**
- âœ… Social Media Agent (3-5 posts)
- âœ… Performance Marketing Agent (PPC plan)
- âœ… Export CSVs for Google Ads upload
- âœ… Enhanced frontend with tabs
- âœ… Edit capabilities for generated content
- âœ… Progress dashboard with WebSocket updates

**Tech Additions:**
- WebSocket for real-time progress
- Enhanced UI components (tabs, cards)
- CSV generation utilities
- Parallel agent execution

**Deliverables:**
- Social media post generation
- Complete PPC campaign structure
- Downloadable CSV/Excel files
- Tabbed review interface
- Edit and regenerate capabilities

**Success Criteria:**
- 3-5 social posts generated
- PPC campaign ready for manual upload
- UI allows review and editing
- Export files work correctly

---

### Phase 3: CRM & Email (3-4 weeks)
**Goal:** Add email campaign generation

**Features:**
- âœ… CRM Agent with MJML email generation
- âœ… Responsive HTML email output
- âœ… Email preview in UI (desktop/mobile)
- âœ… Plain text versions
- âœ… Download HTML files
- âœ… Send test email functionality

**Tech Additions:**
- MJML Python library
- Email preview component
- SMTP integration for test sends
- HTML file downloads

**Deliverables:**
- 3-4 broadcast emails with HTML
- 3-5 automation trigger emails
- Push notification plans
- Email preview UI
- Downloadable HTML files

**Success Criteria:**
- Emails render correctly in major clients
- Mobile responsive design works
- Can send test emails
- Plain text versions generated

---

### Phase 4: Analytics & Polish (3-4 weeks)
**Goal:** Add post-launch analysis and production polish

**Features:**
- âœ… Analyst Agent (BI report processing)
- âœ… File upload for BI reports
- âœ… Statistical analysis
- âœ… A/B test recommendations
- âœ… Production-ready UI polish
- âœ… Error handling improvements
- âœ… User authentication
- âœ… Campaign history

**Tech Additions:**
- pandas/scipy for data analysis
- File upload component
- User authentication (Auth0 or similar)
- Campaign management dashboard

**Deliverables:**
- BI report analysis functionality
- Optimization recommendations
- Polished UI design
- User account system
- Campaign history view

**Success Criteria:**
- Can upload and analyze BI reports
- Recommendations are actionable
- UI is production-ready
- Multiple users can use system

---

### Phase 5: Advanced Features (Ongoing)
**Goal:** Continuous improvement and advanced capabilities

**Potential Features:**
- ðŸ”„ Multi-category campaigns
- ðŸ”„ Seasonal campaign templates
- ðŸ”„ Integration with CMS (auto-publish content)
- ðŸ”„ Integration with Google Ads API (auto-create campaigns)
- ðŸ”„ Integration with email platform (auto-schedule sends)
- ðŸ”„ Learning from past campaigns
- ðŸ”„ Competitive monitoring
- ðŸ”„ Real-time performance tracking
- ðŸ”„ Automated A/B testing
- ðŸ”„ Multi-language support

---

## Cost & Performance Estimates

### Per-Campaign Costs

**LLM API Calls:**
- Research Agent: ~8K tokens input, ~4K output = ~$0.15
- Content Agent: ~6K input, ~3K output = ~$0.12
- Social Media Agent: ~4K input, ~2K output = ~$0.08
- PPC Agent: ~5K input, ~3K output = ~$0.10
- CRM Agent: ~6K input, ~4K output = ~$0.13
- **Total LLM cost per campaign: ~$0.58**

**Image Generation:**
- Google Imagen 3: ~$0.04 per image
- Typical campaign: 1 hero + 3-5 features = 4-6 images
- **Total image cost: ~$0.16-0.24**

**Total Cost Per Campaign: ~$0.75-0.85**

### Performance Metrics

**Execution Times:**
- Research Agent: 2-3 minutes
- Content Agent: 3-4 minutes (including image generation)
- Marketing Agents (parallel): 2-3 minutes
- **Total end-to-end: 7-10 minutes**

**Scalability:**
- With current architecture: 10-20 concurrent campaigns
- With queue system (Celery): 100+ concurrent campaigns
- Database can handle 10K+ campaigns

### Infrastructure Costs (Monthly)

**Production Environment:**
- EC2 instance (t3.large): $60/month
- RDS PostgreSQL (db.t3.small): $25/month
- S3 storage (100GB): $2.30/month
- Redis (ElastiCache): $15/month
- **Total infrastructure: ~$102/month**

**At 100 campaigns/month:**
- API costs: $85
- Infrastructure: $102
- **Total: $187/month**
- **Cost per campaign: $1.87**

**At 1000 campaigns/month:**
- API costs: $850
- Infrastructure: $102 (same)
- **Total: $952/month**
- **Cost per campaign: $0.95**

---

## Appendix

### Sample API Endpoints

```python
# Campaign Management
POST   /api/campaigns              # Create new campaign
GET    /api/campaigns              # List user's campaigns
GET    /api/campaigns/{id}         # Get campaign details
DELETE /api/campaigns/{id}         # Delete campaign
PUT    /api/campaigns/{id}         # Update campaign (edit content)

# Agent Execution
POST   /api/campaigns/{id}/regenerate/{agent}  # Regenerate agent output
POST   /api/campaigns/{id}/rerun               # Rerun entire campaign

# Assets
GET    /api/campaigns/{id}/assets              # List all assets
GET    /api/assets/{id}/download               # Download specific asset

# Export
GET    /api/campaigns/{id}/export/all          # Download complete package
GET    /api/campaigns/{id}/export/ppc          # Download PPC CSVs
GET    /api/campaigns/{id}/export/emails       # Download email HTMLs

# Analyst
POST   /api/campaigns/{id}/analyze             # Upload BI report
GET    /api/campaigns/{id}/analysis            # Get analysis results

# WebSocket
WS     /ws/campaign/{id}                       # Real-time progress updates
```

### Environment Variables

```bash
# API Keys
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_CLOUD_PROJECT=your-project-id
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/marketing_agents

# Redis
REDIS_URL=redis://localhost:6379/0

# Storage
AWS_ACCESS_KEY_ID=...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET=marketing-agents-bucket

# App
SECRET_KEY=your-secret-key
DEBUG=false
ALLOWED_HOSTS=yourdomain.com

# External Services (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASSWORD=...
```

### Deployment Checklist

**Pre-deployment:**
- [ ] Set all environment variables
- [ ] Run database migrations
- [ ] Test all agent executions
- [ ] Verify image generation works
- [ ] Test email HTML rendering
- [ ] Load test with 10 concurrent campaigns
- [ ] Set up monitoring (Sentry, DataDog)
- [ ] Set up backup strategy

**Deployment:**
- [ ] Deploy backend to EC2/ECS
- [ ] Deploy frontend to Vercel/Netlify
- [ ] Configure DNS
- [ ] Set up SSL certificates
- [ ] Configure CORS
- [ ] Set up rate limiting
- [ ] Enable error tracking

**Post-deployment:**
- [ ] Monitor error rates
- [ ] Check API response times
- [ ] Verify WebSocket connections stable
- [ ] Test campaign generation end-to-end
- [ ] Collect user feedback
- [ ] Iterate on agent prompts

---

## Next Steps

1. **Validate Approach**: Review this specification with team
2. **Set Up Development Environment**: 
   - Create GitHub repository
   - Set up Python virtual environment
   - Initialize React project
   - Configure API keys
3. **Start Phase 1 Development**:
   - Build Overlord Agent skeleton
   - Implement Research Agent
   - Implement Content Agent
   - Create basic UI
4. **Test & Iterate**: Run with real category URLs
5. **Proceed to Phase 2**: Add marketing agents

---

**Document Version:** 1.0  
**Last Updated:** 2025-11-12  
**Status:** Ready for Implementation