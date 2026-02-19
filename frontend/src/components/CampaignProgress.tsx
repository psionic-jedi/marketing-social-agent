import React, { useEffect, useState } from 'react';
import { Campaign, campaignService } from '../services/api';
import './CampaignProgress.css';

interface CampaignProgressProps {
  campaignId: string;
  onComplete: () => void;
}

// Map research sub-steps to human-readable descriptions
function getResearchSubStepDescription(currentStep: string): string {
  if (!currentStep) return 'Starting research...';

  if (currentStep.includes('scraping_page')) return 'Scraping category page...';
  if (currentStep.includes('parsing_products')) return 'Parsing product listings...';
  if (currentStep.includes('pagination')) {
    const match = currentStep.match(/\((.+?)\)/);
    return match ? `Searching for more products (${match[1]})...` : 'Paginating for more products...';
  }
  if (currentStep.includes('deep_scraping')) {
    const match = currentStep.match(/\((\d+)\/(\d+)\)/);
    if (match) return `Deep scraping product ${match[1]} of ${match[2]}...`;
    return 'Deep scraping product pages...';
  }
  if (currentStep.includes('analysing_products')) return 'Analysing products with AI...';
  if (currentStep.includes('parent_questions')) return 'Researching common parent questions...';
  if (currentStep.includes('seo_research')) return 'Conducting SEO keyword research...';
  if (currentStep.includes('content_ideas')) return 'Brainstorming content ideas...';

  return 'Analysing category and products...';
}

// Get the main step from current_step (e.g., 'research:deep_scraping (3/45)' -> 'research')
function getMainStep(currentStep: string | null): string {
  if (!currentStep) return '';
  return currentStep.split(':')[0];
}

const AGENT_STEPS = [
  { key: 'research', name: 'Research Agent', description: 'Analysing category and products' },
  { key: 'content', name: 'Content Agent', description: 'Generating marketing copy' },
  { key: 'social_media', name: 'Social Media Agent', description: 'Creating social media strategy' },
  { key: 'ppc', name: 'PPC Agent', description: 'Building Google Ads campaign' },
  { key: 'meta_ads', name: 'Meta Ads Agent', description: 'Creating Facebook & Instagram ads' },
  { key: 'crm', name: 'CRM Agent', description: 'Designing email campaigns' },
  { key: 'analyst', name: 'Analyst Agent', description: 'Generating insights and recommendations' },
];

