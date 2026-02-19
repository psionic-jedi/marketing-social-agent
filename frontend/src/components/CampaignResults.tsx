import React, { useState, useEffect } from 'react';
import { CampaignResults as CampaignResultsType, campaignService } from '../services/api';
import './CampaignResults.css';

interface CampaignResultsProps {
  results: CampaignResultsType;
  onDelete?: () => void;
}

interface EmailPreview {
  subject: string;
  html: string;
}

interface GeneratedArticle {
  meta: {
    title: string;
    description: string;
    keywords: string[];
  };
  article: {
    headline: string;
    subheadline: string;
    introduction: string;
    sections: Array<{
      heading: string;
      content: string;
      subsections?: Array<{ heading: string; content: string }>;
    }>;
    key_takeaways: string[];
    conclusion: string;
    word_count: number;
  };
  faq?: Array<{ question: string; answer: string }>;
}

type TabType = 'overview' | 'research' | 'content' | 'social' | 'ppc' | 'meta' | 'crm' | 'analytics';

const CampaignResults: React.FC<CampaignResultsProps> = ({ results, onDelete }) => {
  const [activeTab, setActiveTab] = useState<TabType>('overview');
  const [emailPreview, setEmailPreview] = useState<EmailPreview | null>(null);
  const [collapsedSections, setCollapsedSections] = useState<Set<string>>(new Set());
  const [openAccordions, setOpenAccordions] = useState<Set<string>>(new Set(['primary-headlines', 'instagram', 'high-intent', 'core-audiences', 'welcome-series']));
  const [generatingArticle, setGeneratingArticle] = useState<string | null>(null);
  const [generatedArticles, setGeneratedArticles] = useState<Record<string, GeneratedArticle>>({});
  const [viewingArticleId, setViewingArticleId] = useState<string | null>(null);
  const [articleError, setArticleError] = useState<string | null>(null);

  // Load saved articles from the database on mount
  useEffect(() => {
    const loadSavedArticles = async () => {
      try {
        const saved = await campaignService.getArticles(results.campaign_id);
        if (saved && Object.keys(saved).length > 0) {
          const articlesMap: Record<string, GeneratedArticle> = {};
          for (const [ideaId, data] of Object.entries(saved)) {
            articlesMap[ideaId] = data.article;
          }
          setGeneratedArticles(articlesMap);
        }
      } catch (error) {
        console.error('Error loading saved articles:', error);
      }
    };

    if (results.campaign_id) {
      loadSavedArticles();
    }
  }, [results.campaign_id]);

  const handleGenerateArticle = async (idea: any) => {
    setGeneratingArticle(idea.id);
    setArticleError(null);

    try {
      const response = await campaignService.generateArticle(results.campaign_id, {
        content_idea_id: idea.id,
        title: idea.title,
        intro: idea.intro,
        type: idea.type,
        key_topics: idea.key_topics || [],
        target_audience: idea.target_audience || '',
        seo_keywords: idea.seo_keywords || []
      });

      if (response.success && response.article) {
        setGeneratedArticles(prev => ({ ...prev, [idea.id]: response.article }));
        setViewingArticleId(idea.id);
      } else {
        setArticleError('Failed to generate article');
      }
    } catch (error: any) {
      console.error('Error generating article:', error);
      setArticleError(error.response?.data?.detail || 'Failed to generate article');
    } finally {
      setGeneratingArticle(null);
    }
  };

  // Get currently viewing article
  const generatedArticle = viewingArticleId ? generatedArticles[viewingArticleId] : null;

  if (!results.results) {
    return (
      <div className="results-empty">
        <div className="status-badge-large status-running">
          <span className="status-pulse"></span>
          {results.status}
        </div>
        <p>Campaign is still processing. Results will appear here when complete.</p>
      </div>
    );
  }

  const { research_data, content_outputs, social_media_plan, ppc_campaign, meta_ads_campaign, crm_plan, analyst_insights } = results.results;

  const toggleSection = (sectionId: string) => {
    const newCollapsed = new Set(collapsedSections);
    if (newCollapsed.has(sectionId)) {
      newCollapsed.delete(sectionId);
    } else {
      newCollapsed.add(sectionId);
    }
    setCollapsedSections(newCollapsed);
  };

  const toggleAccordion = (accordionId: string) => {
    const newOpen = new Set(openAccordions);
    if (newOpen.has(accordionId)) {
      newOpen.delete(accordionId);
    } else {
      newOpen.add(accordionId);
    }
    setOpenAccordions(newOpen);
  };

  // Calculate summary stats
  const productCount = research_data?.products?.length || research_data?.category_insights?.total_products || 0;
  const brandCount = research_data?.category_insights?.common_features?.length || 0;
  const socialPostCount = (social_media_plan?.instagram?.posts?.length || 0) + (social_media_plan?.tiktok?.concepts?.length || 0);
  const keywordCount = ppc_campaign?.keywords?.high_intent?.length || 0 + (ppc_campaign?.keywords?.mid_intent?.length || 0);
  const adSetCount = meta_ads_campaign?.ad_sets?.length || 0;
  const emailCount = (crm_plan?.welcome_series?.length || 0) + (crm_plan?.promotional_campaigns?.length || 0) + (crm_plan?.cart_abandonment ? 1 : 0);

  const tabs: { id: TabType; label: string; icon: string }[] = [
    { id: 'overview', label: 'Overview', icon: '📋' },
    { id: 'research', label: 'Research', icon: '🔍' },
    { id: 'content', label: 'Content', icon: '✍️' },
    { id: 'social', label: 'Social Media', icon: '📱' },
    { id: 'ppc', label: 'Google Ads', icon: '🎯' },
    { id: 'meta', label: 'Meta Ads', icon: '📘' },
    { id: 'crm', label: 'Email & CRM', icon: '📧' },
    { id: 'analytics', label: 'Analytics', icon: '📊' },
  ];

  return (
    <div className="campaign-results-v2">
      {/* Header */}
      <header className="results-header-v2">
        <div className="header-info">
          <h1>{research_data?.category_insights?.category_name || 'Campaign Results'}</h1>
          <p className="header-url">{results.category_url}</p>
        </div>
        <div className="header-actions">
          <span className={`status-badge-large status-${results.status}`}>
            {results.status === 'completed' && '✓ '}
            {results.status}
          </span>
          {onDelete && (
            <button className="action-btn-v2" onClick={onDelete}>
              🗑️ Delete
            </button>
          )}
        </div>
      </header>

      {/* Quick Actions */}
      <div className="quick-actions-v2">
        <button className="action-btn-v2 primary">
          <span>📥</span> Export All
        </button>
        <button className="action-btn-v2">
          <span>📧</span> Download Emails
        </button>
        <button className="action-btn-v2">
          <span>📊</span> Export to CSV
        </button>
      </div>

      {/* Summary Cards */}
      <div className="summary-grid-v2">
        <div className="summary-card-v2">
          <h3>Products Found</h3>
          <div className="value">{productCount}</div>
          <div className="detail">From {brandCount} brands</div>
        </div>
        <div className="summary-card-v2 green">
          <h3>Content Pieces</h3>
          <div className="value">{content_outputs ? '8' : '0'}</div>
          <div className="detail">Headlines, descriptions</div>
        </div>
        <div className="summary-card-v2 blue">
          <h3>Social Posts</h3>
          <div className="value">{socialPostCount}</div>
          <div className="detail">Across platforms</div>
        </div>
        <div className="summary-card-v2 purple">
          <h3>PPC Keywords</h3>
          <div className="value">{keywordCount}</div>
          <div className="detail">By intent level</div>
        </div>
        <div className="summary-card-v2 orange">
          <h3>Meta Ad Sets</h3>
          <div className="value">{adSetCount}</div>
          <div className="detail">With copy variations</div>
        </div>
        <div className="summary-card-v2 pink">
          <h3>Email Templates</h3>
          <div className="value">{emailCount}</div>
          <div className="detail">Welcome, promo, cart</div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="tabs-v2">
        {tabs.map(tab => (
          <button
            key={tab.id}
            className={`tab-v2 ${activeTab === tab.id ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            <span className="icon">{tab.icon}</span>
            {tab.label}
          </button>
        ))}
      </div>

      {/* Tab Panels */}
      <div className="panels-container">
        {/* Overview Panel */}
        {activeTab === 'overview' && (
          <div className="panel-v2">
            {analyst_insights && (
              <div className="insight-callout-v2">
                <span className="icon">💡</span>
                <div>
                  <h4>Campaign Insight</h4>
                  <p>This campaign targets {research_data?.category_insights?.category_name || 'your audience'}.
                     Based on our analysis, {analyst_insights.key_recommendations?.[0] || 'focus on premium positioning for best results'}.</p>
                </div>
              </div>
            )}

            <div className={`section-card-v2 ${collapsedSections.has('recommendations') ? 'collapsed' : ''}`}>
              <div className="section-header-v2" onClick={() => toggleSection('recommendations')}>
                <h2><span>🎯</span> Key Recommendations</h2>
                <span className="toggle">▼</span>
              </div>
              {!collapsedSections.has('recommendations') && (
                <div className="section-content-v2">
                  <div className="data-grid-v2">
                    {analyst_insights?.optimization_recommendations?.slice(0, 3).map((rec: any, idx: number) => (
                      <div key={idx} className="data-card-v2">
                        <h4>{rec.channel || `Recommendation ${idx + 1}`}</h4>
                        <p>{rec.recommendation || rec}</p>
                        <div className="meta-tags">
                          <span>{rec.priority || 'High'} Priority</span>
                        </div>
                      </div>
                    )) || (
                      <>
                        <div className="data-card-v2">
                          <h4>Focus on Quality</h4>
                          <p>Emphasize premium materials and craftsmanship in all ad copy to resonate with target audience.</p>
                          <div className="meta-tags"><span>High Priority</span></div>
                        </div>
                        <div className="data-card-v2">
                          <h4>Leverage Social Proof</h4>
                          <p>Include customer reviews and ratings in marketing materials to build trust.</p>
                          <div className="meta-tags"><span>Medium Priority</span></div>
                        </div>
                      </>
                    )}
                  </div>
                </div>
              )}
            </div>

            {analyst_insights?.budget_allocation && (
              <div className={`section-card-v2 ${collapsedSections.has('budget') ? 'collapsed' : ''}`}>
                <div className="section-header-v2" onClick={() => toggleSection('budget')}>
                  <h2><span>💰</span> Budget Allocation</h2>
                  <span className="toggle">▼</span>
                </div>
                {!collapsedSections.has('budget') && (
                  <div className="section-content-v2">
                    <div className="budget-visual-v2">
                      <div className="budget-segment awareness" style={{ width: '25%' }}>25%</div>
                      <div className="budget-segment prospecting" style={{ width: '45%' }}>45%</div>
                      <div className="budget-segment retargeting" style={{ width: '30%' }}>30%</div>
                    </div>
                    <div className="budget-legend-v2">
                      <div className="legend-item"><div className="dot awareness"></div><span>Awareness</span></div>
                      <div className="legend-item"><div className="dot prospecting"></div><span>Prospecting</span></div>
                      <div className="legend-item"><div className="dot retargeting"></div><span>Retargeting</span></div>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Research Panel */}
        {activeTab === 'research' && research_data && (
          <div className="panel-v2">
            <div className={`section-card-v2 ${collapsedSections.has('products') ? 'collapsed' : ''}`}>
              <div className="section-header-v2" onClick={() => toggleSection('products')}>
                <h2><span>🛍️</span> Products Discovered <span className="badge">{productCount} items</span></h2>
                <span className="toggle">▼</span>
              </div>
              {!collapsedSections.has('products') && (
                <div className="section-content-v2">
                  <table className="data-table-v2">
                    <thead>
                      <tr>
                        <th>Product</th>
                        <th>Brand</th>
                        <th>Price</th>
                      </tr>
                    </thead>
                    <tbody>
                      {research_data.products?.slice(0, 5).map((product: any, idx: number) => (
                        <tr key={idx}>
                          <td className="primary">{product.name}</td>
                          <td>{product.brand || '-'}</td>
                          <td>£{product.price}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {research_data.category_insights && (
              <div className={`section-card-v2 ${collapsedSections.has('insights') ? 'collapsed' : ''}`}>
                <div className="section-header-v2" onClick={() => toggleSection('insights')}>
                  <h2><span>📈</span> Market Insights</h2>
                  <span className="toggle">▼</span>
                </div>
                {!collapsedSections.has('insights') && (
                  <div className="section-content-v2">
                    <div className="data-grid-v2">
                      <div className="data-card-v2">
                        <h4>Price Range</h4>
                        <p>£{research_data.category_insights.price_range?.min} - £{research_data.category_insights.price_range?.max}</p>
                        <p className="subtext">Average: £{research_data.category_insights.price_range?.avg?.toFixed(2)}</p>
                      </div>
                      <div className="data-card-v2">
                        <h4>Common Features</h4>
                        <div className="tag-list-v2">
                          {research_data.category_insights.common_features?.slice(0, 5).map((feature: string, idx: number) => (
                            <span key={idx} className="tag-v2">{feature}</span>
                          ))}
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Content Ideas Section */}
            {research_data.content_ideas && research_data.content_ideas.length > 0 && (
              <div className={`section-card-v2 ${collapsedSections.has('content-ideas') ? 'collapsed' : ''}`}>
                <div className="section-header-v2" onClick={() => toggleSection('content-ideas')}>
                  <h2><span>💡</span> Content & Article Ideas <span className="badge">{research_data.content_ideas.length} ideas</span></h2>
                  <span className="toggle">▼</span>
                </div>
                {!collapsedSections.has('content-ideas') && (
                  <div className="section-content-v2">
                    <p className="section-intro">
                      Based on the products and category analysis, here are tailored content ideas that would resonate with your target audience.
                      Click "Generate Article" to create a full SEO-optimised article.
                    </p>
                    <div className="content-ideas-grid">
                      {research_data.content_ideas.map((idea: any, idx: number) => (
                        <div key={idea.id || idx} className="content-idea-card">
                          <div className="idea-header">
                            <span className={`idea-type-badge ${idea.type}`}>{idea.type?.replace('_', ' ')}</span>
                            <span className="idea-audience">{idea.target_audience}</span>
                          </div>
                          <h3 className="idea-title">{idea.title}</h3>
                          <p className="idea-intro">{idea.intro}</p>
                          <div className="idea-topics">
                            <span className="topics-label">Key Topics:</span>
                            <div className="topic-tags">
                              {idea.key_topics?.slice(0, 4).map((topic: string, tidx: number) => (
                                <span key={tidx} className="topic-tag">{topic}</span>
                              ))}
                            </div>
                          </div>
                          {idea.why_this_matters && (
                            <p className="idea-rationale">
                              <span className="rationale-icon">💭</span>
                              {idea.why_this_matters}
                            </p>
                          )}
                          <div className="idea-footer">
                            <span className="word-count">~{idea.estimated_word_count || 1200} words</span>
                            <div className="idea-actions">
                              {generatedArticles[idea.id] && (
                                <button
                                  className="view-article-btn"
                                  onClick={() => setViewingArticleId(idea.id)}
                                >
                                  <span>📄</span>
                                  View Article
                                </button>
                              )}
                              <button
                                className={`generate-btn ${generatingArticle === idea.id ? 'loading' : ''}`}
                                onClick={() => handleGenerateArticle(idea)}
                                disabled={generatingArticle !== null}
                              >
                                {generatingArticle === idea.id ? (
                                  <>
                                    <span className="spinner"></span>
                                    Generating...
                                  </>
                                ) : generatedArticles[idea.id] ? (
                                  <>
                                    <span>🔄</span>
                                    Regenerate
                                  </>
                                ) : (
                                  <>
                                    <span>✨</span>
                                    Generate Article
                                  </>
                                )}
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                    {articleError && (
                      <div className="article-error">
                        <span>⚠️</span> {articleError}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Content Panel */}
        {activeTab === 'content' && content_outputs && (
          <div className="panel-v2">
            <div className={`section-card-v2 ${collapsedSections.has('headlines') ? 'collapsed' : ''}`}>
              <div className="section-header-v2" onClick={() => toggleSection('headlines')}>
                <h2><span>📝</span> Headlines & Taglines</h2>
                <span className="toggle">▼</span>
              </div>
              {!collapsedSections.has('headlines') && (
                <div className="section-content-v2">
                  {content_outputs.hero_section && (
                    <div className="hero-preview-v2">
                      <div className="hero-badge">Hero Section</div>
                      <h3>{content_outputs.hero_section.headline}</h3>
                      <p>{content_outputs.hero_section.subheadline}</p>
                      <button className="cta-preview">{content_outputs.hero_section.cta_text}</button>
                    </div>
                  )}

                  {content_outputs.meta_tags && (
                    <div className="accordion-v2">
                      <div className="accordion-header-v2" onClick={() => toggleAccordion('seo-tags')}>
                        <span>SEO Meta Tags</span>
                        <span className="arrow">{openAccordions.has('seo-tags') ? '▼' : '▶'}</span>
                      </div>
                      {openAccordions.has('seo-tags') && (
                        <div className="accordion-content-v2">
                          <div className="meta-item-v2">
                            <span className="label">Title:</span>
                            <code>{content_outputs.meta_tags.meta_title}</code>
                          </div>
                          <div className="meta-item-v2">
                            <span className="label">Description:</span>
                            <code>{content_outputs.meta_tags.meta_description}</code>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Social Media Panel */}
        {activeTab === 'social' && social_media_plan && (
          <div className="panel-v2">
            <div className={`section-card-v2 ${collapsedSections.has('social-calendar') ? 'collapsed' : ''}`}>
              <div className="section-header-v2" onClick={() => toggleSection('social-calendar')}>
                <h2><span>📱</span> Social Media Calendar <span className="badge">{socialPostCount} posts</span></h2>
                <span className="toggle">▼</span>
              </div>
              {!collapsedSections.has('social-calendar') && (
                <div className="section-content-v2">
                  {social_media_plan.instagram?.posts && (
                    <div className="accordion-v2">
                      <div className="accordion-header-v2" onClick={() => toggleAccordion('instagram')}>
                        <span>📸 Instagram ({social_media_plan.instagram.posts.length} posts)</span>
                        <span className="arrow">{openAccordions.has('instagram') ? '▼' : '▶'}</span>
                      </div>
                      {openAccordions.has('instagram') && (
                        <div className="accordion-content-v2">
                          <div className="data-grid-v2">
                            {social_media_plan.instagram.posts.slice(0, 3).map((post: any, idx: number) => (
                              <div key={idx} className="data-card-v2">
                                <h4>Post {idx + 1}</h4>
                                <p>{post.caption?.substring(0, 100)}...</p>
                                <div className="tag-list-v2">
                                  {post.hashtags?.slice(0, 3).map((tag: string, tagIdx: number) => (
                                    <span key={tagIdx} className="tag-v2">{tag}</span>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {social_media_plan.tiktok?.concepts && (
                    <div className="accordion-v2">
                      <div className="accordion-header-v2" onClick={() => toggleAccordion('tiktok')}>
                        <span>🎵 TikTok ({social_media_plan.tiktok.concepts.length} concepts)</span>
                        <span className="arrow">{openAccordions.has('tiktok') ? '▼' : '▶'}</span>
                      </div>
                      {openAccordions.has('tiktok') && (
                        <div className="accordion-content-v2">
                          <div className="data-grid-v2">
                            {social_media_plan.tiktok.concepts.slice(0, 3).map((concept: any, idx: number) => (
                              <div key={idx} className="data-card-v2">
                                <h4>{concept.hook}</h4>
                                <p>{concept.content_idea}</p>
                                <div className="tag-list-v2">
                                  {concept.hashtags?.slice(0, 3).map((tag: string, tagIdx: number) => (
                                    <span key={tagIdx} className="tag-v2">{tag}</span>
                                  ))}
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* PPC Panel */}
        {activeTab === 'ppc' && ppc_campaign && (
          <div className="panel-v2">
            {/* Campaign Types Section */}
            {ppc_campaign.campaign_types && (
              <div className={`section-card-v2 ${collapsedSections.has('campaign-types') ? 'collapsed' : ''}`}>
                <div className="section-header-v2" onClick={() => toggleSection('campaign-types')}>
                  <h2><span>🎯</span> Recommended Campaign Types</h2>
                  <span className="toggle">▼</span>
                </div>
                {!collapsedSections.has('campaign-types') && (
                  <div className="section-content-v2">
                    <div className="data-grid-v2">
                      {Object.entries(ppc_campaign.campaign_types).map(([key, campaign]: [string, any]) => (
                        <div key={key} className={`data-card-v2 ${campaign.recommended ? 'recommended' : 'not-recommended'}`}>
                          <div className="card-header-row">
                            <h4>{campaign.name}</h4>
                            <span className={`priority-badge ${campaign.priority?.toLowerCase()}`}>{campaign.priority}</span>
                          </div>
                          <p className="description">{campaign.description}</p>
                          <div className="campaign-stats">
                            <div className="stat-row">
                              <span className="label">Expected ROAS:</span>
                              <span className="value highlight">{campaign.expected_roas}</span>
                            </div>
                            <div className="stat-row">
                              <span className="label">Budget Allocation:</span>
                              <span className="value">{campaign.recommended_budget_percentage}%</span>
                            </div>
                            <div className="stat-row">
                              <span className="label">Time to Results:</span>
                              <span className="value">{campaign.time_to_results}</span>
                            </div>
                          </div>
                          <p className="best-for"><strong>Best for:</strong> {campaign.best_for}</p>
                          {!campaign.recommended && (
                            <div className="not-recommended-badge">Not recommended for current budget</div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* KPI Targets Section */}
            {ppc_campaign.kpi_targets && (
              <div className={`section-card-v2 ${collapsedSections.has('kpi-targets') ? 'collapsed' : ''}`}>
                <div className="section-header-v2" onClick={() => toggleSection('kpi-targets')}>
                  <h2><span>📈</span> KPI Targets & Profitability</h2>
                  <span className="toggle">▼</span>
                </div>
                {!collapsedSections.has('kpi-targets') && (
                  <div className="section-content-v2">
                    {/* Profitability Analysis */}
                    {ppc_campaign.kpi_targets.profitability_analysis && (
                      <div className="insight-callout-v2 profitability">
                        <span className="icon">💰</span>
                        <div>
                          <h4>Profitability Analysis</h4>
                          <p>{ppc_campaign.kpi_targets.profitability_analysis.explanation}</p>
                          <div className="kpi-highlight-row">
                            <div className="kpi-item">
                              <span className="kpi-label">Margin Tier</span>
                              <span className="kpi-value">{ppc_campaign.kpi_targets.profitability_analysis.margin_tier}</span>
                            </div>
                            <div className="kpi-item">
                              <span className="kpi-label">Gross Margin</span>
                              <span className="kpi-value">{ppc_campaign.kpi_targets.profitability_analysis.estimated_gross_margin}</span>
                            </div>
                            <div className="kpi-item warning">
                              <span className="kpi-label">Break-Even ROAS</span>
                              <span className="kpi-value">{ppc_campaign.kpi_targets.profitability_analysis.break_even_roas}x</span>
                            </div>
                            <div className="kpi-item success">
                              <span className="kpi-label">Target ROAS</span>
                              <span className="kpi-value">{ppc_campaign.kpi_targets.profitability_analysis.target_roas_for_profit}x</span>
                            </div>
                          </div>
                        </div>
                      </div>
                    )}

                    {/* ROAS Targets by Campaign Type */}
                    {ppc_campaign.kpi_targets.roas_targets?.by_campaign_type && (
                      <div className="accordion-v2">
                        <div className="accordion-header-v2" onClick={() => toggleAccordion('roas-targets')}>
                          <span>ROAS Targets by Campaign Type</span>
                          <span className="arrow">{openAccordions.has('roas-targets') ? '▼' : '▶'}</span>
                        </div>
                        {openAccordions.has('roas-targets') && (
                          <div className="accordion-content-v2">
                            <table className="data-table-v2">
                              <thead>
                                <tr>
                                  <th>Campaign Type</th>
                                  <th>Minimum ROAS</th>
                                  <th>Target ROAS</th>
                                </tr>
                              </thead>
                              <tbody>
                                {Object.entries(ppc_campaign.kpi_targets.roas_targets.by_campaign_type).map(([type, targets]: [string, any]) => (
                                  <tr key={type}>
                                    <td className="primary">{type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}</td>
                                    <td>{targets.minimum}x</td>
                                    <td className="highlight">{targets.target}x</td>
                                  </tr>
                                ))}
                              </tbody>
                            </table>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Efficiency Targets */}
                    {ppc_campaign.kpi_targets.efficiency_targets && (
                      <div className="accordion-v2">
                        <div className="accordion-header-v2" onClick={() => toggleAccordion('efficiency-targets')}>
                          <span>Efficiency Targets</span>
                          <span className="arrow">{openAccordions.has('efficiency-targets') ? '▼' : '▶'}</span>
                        </div>
                        {openAccordions.has('efficiency-targets') && (
                          <div className="accordion-content-v2">
                            <div className="kpi-grid">
                              <div className="kpi-box">
                                <span className="kpi-label">Target CPA</span>
                                <span className="kpi-value">£{ppc_campaign.kpi_targets.efficiency_targets.target_cpa}</span>
                              </div>
                              <div className="kpi-box">
                                <span className="kpi-label">Max CPA</span>
                                <span className="kpi-value warning">£{ppc_campaign.kpi_targets.efficiency_targets.maximum_cpa}</span>
                              </div>
                              <div className="kpi-box">
                                <span className="kpi-label">Target CPC</span>
                                <span className="kpi-value">£{ppc_campaign.kpi_targets.efficiency_targets.target_cpc}</span>
                              </div>
                              <div className="kpi-box">
                                <span className="kpi-label">Target CTR</span>
                                <span className="kpi-value">{ppc_campaign.kpi_targets.efficiency_targets.target_ctr}</span>
                              </div>
                              <div className="kpi-box">
                                <span className="kpi-label">Target CVR</span>
                                <span className="kpi-value">{ppc_campaign.kpi_targets.efficiency_targets.target_cvr}</span>
                              </div>
                              <div className="kpi-box">
                                <span className="kpi-label">Impression Share</span>
                                <span className="kpi-value">{ppc_campaign.kpi_targets.efficiency_targets.target_impression_share}</span>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}

                    {/* Revenue Targets */}
                    {ppc_campaign.kpi_targets.revenue_targets && (
                      <div className="accordion-v2">
                        <div className="accordion-header-v2" onClick={() => toggleAccordion('revenue-targets')}>
                          <span>Revenue & Profit Targets</span>
                          <span className="arrow">{openAccordions.has('revenue-targets') ? '▼' : '▶'}</span>
                        </div>
                        {openAccordions.has('revenue-targets') && (
                          <div className="accordion-content-v2">
                            <div className="kpi-grid large">
                              <div className="kpi-box">
                                <span className="kpi-label">Monthly Budget</span>
                                <span className="kpi-value">£{ppc_campaign.kpi_targets.revenue_targets.monthly_budget?.toLocaleString()}</span>
                              </div>
                              <div className="kpi-box success">
                                <span className="kpi-label">Target Revenue</span>
                                <span className="kpi-value">£{ppc_campaign.kpi_targets.revenue_targets.target_revenue?.toLocaleString()}</span>
                              </div>
                              <div className="kpi-box">
                                <span className="kpi-label">Target Orders</span>
                                <span className="kpi-value">{ppc_campaign.kpi_targets.revenue_targets.target_orders}</span>
                              </div>
                              <div className="kpi-box success">
                                <span className="kpi-label">Target Profit</span>
                                <span className="kpi-value">£{ppc_campaign.kpi_targets.revenue_targets.target_profit?.toLocaleString()}</span>
                              </div>
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Strategic Budget Allocation */}
            {ppc_campaign.strategic_allocation && (
              <div className={`section-card-v2 ${collapsedSections.has('budget-allocation') ? 'collapsed' : ''}`}>
                <div className="section-header-v2" onClick={() => toggleSection('budget-allocation')}>
                  <h2><span>💰</span> Strategic Budget Allocation</h2>
                  <span className="toggle">▼</span>
                </div>
                {!collapsedSections.has('budget-allocation') && (
                  <div className="section-content-v2">
                    {/* Phase Recommendation */}
                    {ppc_campaign.strategic_allocation.phase_recommendation && (
                      <div className="insight-callout-v2 phase">
                        <span className="icon">🚀</span>
                        <div>
                          <h4>Phase: {ppc_campaign.strategic_allocation.phase_recommendation.phase}</h4>
                          <p><strong>Focus:</strong> {ppc_campaign.strategic_allocation.phase_recommendation.focus}</p>
                          <p>{ppc_campaign.strategic_allocation.phase_recommendation.rationale}</p>
                          <p className="next-step"><strong>Next Step:</strong> {ppc_campaign.strategic_allocation.phase_recommendation.next_step}</p>
                        </div>
                      </div>
                    )}

                    {/* Campaign Mix */}
                    {ppc_campaign.strategic_allocation.campaign_mix && (
                      <div className="budget-allocation-visual">
                        <h4>Budget Distribution</h4>
                        <div className="budget-bars">
                          {ppc_campaign.strategic_allocation.campaign_mix.map((item: any, idx: number) => (
                            <div key={idx} className="budget-bar-item">
                              <div className="bar-label">
                                <span>{item.campaign_type}</span>
                                <span className="percentage">{item.percentage}%</span>
                              </div>
                              <div className="bar-container">
                                <div
                                  className={`bar-fill priority-${item.priority?.toLowerCase()}`}
                                  style={{ width: `${item.percentage}%` }}
                                ></div>
                              </div>
                              <div className="bar-details">
                                <span>£{item.monthly_budget?.toLocaleString()}/mo</span>
                                <span>ROAS: {item.expected_roas}</span>
                              </div>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Scaling Rules */}
                    {ppc_campaign.strategic_allocation.scaling_rules && (
                      <div className="accordion-v2">
                        <div className="accordion-header-v2" onClick={() => toggleAccordion('scaling-rules')}>
                          <span>Scaling Rules</span>
                          <span className="arrow">{openAccordions.has('scaling-rules') ? '▼' : '▶'}</span>
                        </div>
                        {openAccordions.has('scaling-rules') && (
                          <div className="accordion-content-v2">
                            <div className="rules-list">
                              {ppc_campaign.strategic_allocation.scaling_rules.map((rule: any, idx: number) => (
                                <div key={idx} className="rule-item">
                                  <div className="rule-trigger">
                                    <span className="icon">⚡</span>
                                    <span>{rule.trigger}</span>
                                  </div>
                                  <div className="rule-action">
                                    <span className="label">Action:</span> {rule.action}
                                  </div>
                                  <div className="rule-focus">
                                    <span className="label">Focus:</span> {rule.focus}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>
                        )}
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}

            {/* Ad Groups */}
            {ppc_campaign.ad_groups && (
              <div className={`section-card-v2 ${collapsedSections.has('ad-groups') ? 'collapsed' : ''}`}>
                <div className="section-header-v2" onClick={() => toggleSection('ad-groups')}>
                  <h2><span>📂</span> Ad Groups <span className="badge">{ppc_campaign.ad_groups.length} groups</span></h2>
                  <span className="toggle">▼</span>
                </div>
                {!collapsedSections.has('ad-groups') && (
                  <div className="section-content-v2">
                    <div className="data-grid-v2">
                      {ppc_campaign.ad_groups.slice(0, 6).map((group: any, idx: number) => (
                        <div key={idx} className="data-card-v2">
                          <div className="card-header-row">
                            <h4>{group.ad_group_name}</h4>
                            <span className={`priority-badge ${group.priority?.toLowerCase()}`}>{group.priority}</span>
                          </div>
                          <div className="stat-row">
                            <span className="label">Theme:</span>
                            <span className="tag-v2">{group.theme}</span>
                          </div>
                          <div className="stat-row">
                            <span className="label">Max CPC:</span>
                            <span className="value">£{group.max_cpc}</span>
                          </div>
                          <div className="stat-row">
                            <span className="label">Daily Budget:</span>
                            <span className="value">£{group.recommended_daily_budget}</span>
                          </div>
                          <div className="keywords-preview">
                            {group.keywords?.slice(0, 3).map((kw: string, kwIdx: number) => (
                              <span key={kwIdx} className="keyword-tag">{kw}</span>
                            ))}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {ppc_campaign.ads && (
              <div className={`section-card-v2 ${collapsedSections.has('ad-copy') ? 'collapsed' : ''}`}>
                <div className="section-header-v2" onClick={() => toggleSection('ad-copy')}>
                  <h2><span>📝</span> Ad Copy <span className="badge">{ppc_campaign.ads.length} variations</span></h2>
                  <span className="toggle">▼</span>
                </div>
                {!collapsedSections.has('ad-copy') && (
                  <div className="section-content-v2">
                    <div className="data-grid-v2">
                      {ppc_campaign.ads.slice(0, 6).map((ad: any, idx: number) => (
                        <div key={idx} className="data-card-v2">
                          <span className="badge-inline">{ad.ad_group}</span>
                          <h4>{ad.headlines?.[0]}</h4>
                          <p>{ad.descriptions?.[0]}</p>
                          <div className="headlines-list">
                            {ad.headlines?.slice(1, 4).map((headline: string, hIdx: number) => (
                              <span key={hIdx} className="headline-tag">{headline}</span>
                            ))}
                          </div>
                          <div className="meta-item-v2">
                            <span className="label">Display URL:</span>
                            <code>{ad.display_url}</code>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Meta Ads Panel */}
        {activeTab === 'meta' && meta_ads_campaign && (
          <div className="panel-v2">
            <div className={`section-card-v2 ${collapsedSections.has('audiences') ? 'collapsed' : ''}`}>
              <div className="section-header-v2" onClick={() => toggleSection('audiences')}>
                <h2><span>👥</span> Audience Targeting</h2>
                <span className="toggle">▼</span>
              </div>
              {!collapsedSections.has('audiences') && (
                <div className="section-content-v2">
                  {meta_ads_campaign.audiences?.core_audiences && (
                    <div className="accordion-v2">
                      <div className="accordion-header-v2" onClick={() => toggleAccordion('core-audiences')}>
                        <span>Core Audiences ({meta_ads_campaign.audiences.core_audiences.length})</span>
                        <span className="arrow">{openAccordions.has('core-audiences') ? '▼' : '▶'}</span>
                      </div>
                      {openAccordions.has('core-audiences') && (
                        <div className="accordion-content-v2">
                          <div className="data-grid-v2">
                            {meta_ads_campaign.audiences.core_audiences.slice(0, 3).map((audience: any, idx: number) => (
                              <div key={idx} className="data-card-v2">
                                <span className="badge-inline">{audience.priority} Priority</span>
                                <h4>{audience.name}</h4>
                                <p>Age: {audience.targeting?.age_range || 'All'}</p>
                                <p className="subtext">Est. reach: {audience.estimated_reach}</p>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}

                  {meta_ads_campaign.audiences?.lookalike_audiences && (
                    <div className="accordion-v2">
                      <div className="accordion-header-v2" onClick={() => toggleAccordion('lookalike')}>
                        <span>Lookalike Audiences ({meta_ads_campaign.audiences.lookalike_audiences.length})</span>
                        <span className="arrow">{openAccordions.has('lookalike') ? '▼' : '▶'}</span>
                      </div>
                      {openAccordions.has('lookalike') && (
                        <div className="accordion-content-v2">
                          <div className="data-grid-v2">
                            {meta_ads_campaign.audiences.lookalike_audiences.map((audience: any, idx: number) => (
                              <div key={idx} className="data-card-v2">
                                <h4>{audience.name}</h4>
                                <p>{audience.description}</p>
                                <div className="tag-list-v2">
                                  <span className="tag-v2">{audience.percentage}</span>
                                  <span className="tag-v2">{audience.country}</span>
                                </div>
                              </div>
                            ))}
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            {meta_ads_campaign.ad_creatives && (
              <div className={`section-card-v2 ${collapsedSections.has('creatives') ? 'collapsed' : ''}`}>
                <div className="section-header-v2" onClick={() => toggleSection('creatives')}>
                  <h2><span>🎨</span> Ad Creatives <span className="badge">{meta_ads_campaign.ad_creatives.length} formats</span></h2>
                  <span className="toggle">▼</span>
                </div>
                {!collapsedSections.has('creatives') && (
                  <div className="section-content-v2">
                    <div className="ad-preview-grid-v2">
                      {meta_ads_campaign.ad_creatives.slice(0, 3).map((creative: any, idx: number) => (
                        <div key={idx} className="ad-preview-v2">
                          <div className="ad-image" style={{
                            background: idx === 0 ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' :
                                        idx === 1 ? 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' :
                                        'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)'
                          }}>
                            {creative.format}
                          </div>
                          <div className="ad-content">
                            <h4>{creative.name}</h4>
                            <p>{creative.recommended_for}</p>
                            <span className="cta-btn">Learn More</span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}

            {meta_ads_campaign.ad_copy?.variations && (
              <div className={`section-card-v2 ${collapsedSections.has('meta-copy') ? 'collapsed' : ''}`}>
                <div className="section-header-v2" onClick={() => toggleSection('meta-copy')}>
                  <h2><span>✍️</span> Ad Copy Variations <span className="badge">{meta_ads_campaign.ad_copy.variations.length}</span></h2>
                  <span className="toggle">▼</span>
                </div>
                {!collapsedSections.has('meta-copy') && (
                  <div className="section-content-v2">
                    <table className="data-table-v2">
                      <thead>
                        <tr>
                          <th>Style</th>
                          <th>Primary Text</th>
                          <th>CTA</th>
                        </tr>
                      </thead>
                      <tbody>
                        {meta_ads_campaign.ad_copy.variations.map((variation: any, idx: number) => (
                          <tr key={idx}>
                            <td><span className={`tag-v2 ${variation.tone}`}>{variation.tone}</span></td>
                            <td className="primary">{variation.primary_text?.substring(0, 80)}...</td>
                            <td>{variation.cta_button}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* CRM Panel */}
        {activeTab === 'crm' && crm_plan && (
          <div className="panel-v2">
            <div className={`section-card-v2 ${collapsedSections.has('emails') ? 'collapsed' : ''}`}>
              <div className="section-header-v2" onClick={() => toggleSection('emails')}>
                <h2><span>📧</span> Email Templates <span className="badge">{emailCount} emails</span></h2>
                <span className="toggle">▼</span>
              </div>
              {!collapsedSections.has('emails') && (
                <div className="section-content-v2">
                  {crm_plan.welcome_series && (
                    <div className="accordion-v2">
                      <div className="accordion-header-v2" onClick={() => toggleAccordion('welcome-series')}>
                        <span>Welcome Series ({crm_plan.welcome_series.length} emails)</span>
                        <span className="arrow">{openAccordions.has('welcome-series') ? '▼' : '▶'}</span>
                      </div>
                      {openAccordions.has('welcome-series') && (
                        <div className="accordion-content-v2">
                          {crm_plan.welcome_series.slice(0, 3).map((email: any, idx: number) => (
                            <div key={idx} className="email-preview-card-v2">
                              <div className="email-header-v2">
                                <strong>{email.subject_line || email.subject}</strong>
                                <span>{email.send_timing}</span>
                              </div>
                              <div className="email-body-v2">
                                <p>{email.preheader || email.preview_text}</p>
                              </div>
                              {email.html_template && (
                                <button
                                  className="preview-btn-v2"
                                  onClick={() => setEmailPreview({
                                    subject: email.subject_line || email.subject,
                                    html: email.html_template
                                  })}
                                >
                                  👁️ Preview Email
                                </button>
                              )}
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  )}

                  {crm_plan.cart_abandonment && (
                    <div className="accordion-v2">
                      <div className="accordion-header-v2" onClick={() => toggleAccordion('cart-abandonment')}>
                        <span>Cart Abandonment (1 email)</span>
                        <span className="arrow">{openAccordions.has('cart-abandonment') ? '▼' : '▶'}</span>
                      </div>
                      {openAccordions.has('cart-abandonment') && (
                        <div className="accordion-content-v2">
                          <div className="email-preview-card-v2">
                            <div className="email-header-v2">
                              <strong>{crm_plan.cart_abandonment.subject}</strong>
                            </div>
                            <div className="email-body-v2">
                              <p>{crm_plan.cart_abandonment.preview_text}</p>
                            </div>
                          </div>
                        </div>
                      )}
                    </div>
                  )}
                </div>
              )}
            </div>

            {crm_plan.segmentation_strategy?.segments && (
              <div className={`section-card-v2 ${collapsedSections.has('segments') ? 'collapsed' : ''}`}>
                <div className="section-header-v2" onClick={() => toggleSection('segments')}>
                  <h2><span>👥</span> Customer Segments <span className="badge">{crm_plan.segmentation_strategy.segments.length}</span></h2>
                  <span className="toggle">▼</span>
                </div>
                {!collapsedSections.has('segments') && (
                  <div className="section-content-v2">
                    <div className="data-grid-v2">
                      {crm_plan.segmentation_strategy.segments.map((segment: any, idx: number) => (
                        <div key={idx} className="data-card-v2">
                          <h4>{segment.name}</h4>
                          <p>{segment.criteria}</p>
                          <div className="progress-bar-v2">
                            <div className="fill" style={{ width: `${(idx + 1) * 25}%` }}></div>
                          </div>
                          <p className="subtext">~{(idx + 1) * 15}% of database</p>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {/* Analytics Panel */}
        {activeTab === 'analytics' && analyst_insights && (
          <div className="panel-v2">
            {analyst_insights.performance_predictions && (
              <div className={`section-card-v2 ${collapsedSections.has('predictions') ? 'collapsed' : ''}`}>
                <div className="section-header-v2" onClick={() => toggleSection('predictions')}>
                  <h2><span>📊</span> Performance Projections</h2>
                  <span className="toggle">▼</span>
                </div>
                {!collapsedSections.has('predictions') && (
                  <div className="section-content-v2">
                    <table className="data-table-v2">
                      <thead>
                        <tr>
                          <th>Metric</th>
                          <th>Conservative</th>
                          <th>Expected</th>
                          <th>Optimistic</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(analyst_insights.performance_predictions).slice(0, 4).map(([metric, predictions]: [string, any], idx: number) => (
                          <tr key={idx}>
                            <td className="primary">{metric.replace(/_/g, ' ')}</td>
                            <td>{predictions.conservative || '-'}</td>
                            <td className="highlight">{predictions.expected || predictions.target || '-'}</td>
                            <td>{predictions.optimistic || '-'}</td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                )}
              </div>
            )}

            {analyst_insights.risk_analysis && (
              <div className={`section-card-v2 ${collapsedSections.has('risks') ? 'collapsed' : ''}`}>
                <div className="section-header-v2" onClick={() => toggleSection('risks')}>
                  <h2><span>⚠️</span> Risk Analysis</h2>
                  <span className="toggle">▼</span>
                </div>
                {!collapsedSections.has('risks') && (
                  <div className="section-content-v2">
                    <div className="data-grid-v2">
                      {analyst_insights.risk_analysis.risks?.slice(0, 3).map((risk: any, idx: number) => (
                        <div key={idx} className="data-card-v2">
                          <h4>{risk.risk || risk.category}</h4>
                          <p>{risk.mitigation || risk.description}</p>
                          <div className="meta-tags">
                            <span className={`tag-v2 ${risk.level?.toLowerCase() || 'medium'}`}>
                              {risk.level || 'Medium'}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      {/* Email Preview Modal */}
      {emailPreview && (
        <div className="modal-overlay-v2" onClick={() => setEmailPreview(null)}>
          <div className="modal-content-v2" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-v2">
              <h3>📧 {emailPreview.subject}</h3>
              <button className="close-btn-v2" onClick={() => setEmailPreview(null)}>✕</button>
            </div>
            <div className="modal-body-v2">
              <iframe
                srcDoc={emailPreview.html}
                title="Email Preview"
                sandbox="allow-same-origin"
              />
            </div>
            <div className="modal-footer-v2">
              <button
                className="action-btn-v2"
                onClick={() => {
                  navigator.clipboard.writeText(emailPreview.html);
                  alert('HTML copied to clipboard!');
                }}
              >
                📋 Copy HTML
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Generated Article Modal */}
      {generatedArticle && (
        <div className="modal-overlay-v2 article-modal" onClick={() => setViewingArticleId(null)}>
          <div className="modal-content-v2 article-modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header-v2">
              <h3>📝 Generated Article</h3>
              <button className="close-btn-v2" onClick={() => setViewingArticleId(null)}>✕</button>
            </div>
            <div className="modal-body-v2 article-body">
              {/* Meta Section */}
              <div className="article-meta-section">
                <h4>SEO Meta Tags</h4>
                <div className="meta-item-v2">
                  <span className="label">Title:</span>
                  <code>{generatedArticle.meta?.title}</code>
                </div>
                <div className="meta-item-v2">
                  <span className="label">Description:</span>
                  <code>{generatedArticle.meta?.description}</code>
                </div>
                <div className="meta-item-v2">
                  <span className="label">Keywords:</span>
                  <div className="tag-list-v2">
                    {generatedArticle.meta?.keywords?.map((kw: string, idx: number) => (
                      <span key={idx} className="tag-v2">{kw}</span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Article Content */}
              <div className="article-content-section">
                <h1 className="article-headline">{generatedArticle.article?.headline}</h1>
                {generatedArticle.article?.subheadline && (
                  <p className="article-subheadline">{generatedArticle.article.subheadline}</p>
                )}

                <div className="article-intro">
                  {generatedArticle.article?.introduction}
                </div>

                {generatedArticle.article?.sections?.map((section: any, idx: number) => (
                  <div key={idx} className="article-section">
                    <h2>{section.heading}</h2>
                    <p>{section.content}</p>
                    {section.subsections?.map((sub: any, subIdx: number) => (
                      <div key={subIdx} className="article-subsection">
                        <h3>{sub.heading}</h3>
                        <p>{sub.content}</p>
                      </div>
                    ))}
                  </div>
                ))}

                {generatedArticle.article?.key_takeaways && generatedArticle.article.key_takeaways.length > 0 && (
                  <div className="article-takeaways">
                    <h2>Key Takeaways</h2>
                    <ul>
                      {generatedArticle.article.key_takeaways.map((takeaway: string, idx: number) => (
                        <li key={idx}>{takeaway}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {generatedArticle.article?.conclusion && (
                  <div className="article-conclusion">
                    <p>{generatedArticle.article.conclusion}</p>
                  </div>
                )}
              </div>

              {/* FAQ Section */}
              {generatedArticle.faq && generatedArticle.faq.length > 0 && (
                <div className="article-faq-section">
                  <h2>Frequently Asked Questions</h2>
                  {generatedArticle.faq.map((faq: any, idx: number) => (
                    <div key={idx} className="faq-item">
                      <h4>{faq.question}</h4>
                      <p>{faq.answer}</p>
                    </div>
                  ))}
                </div>
              )}

              <div className="article-word-count">
                <span>Word count: ~{generatedArticle.article?.word_count || 'N/A'}</span>
              </div>
            </div>
            <div className="modal-footer-v2">
              <button
                className="action-btn-v2"
                onClick={() => {
                  const articleText = `# ${generatedArticle.article?.headline}\n\n${generatedArticle.article?.introduction}\n\n${generatedArticle.article?.sections?.map((s: any) => `## ${s.heading}\n\n${s.content}`).join('\n\n')}\n\n## Key Takeaways\n\n${generatedArticle.article?.key_takeaways?.map((t: string) => `- ${t}`).join('\n')}\n\n${generatedArticle.article?.conclusion}`;
                  navigator.clipboard.writeText(articleText);
                  alert('Article copied to clipboard as Markdown!');
                }}
              >
                📋 Copy as Markdown
              </button>
              <button
                className="action-btn-v2"
                onClick={() => {
                  navigator.clipboard.writeText(JSON.stringify(generatedArticle, null, 2));
                  alert('Full JSON copied to clipboard!');
                }}
              >
                📦 Copy JSON
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CampaignResults;
