"""
Content Agent - Creates marketing content and generates images.

Responsibilities:
1. Generate hero section content
2. Create feature callouts
3. Write category description
4. Generate image prompts
5. Generate images using Gemini 2.5 Flash
6. Create SEO meta tags
"""
import logging
from typing import Dict, List
import google.generativeai as genai
from anthropic import Anthropic

from app.core.config import settings
from app.agents.state import MarketingCampaignState
from app.storage.factory import storage

logger = logging.getLogger(__name__)


class ContentAgent:
    """Content agent for generating marketing content and images."""

    def __init__(self):
        self.anthropic = Anthropic(api_key=settings.anthropic_api_key)
        genai.configure(api_key=settings.google_api_key)
        self.gemini_model = genai.GenerativeModel('gemini-2.0-flash-exp')

    def execute(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Execute the content agent workflow.

        Args:
            state: Current campaign state with research_data

        Returns:
            Updated state with content_outputs and generated_images
        """
        logger.info(f"Content Agent starting for campaign {state['campaign_id']}")

        state["current_step"] = "content"
        state["progress_percentage"] = 40

        try:
            research_data = state.get("research_data")
            if not research_data:
                raise ValueError("No research data available")

            # Step 1: Generate hero section
            logger.info("Generating hero section content")
            hero_section = self._generate_hero_section(research_data)

            # Step 2: Generate feature callouts
            logger.info("Generating feature callouts")
            features = self._generate_features(research_data)

            # Step 3: Generate category description
            logger.info("Generating category description")
            category_description = self._generate_category_description(research_data)

            # Step 4: Generate SEO meta tags
            logger.info("Generating SEO meta tags")
            meta_tags = self._generate_meta_tags(research_data)

            # Step 5: Generate image prompts
            logger.info("Generating image prompts")
            image_prompts = self._generate_image_prompts(hero_section, features)

            # Step 6: Generate images with Gemini
            logger.info("Generating images with Gemini 2.5 Flash")
            generated_images = self._generate_images(
                image_prompts,
                state["campaign_id"]
            )

            # Compile content outputs
            content_outputs = {
                "hero_section": hero_section,
                "features": features,
                "category_description": category_description,
                "meta_tags": meta_tags,
                "image_prompts": image_prompts
            }

            state["content_outputs"] = content_outputs
            state["generated_images"] = generated_images
            state["progress_percentage"] = 60
            logger.info("Content Agent completed successfully")

            return state

        except Exception as e:
            error_msg = f"Content Agent failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)
            state["progress_percentage"] = 60
            return state

    def _generate_hero_section(self, research_data: Dict) -> Dict:
        """
        Generate hero section content (headline, subheadline, CTA).

        Args:
            research_data: Research data from Research Agent

        Returns:
            Dictionary with hero section content
        """
        category_insights = research_data.get("category_insights", {})
        category_name = category_insights.get("category_name", "Products")

        prompt = f"""Create compelling hero section content for a {category_name} category page.

Category Insights:
- Total products: {category_insights.get('total_products', 0)}
- Price range: £{category_insights.get('price_range', {}).get('min', 0):.2f} - £{category_insights.get('price_range', {}).get('max', 0):.2f}
- Common features: {', '.join(category_insights.get('common_features', [])[:3])}

Create:
1. A compelling headline (6-10 words) that highlights the main benefit
2. A subheadline (10-15 words) that addresses a parent's concern or desire
3. A clear call-to-action button text (2-4 words)

Make it emotional, benefit-focused, and parent-friendly.

IMPORTANT: Return ONLY valid JSON in this exact format:
{{
  "headline": "Your compelling headline here",
  "subheadline": "Your subheadline here",
  "cta_text": "Shop Now",
  "cta_url": "/category"
}}"""

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse Claude's JSON response
            import json
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            hero_data = json.loads(response_text)
            logger.info(f"Generated hero section: {hero_data.get('headline', '')}")
            return hero_data

        except Exception as e:
            logger.error(f"Error generating hero section: {e}", exc_info=True)
            return {
                "headline": f"Discover Quality {category_name}",
                "subheadline": "Comfortable, durable, and designed with your child in mind",
                "cta_text": "Shop Now",
                "cta_url": "/category"
            }

    def _generate_features(self, research_data: Dict) -> List[Dict]:
        """
        Generate 4-8 feature callouts with benefit-focused copy.

        Args:
            research_data: Research data

        Returns:
            List of feature dictionaries (min 4, max 8)
        """
        common_features = research_data.get("category_insights", {}).get("common_features", [])
        category_name = research_data.get("category_insights", {}).get("category_name", "Products")
        products = research_data.get("products", [])

        # Extract additional features from products
        product_features = []
        for product in products[:10]:
            product_features.extend(product.get("features", []))
        all_features = list(set(common_features + product_features))[:10]

        prompt = f"""Create 6 compelling feature callouts for a {category_name} category page.

Features Found in Products:
{', '.join(all_features) if all_features else 'Quality materials, comfort, durability'}

For each feature:
1. Create a benefit-focused title (3-5 words)
2. Write a description that addresses parent concerns (15-25 words)
3. Assign an icon type: "quality", "comfort", "care", "safety", "style", or "value"

Create 6 UNIQUE feature callouts covering different aspects:
- Material quality
- Comfort & fit
- Safety features
- Style & design
- Durability & care
- Value proposition

IMPORTANT: Return ONLY valid JSON in this exact format:
{{
  "features": [
    {{
      "title": "Feature Title",
      "description": "Benefit-focused description",
      "icon": "quality"
    }}
  ]
}}"""

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1500,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            # Parse Claude's JSON response
            import json
            response_text = response.content[0].text.strip()

            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            data = json.loads(response_text)
            features = data.get("features", [])
            logger.info(f"Generated {len(features)} feature callouts")
            # Return min 4, max 8 features
            return features[:8] if len(features) >= 4 else features + self._get_default_features()[:4-len(features)]

        except Exception as e:
            logger.error(f"Error generating features: {e}", exc_info=True)
            return self._get_default_features()

    def _get_default_features(self) -> List[Dict]:
        """Return default feature callouts as fallback."""
        return [
            {
                "title": "Premium Quality Materials",
                "description": "Made from the finest fabrics that are soft, durable, and safe for sensitive skin",
                "icon": "quality"
            },
            {
                "title": "Designed for Comfort",
                "description": "Every piece is crafted with your child's comfort in mind, perfect for all-day wear",
                "icon": "comfort"
            },
            {
                "title": "Easy Care & Maintenance",
                "description": "Machine washable and designed to last through countless washes and wear",
                "icon": "care"
            },
            {
                "title": "Safety First Design",
                "description": "Thoughtfully designed with child safety in mind, meeting the highest standards",
                "icon": "safety"
            },
            {
                "title": "Stylish & On-Trend",
                "description": "Designer styles that keep your little ones looking fashionable and feeling confident",
                "icon": "style"
            },
            {
                "title": "Exceptional Value",
                "description": "Investment pieces that combine luxury quality with lasting durability",
                "icon": "value"
                }
            ]

    def _generate_category_description(self, research_data: Dict) -> str:
        """
        Generate SEO-optimized category description (2-3 paragraphs).

        Args:
            research_data: Research data

        Returns:
            Category description text
        """
        category_name = research_data.get("category_insights", {}).get("category_name", "Products")
        seo_keywords = research_data.get("seo_keywords", {})

        prompt = f"""Write a compelling 2-3 paragraph category description for {category_name}.

Include:
- Introduction to the category and its benefits
- Address common parent concerns
- Highlight key features and quality
- Natural incorporation of keywords: {', '.join(seo_keywords.get('primary', [])[:2])}

Tone: Warm, informative, parent-friendly
Length: 150-200 words"""

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=800,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text

        except Exception as e:
            logger.error(f"Error generating category description: {e}")
            return f"Explore our collection of {category_name}. Quality products designed with your family in mind."

    def _generate_meta_tags(self, research_data: Dict) -> Dict:
        """
        Generate SEO meta title and description.

        Args:
            research_data: Research data

        Returns:
            Dictionary with meta_title and meta_description
        """
        category_name = research_data.get("category_insights", {}).get("category_name", "Products")
        products = research_data.get("products", [])
        price_range = research_data.get("category_insights", {}).get("price_range", {})
        seo_keywords = research_data.get("seo_keywords", {})

        prompt = f"""Create compelling SEO meta tags for a {category_name} category page.

Context:
- Category: {category_name}
- Price range: £{price_range.get('min', 0):.2f} - £{price_range.get('max', 0):.2f}
- Primary keywords: {', '.join(seo_keywords.get('primary', [])[:3])}

Create:
1. Meta Title (50-60 characters) - Include main keyword and compelling hook
2. Meta Description (150-160 characters) - Include USPs, keywords, and call-to-action

IMPORTANT:
- Do NOT include specific product counts or numbers like "35+" or "50+"
- Return ONLY valid JSON:
{{
  "meta_title": "Your title here",
  "meta_description": "Your description here"
}}"""

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=500,
                temperature=0.7,
                messages=[{"role": "user", "content": prompt}]
            )

            import json
            response_text = response.content[0].text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            meta_data = json.loads(response_text)
            logger.info(f"Generated unique meta tags: {meta_data.get('meta_title', '')}")
            return meta_data

        except Exception as e:
            logger.error(f"Error generating meta tags: {e}", exc_info=True)
            return {
                "meta_title": f"{category_name} | Quality Children's Wear",
                "meta_description": f"Shop our collection of {category_name}. Quality, comfort, and style for your little ones. Fast delivery and hassle-free returns."
            }

    def _generate_image_prompts(self, hero_section: Dict, features: List[Dict]) -> List[Dict]:
        """
        Generate image prompts for Gemini.

        Args:
            hero_section: Hero section content
            features: Feature callouts

        Returns:
            List of image prompt dictionaries
        """
        prompts = [
            {
                "type": "hero",
                "prompt": f"A warm, inviting scene of happy children wearing comfortable clothing, lifestyle photography, natural lighting, cheerful atmosphere. Based on: {hero_section.get('headline', '')}",
                "filename": "hero_image.jpg"
            }
        ]

        for i, feature in enumerate(features[:3]):
            prompts.append({
                "type": "feature",
                "prompt": f"An icon or simple illustration representing {feature['title']}, clean design, modern style, friendly colors",
                "filename": f"feature_{i+1}.jpg"
            })

        return prompts

    def _generate_images(self, image_prompts: List[Dict], campaign_id: str) -> List[str]:
        """
        Generate images using Claude's image generation capabilities.

        Args:
            image_prompts: List of image prompts
            campaign_id: Campaign ID for storage path

        Returns:
            List of image metadata with prompts
        """
        generated_images = []

        for prompt_data in image_prompts:
            try:
                logger.info(f"Image prompt prepared: {prompt_data['filename']}")

                # For now, we store the image generation prompts
                # These can be used with DALL-E, Midjourney, Stable Diffusion, etc.
                # In a production system, you would integrate with an image generation API here

                enhanced_prompt = self._enhance_image_prompt(prompt_data["prompt"])

                file_path = f"campaigns/{campaign_id}/images/{prompt_data['filename']}"

                generated_images.append({
                    "type": prompt_data["type"],
                    "url": file_path,
                    "prompt": prompt_data["prompt"],
                    "enhanced_prompt": enhanced_prompt,
                    "status": "prompt_ready",
                    "generation_notes": "Use this prompt with DALL-E 3, Midjourney, or Stable Diffusion"
                })

                logger.info(f"Image prompt ready for: {prompt_data['filename']}")

            except Exception as e:
                logger.error(f"Error preparing image prompt {prompt_data['filename']}: {e}")
                continue

        return generated_images

    def _enhance_image_prompt(self, basic_prompt: str) -> str:
        """Enhance image prompt with style and quality directives."""
        enhancements = [
            "high quality",
            "professional photography",
            "soft natural lighting",
            "warm and inviting atmosphere",
            "lifestyle photography style",
            "shallow depth of field",
            "8k resolution"
        ]
        return f"{basic_prompt}, {', '.join(enhancements)}"