const CampaignProgress: React.FC<CampaignProgressProps> = ({ campaignId, onComplete }) => {
  const [campaign, setCampaign] = useState<Campaign | null>(null);
  const [isPolling, setIsPolling] = useState(true);

  useEffect(() => {
    let pollInterval: NodeJS.Timeout;

    const pollCampaign = async () => {
      try {
        const data = await campaignService.getCampaign(campaignId);
        setCampaign(data);

        // Stop polling if campaign is completed, failed, or partial
        if (['completed', 'failed', 'partial'].includes(data.status)) {
          setIsPolling(false);
          onComplete();
        }
      } catch (error) {
        console.error('Error polling campaign:', error);
      }
    };

    // Initial poll
    pollCampaign();

    // Set up polling interval (every 2 seconds)
    if (isPolling) {
      pollInterval = setInterval(pollCampaign, 2000);
    }

    return () => {
      if (pollInterval) {
        clearInterval(pollInterval);
      }
    };
  }, [campaignId, isPolling, onComplete]);

  if (!campaign) {
    return (
      <div className="progress-container">
        <div className="loading-spinner"></div>
        <p>Loading campaign...</p>
      </div>
    );
  }

  const mainStep = getMainStep(campaign.current_step);
  const currentStepIndex = mainStep
    ? AGENT_STEPS.findIndex(step => mainStep.includes(step.key))
    : -1;

  // Get deep scraping progress for sub-progress bar
  const deepScrapingMatch = campaign.current_step?.match(/deep_scraping \((\d+)\/(\d+)\)/);
  const deepScrapingCurrent = deepScrapingMatch ? parseInt(deepScrapingMatch[1]) : 0;
  const deepScrapingTotal = deepScrapingMatch ? parseInt(deepScrapingMatch[2]) : 0;
  const deepScrapingPercent = deepScrapingTotal > 0 ? (deepScrapingCurrent / deepScrapingTotal) * 100 : 0;

  return (
    <div className="progress-container">
      <div className="progress-header">
        <h2>Campaign In Progress</h2>
        <div className="progress-status">
          <span className={`status-badge status-${campaign.status}`}>
            {campaign.status}
          </span>
          <span className="progress-percent">
            {Number(campaign.progress_percentage || 0).toFixed(0)}%
          </span>
        </div>
      </div>

      <div className="progress-bar-container">
        <div
          className="progress-bar-fill"
          style={{ width: `${campaign.progress_percentage || 0}%` }}
        />
      </div>

      {/* Live activity indicator */}
      {campaign.status === 'running' && campaign.current_step && (
        <div className="live-activity">
          <div className="live-dot"></div>
          <span className="live-text">
            {campaign.current_step.includes('research:')
              ? getResearchSubStepDescription(campaign.current_step)
              : AGENT_STEPS.find(s => mainStep.includes(s.key))?.description || campaign.current_step
            }
          </span>
        </div>
      )}

      <div className="agents-list">
        {AGENT_STEPS.map((agent, index) => {
          const isCompleted = index < currentStepIndex || campaign.status === 'completed';
          const isCurrent = index === currentStepIndex && campaign.status === 'running';
          const isPending = index > currentStepIndex;

          // Dynamic description for current research step
          let description = agent.description;
          if (agent.key === 'research' && isCurrent && campaign.current_step) {
            description = getResearchSubStepDescription(campaign.current_step);
          }

          return (
            <div
              key={agent.key}
              className={`agent-step ${isCompleted ? 'completed' : ''} ${isCurrent ? 'active' : ''} ${isPending ? 'pending' : ''}`}
            >
              <div className="agent-step-icon">
                {isCompleted ? (
                  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="12" r="10" fill="#10b981"/>
                    <path d="M8 12l2 2 4-4" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                ) : isCurrent ? (
                  <div className="spinner-small"></div>
                ) : (
                  <div className="step-number">{index + 1}</div>
                )}
              </div>
              <div className="agent-step-content">
                <div className="agent-step-name">{agent.name}</div>
                <div className="agent-step-description">{description}</div>

                {/* Sub-progress bar for deep scraping */}
                {agent.key === 'research' && isCurrent && deepScrapingTotal > 0 && (
                  <div className="sub-progress">
                    <div className="sub-progress-bar">
                      <div
                        className="sub-progress-fill"
                        style={{ width: `${deepScrapingPercent}%` }}
                      />
                    </div>
                    <span className="sub-progress-text">
                      {deepScrapingCurrent}/{deepScrapingTotal} products
                    </span>
                  </div>
                )}
              </div>
            </div>
          );
        })}
      </div>

      {campaign.status === 'completed' && (
        <div className="progress-complete">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <circle cx="32" cy="32" r="30" fill="#10b981"/>
            <path d="M20 32l8 8 16-16" stroke="white" strokeWidth="4" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <h3>Campaign Complete!</h3>
          <p>All agents have finished executing. View results below.</p>
        </div>
      )}

      {campaign.status === 'failed' && (
        <div className="progress-failed">
          <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
            <circle cx="32" cy="32" r="30" fill="#ef4444"/>
            <path d="M24 24L40 40M40 24L24 40" stroke="white" strokeWidth="4" strokeLinecap="round"/>
          </svg>
          <h3>Campaign Failed</h3>
          <p>An error occurred during execution. Please try again.</p>
        </div>
      )}
    </div>
  );
};

export default CampaignProgress;
