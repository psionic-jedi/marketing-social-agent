"""
Article Generator Service - Generates full SEO-optimized articles from content ideas.
"""
import logging
from typing import Dict, List
from anthropic import Anthropic

from app.core.config import settings

logger = logging.getLogger(__name__)


class ArticleGenerator:
    """Service for generating full articles from content ideas."""

    def __init__(self, db=None, campaign_id: str = None):
        self.anthropic = Anthropic(api_key=settings.anthropic_api_key)
        self.db = db
        self.campaign_id = campaign_id

    async def generate_full_article(
        self,
        title: str,
        intro: str,
        article_type: str,
        key_topics: List[str],
        target_audience: str,
        seo_keywords: List[str],
        category_name: str,
        products: List[Dict]
    ) -> Dict:
        """
        Generate a complete SEO-optimized article.

        Args:
            title: Article title
            intro: Article introduction/hook
            article_type: Type of article (buying_guide, how_to, educational, seasonal)
            key_topics: Main topics to cover
            target_audience: Who the article is for
            seo_keywords: Keywords to optimize for
            category_name: Product category name
            products: Sample products for context

        Returns:
            Dict with full article content, meta data, and structure
        """
        # Build product context
        product_examples = []
        for p in products[:8]:
            product_examples.append(f"- {p.get('name', 'Product')}: {p.get('description', '')[:100]}")
        product_context = "\n".join(product_examples) if product_examples else "Various children's products"

        # Build the prompt based on article type
        type_instructions = self._get_type_instructions(article_type)

        prompt = f"""You are an expert content writer for a premium children's clothing retailer.
Write a comprehensive, helpful article that provides genuine value to parents.

ARTICLE DETAILS:
Title: {title}
Introduction: {intro}
Article Type: {article_type}
Target Audience: {target_audience}
Key Topics to Cover: {', '.join(key_topics)}
SEO Keywords: {', '.join(seo_keywords)}
Product Category: {category_name}

SAMPLE PRODUCTS FOR CONTEXT:
{product_context}

{type_instructions}

WRITING GUIDELINES:
1. Write in a warm, knowledgeable, but not condescending tone
2. Use British English spelling
3. Include practical, actionable advice that parents can use immediately
4. Back up claims with reasoning (e.g., "because newborns can't regulate temperature...")
5. Include specific examples and scenarios
6. Make it scannable with clear headers and bullet points where appropriate
7. Naturally incorporate the SEO keywords without keyword stuffing
8. Write 1000-1500 words for the main body content
9. Include a compelling conclusion with a subtle call-to-action

IMPORTANT: Return ONLY valid JSON in this exact format:
{{
  "meta": {{
    "title": "SEO-optimised page title (50-60 chars)",
    "description": "Meta description for search results (150-160 chars)",
    "keywords": ["keyword1", "keyword2", "keyword3"]
  }},
  "article": {{
    "headline": "Main headline (can differ from meta title)",
    "subheadline": "Supporting subheadline",
    "introduction": "Opening paragraph that hooks the reader (expanded from the brief intro)",
    "sections": [
      {{
        "heading": "H2 Section Heading",
        "content": "Full paragraph content for this section...",
        "subsections": [
          {{
            "heading": "H3 Subsection (optional)",
            "content": "Subsection content..."
          }}
        ]
      }}
    ],
    "key_takeaways": [
      "Bullet point takeaway 1",
      "Bullet point takeaway 2",
      "Bullet point takeaway 3"
    ],
    "conclusion": "Concluding paragraph with subtle CTA",
    "word_count": 1200
  }},
  "internal_links": [
    {{
      "anchor_text": "suggested anchor text",
      "target_page": "suggested page to link to (e.g., /category/nightwear)"
    }}
  ],
  "faq": [
    {{
      "question": "Common question related to the topic?",
      "answer": "Helpful answer..."
    }}
  ]
}}"""

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=8000,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            # Track cost if db session and campaign_id are available
            if self.db and self.campaign_id:
                try:
                    from app.services.cost_tracker import save_single_usage
                    save_single_usage(self.db, self.campaign_id, "article_generator", "generate_article", response)
                except Exception as cost_err:
                    logger.warning(f"Failed to save article generation cost: {cost_err}")

            import json
            response_text = response.content[0].text.strip()

            # Clean markdown if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            article_data = json.loads(response_text)

            # Add generation metadata
            article_data["generation_info"] = {
                "article_type": article_type,
                "target_audience": target_audience,
                "category": category_name,
                "generated_for_title": title
            }

            logger.info(f"Generated article: {title[:50]}...")
            return article_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse article JSON: {e}")
            # Return a structured error response
            return self._generate_fallback_article(title, intro, key_topics, category_name)

        except Exception as e:
            logger.error(f"Error generating article: {e}", exc_info=True)
            raise

    def _get_type_instructions(self, article_type: str) -> str:
        """Get specific instructions based on article type."""
        instructions = {
            "buying_guide": """
BUYING GUIDE SPECIFIC INSTRUCTIONS:
- Include a "What to Look For" section with key features to consider
- Add a comparison of different options/price points
- Include sizing guidance where relevant
- Mention quality indicators and red flags
- Add a "Best For" section matching product types to needs
- Include care and maintenance tips
""",
            "how_to": """
HOW-TO GUIDE SPECIFIC INSTRUCTIONS:
- Structure content as clear, numbered steps where appropriate
- Include "Why this matters" explanations for key steps
- Add common mistakes to avoid
- Include visual description suggestions (what images would help)
- Provide alternatives for different situations
- End with troubleshooting tips
""",
            "educational": """
EDUCATIONAL CONTENT SPECIFIC INSTRUCTIONS:
- Lead with the key facts parents need to know
- Explain the science/reasoning behind recommendations
- Include age-specific guidance where relevant
- Reference safety guidelines where applicable
- Debunk common myths if relevant
- Include expert tips or professional recommendations
""",
            "seasonal": """
SEASONAL CONTENT SPECIFIC INSTRUCTIONS:
- Include specific seasonal considerations (temperature, weather, occasions)
- Provide a checklist of essentials
- Include layering guidance where relevant
- Mention timing for purchases/preparation
- Include both immediate and upcoming season needs
- Add storage tips for off-season items
"""
        }
        return instructions.get(article_type, instructions["buying_guide"])

    def _generate_fallback_article(self, title: str, intro: str, key_topics: List[str], category_name: str) -> Dict:
        """Generate a basic fallback article structure if AI generation fails."""
        return {
            "meta": {
                "title": title[:60],
                "description": intro[:160],
                "keywords": key_topics[:5]
            },
            "article": {
                "headline": title,
                "subheadline": f"Your complete guide to {category_name}",
                "introduction": intro,
                "sections": [
                    {
                        "heading": topic.title(),
                        "content": f"Content about {topic} for {category_name}...",
                        "subsections": []
                    }
                    for topic in key_topics[:4]
                ],
                "key_takeaways": [
                    f"Key point about {topic}" for topic in key_topics[:3]
                ],
                "conclusion": f"We hope this guide helps you find the perfect {category_name} for your little one.",
                "word_count": 0
            },
            "internal_links": [],
            "faq": [],
            "generation_info": {
                "fallback": True,
                "reason": "AI generation failed - basic structure provided"
            }
        }
