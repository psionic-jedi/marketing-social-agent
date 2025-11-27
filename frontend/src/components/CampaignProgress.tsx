import React, { useEffect, useState } from 'react';
import { Campaign, campaignService } from '../services/api';
import './CampaignProgress.css';

interface CampaignProgressProps {
  campaignId: string;
  onComplete: () => void;
}

const AGENT_STEPS = [
  { key: 'research', name: 'Research Agent', description: 'Analyzing category and products' },
  { key: 'deep_scraping', name: 'Deep Product Scraping', description: 'Visiting product pages for detailed info', isSubStep: true },
  { key: 'content', name: 'Content Agent', description: 'Generating marketing copy' },
  { key: 'social_media', name: 'Social Media Agent', description: 'Creating social media strategy' },
  { key: 'ppc', name: 'PPC Agent', description: 'Building Google Ads campaign' },
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

  const currentStepIndex = campaign.current_step
    ? AGENT_STEPS.findIndex(step => campaign.current_step?.includes(step.key))
    : -1;

  return (
    <div className="progress-container">
      <div className="progress-header">
        <h2>Campaign In Progress</h2>
        <div className="progress-status">
          <span className={`status-badge status-${campaign.status}`}>
            {campaign.status}
          </span>
          <span className="progress-percent">
            {campaign.progress_percentage || 0}%
          </span>
        </div>
      </div>

      <div className="progress-bar-container">
        <div
          className="progress-bar-fill"
          style={{ width: `${campaign.progress_percentage || 0}%` }}
        />
      </div>

      <div className="agents-list">
        {AGENT_STEPS.map((agent, index) => {
          const isCompleted = index < currentStepIndex || campaign.status === 'completed';
          const isCurrent = index === currentStepIndex && campaign.status === 'running';
          const isPending = index > currentStepIndex;
          const isSubStep = (agent as any).isSubStep;

          // Get dynamic description for deep scraping (shows "Scraping product 5/35")
          let description = agent.description;
          if (agent.key === 'deep_scraping' && isCurrent && campaign.current_step) {
            const match = campaign.current_step.match(/\((\d+)\/(\d+)\)/);
            if (match) {
              description = `Scraping product ${match[1]} of ${match[2]} for full details`;
            }
          }

          return (
            <div
              key={agent.key}
              className={`agent-step ${isCompleted ? 'completed' : ''} ${isCurrent ? 'active' : ''} ${isPending ? 'pending' : ''} ${isSubStep ? 'sub-step' : ''}`}
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
                  <div className="step-number">{isSubStep ? '↳' : index}</div>
                )}
              </div>
              <div className="agent-step-content">
                <div className="agent-step-name">{agent.name}</div>
                <div className="agent-step-description">{description}</div>
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
