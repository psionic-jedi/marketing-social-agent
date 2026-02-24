"""
Social Media Agent - Creates social media content plan and posts.

Responsibilities:
1. Generate Instagram posts with captions and hashtags
2. Generate Facebook posts
3. Generate TikTok video concepts
4. Create posting schedule
5. Recommend influencer collaboration opportunities
"""
import logging
from typing import Dict, List
from datetime import datetime, timedelta
from anthropic import Anthropic

from app.core.config import settings
from app.agents.state import MarketingCampaignState

logger = logging.getLogger(__name__)


class SocialMediaAgent:
    """Social media agent for creating social media content and strategy."""

    def __init__(self, cost_tracker=None):
        self.anthropic = Anthropic(api_key=settings.anthropic_api_key)
        self.cost_tracker = cost_tracker

    def execute(self, state: MarketingCampaignState) -> MarketingCampaignState:
        """
        Execute the social media agent workflow.

        Args:
            state: Current campaign state with research_data and content_outputs

        Returns:
            Updated state with social_media_plan
        """
        logger.info(f"Social Media Agent starting for campaign {state['campaign_id']}")

        state["current_step"] = "social_media"
        state["progress_percentage"] = 65

        try:
            research_data = state.get("research_data")
            content_outputs = state.get("content_outputs")

            if not research_data or not content_outputs:
                raise ValueError("Missing research data or content outputs")

            category_name = research_data.get("category_insights", {}).get("category_name", "Products")

            # Generate social media content
            logger.info("Generating Instagram posts")
            instagram_posts = self._generate_instagram_posts(research_data, content_outputs)

            logger.info("Generating Facebook posts")
            facebook_posts = self._generate_facebook_posts(research_data, content_outputs)

            logger.info("Generating TikTok video concepts")
            tiktok_concepts = self._generate_tiktok_concepts(research_data)

            logger.info("Creating posting schedule")
            posting_schedule = self._create_posting_schedule(
                len(instagram_posts) + len(facebook_posts) + len(tiktok_concepts)
            )

            logger.info("Generating hashtag strategy")
            hashtag_strategy = self._generate_hashtag_strategy(research_data)

            # Compile social media plan
            social_media_plan = {
                "instagram": {
                    "posts": instagram_posts,
                    "posting_frequency": "3-4 times per week"
                },
                "facebook": {
                    "posts": facebook_posts,
                    "posting_frequency": "2-3 times per week"
                },
                "tiktok": {
                    "concepts": tiktok_concepts,
                    "posting_frequency": "2-3 times per week"
                },
                "posting_schedule": posting_schedule,
                "hashtag_strategy": hashtag_strategy,
                "influencer_recommendations": self._generate_influencer_recommendations(category_name)
            }

            state["social_media_plan"] = social_media_plan
            state["progress_percentage"] = 70
            logger.info("Social Media Agent completed successfully")

            return state

        except Exception as e:
            error_msg = f"Social Media Agent failed: {str(e)}"
            logger.error(error_msg, exc_info=True)
            state["errors"].append(error_msg)
            state["progress_percentage"] = 70
            return state

    def _generate_instagram_posts(self, research_data: Dict, content_outputs: Dict) -> List[Dict]:
        """Generate 5-7 Instagram post concepts with captions and hashtags."""
        category_name = research_data.get("category_insights", {}).get("category_name", "Products")
        features = content_outputs.get("features", [])
        products = research_data.get("products", [])
        parent_questions = research_data.get("parent_questions", [])

        prompt = f"""Create 5 engaging Instagram post concepts for {category_name}.

Context:
- Category: {category_name}
- Products: {len(products)} items
- Key features: {', '.join([f['title'] for f in features[:3]])}
- Parent concerns: {', '.join([q.get('question', '') for q in parent_questions[:2]])}

For EACH of the 5 posts, provide:
1. Concept - What the visual shows (lifestyle photo, flat lay, etc.)
2. Caption - Engaging text (100-150 chars with emojis)
3. Hashtags - 5-8 relevant hashtags (array)
4. Best posting time - e.g., "7-9 AM" or "7-9 PM"

Make posts visually appealing, authentic, parent-friendly, and varied in style.

IMPORTANT: Return ONLY valid JSON:
{{
  "posts": [
    {{
      "post_number": 1,
      "concept": "description of visual",
      "caption": "engaging caption with emojis",
      "hashtags": ["#hashtag1", "#hashtag2"],
      "best_time": "7-9 AM"
    }}
  ]
}}"""

        try:
            response = self.anthropic.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=3000,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )

            if self.cost_tracker:
                self.cost_tracker.record(response, "social_media", "instagram_posts")

            import json
            response_text = response.content[0].text.strip()
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]
                response_text = response_text.strip()

            post_data = json.loads(response_text)
            posts = post_data.get("posts", [])
            logger.info(f"Generated {len(posts)} unique Instagram posts")
            return posts

        except Exception as e:
            logger.error(f"Error generating Instagram posts: {e}", exc_info=True)
            return self._get_fallback_instagram_posts(category_name)

    def _generate_facebook_posts(self, research_data: Dict, content_outputs: Dict) -> List[Dict]:
        """Generate 3-5 Facebook post concepts."""
        category_name = research_data.get("category_insights", {}).get("category_name", "Products")
        parent_questions = research_data.get("parent_questions", [])

        posts = []
        for i, question in enumerate(parent_questions[:3]):
            posts.append({
                "post_number": i + 1,
                "post_type": "Educational",
                "headline": question.get("question", f"What parents ask about {category_name}"),
                "content": f"Many parents ask: '{question.get('question', '')}' Here's what you need to know...",
                "cta": "Read More",
                "best_time": "10 AM - 2 PM"
            })

        # Add promotional posts
        posts.append({
            "post_number": len(posts) + 1,
            "post_type": "Promotional",
            "headline": f"Discover Our {category_name} Collection",
            "content": content_outputs.get("category_description", "")[:200],
            "cta": "Shop Now",
            "best_time": "6-8 PM"
        })

        return posts

    def _generate_tiktok_concepts(self, research_data: Dict) -> List[Dict]:
        """Generate 3-4 TikTok video concepts."""
        category_name = research_data.get("category_insights", {}).get("category_name", "Products")

        concepts = [
            {
                "concept_number": 1,
                "hook": "POV: You just discovered the perfect baby sleepsuit",
                "content_idea": "Quick unboxing showing features and quality",
                "duration": "15-30 seconds",
                "music_suggestion": "Trending upbeat sound",
                "hashtags": ["#babyhacks", "#parentingtips", "#newmom"]
            },
            {
                "concept_number": 2,
                "hook": "3 things to look for when buying baby sleepsuits",
                "content_idea": "Educational listicle format",
                "duration": "30-45 seconds",
                "music_suggestion": "Lo-fi beats",
                "hashtags": ["#parentinghacks", "#babymusthaves"]
            },
            {
                "concept_number": 3,
                "hook": "The difference is REAL",
                "content_idea": "Before/after showing quality difference",
                "duration": "15-20 seconds",
                "music_suggestion": "Dramatic reveal sound",
                "hashtags": ["#qualitymatters", "#smartshopping"]
            }
        ]

        return concepts

    def _create_posting_schedule(self, total_posts: int) -> List[Dict]:
        """Create a 2-week posting schedule."""
        schedule = []
        start_date = datetime.now()

        platforms = ["Instagram", "Facebook", "TikTok"]
        for i in range(min(14, total_posts)):
            post_date = start_date + timedelta(days=i)
            schedule.append({
                "date": post_date.strftime("%Y-%m-%d"),
                "day": post_date.strftime("%A"),
                "platform": platforms[i % 3],
                "time": "7:00 PM" if i % 2 == 0 else "12:00 PM",
                "post_type": "Content" if i % 3 != 2 else "Engagement"
            })

        return schedule

    def _generate_hashtag_strategy(self, research_data: Dict) -> Dict:
        """Generate hashtag strategy."""
        category_name = research_data.get("category_insights", {}).get("category_name", "Products")

        return {
            "branded_hashtags": [
                f"#{category_name.replace(' ', '')}",
                "#QualityKidswear",
                "#ShopWithUs"
            ],
            "popular_hashtags": [
                "#parentinglife",
                "#babyfashion",
                "#newparents",
                "#babyessentials",
                "#parenthood"
            ],
            "niche_hashtags": [
                "#organicbabyclothes",
                "#sustainablekids",
                "#parentingtips",
                "#babylove"
            ],
            "strategy_notes": "Use 15-20 hashtags on Instagram, 3-5 on Facebook, 3-4 on TikTok"
        }

    def _generate_influencer_recommendations(self, category_name: str) -> List[Dict]:
        """Generate influencer collaboration recommendations."""
        return [
            {
                "type": "Micro-influencers",
                "follower_range": "10K-50K",
                "focus": "Parenting and lifestyle",
                "engagement_rate": "3-8%",
                "collaboration_idea": "Product reviews and honest testimonials"
            },
            {
                "type": "Nano-influencers",
                "follower_range": "1K-10K",
                "focus": "Local parent communities",
                "engagement_rate": "8-15%",
                "collaboration_idea": "Authentic user-generated content"
            },
            {
                "type": "Parent bloggers",
                "follower_range": "Varies",
                "focus": "Written content and SEO",
                "engagement_rate": "N/A",
                "collaboration_idea": "Detailed product features and gift guides"
            }
        ]

    def _get_fallback_instagram_posts(self, category_name: str) -> List[Dict]:
        """Fallback Instagram posts if AI generation fails."""
        return [
            {
                "post_number": 1,
                "concept": "Lifestyle product shot",
                "caption": f"Quality {category_name} for your little ones ✨",
                "description": "Comfort, style, and quality combined",
                "cta": "Shop Now",
                "best_time": "7-9 PM"
            }
        ]
