import React, { useState, useEffect } from 'react';
import CampaignForm from './components/CampaignForm';
import CampaignResults from './components/CampaignResults';
import CampaignProgress from './components/CampaignProgress';
import { Campaign, CampaignResults as CampaignResultsType, campaignService } from './services/api';
import './App.css';

function App() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedCampaign, setSelectedCampaign] = useState<string | null>(null);
  const [campaignResults, setCampaignResults] = useState<CampaignResultsType | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Load campaigns on mount
  useEffect(() => {
    loadCampaigns();
  }, []);

  // Load campaign results when selected
  useEffect(() => {
    if (selectedCampaign) {
      loadCampaignResults(selectedCampaign);
    }
  }, [selectedCampaign]);

  const loadCampaigns = async () => {
    try {
      const data = await campaignService.getCampaigns();
      // Sort campaigns: completed first, then by creation date (newest first)
      const sorted = data.sort((a, b) => {
        // Prioritize completed campaigns
        if (a.status === 'completed' && b.status !== 'completed') return -1;
        if (a.status !== 'completed' && b.status === 'completed') return 1;
        // Then sort by creation date (newest first)
        return new Date(b.created_at).getTime() - new Date(a.created_at).getTime();
      });
      setCampaigns(sorted);
    } catch (error) {
      console.error('Failed to load campaigns:', error);
    }
  };

  const loadCampaignResults = async (id: string) => {
    setIsLoading(true);
    try {
      const results = await campaignService.getCampaignResults(id);
      setCampaignResults(results);
    } catch (error) {
      console.error('Failed to load campaign results:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCampaignCreated = (campaign: Campaign) => {
    setCampaigns([campaign, ...campaigns]);
    setSelectedCampaign(campaign.id);
  };

  const handleProgressComplete = () => {
    // Reload campaigns list
    loadCampaigns();
    // Load results
    if (selectedCampaign) {
      loadCampaignResults(selectedCampaign);
    }
  };

  // Get the selected campaign object
  const selectedCampaignObj = campaigns.find(c => c.id === selectedCampaign);
  const isRunning = selectedCampaignObj?.status === 'running' || selectedCampaignObj?.status === 'pending';

  return (
    <div className="app">
      {/* Header */}
      <header className="app-header">
        <div className="header-content">
          <div className="header-left">
            <div className="logo">
              <svg width="32" height="32" viewBox="0 0 32 32" fill="none">
                <rect width="32" height="32" rx="8" fill="url(#gradient)"/>
                <path d="M16 8L8 13L16 18L24 13L16 8Z" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <path d="M8 18L16 23L24 18" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <defs>
                  <linearGradient id="gradient" x1="0" y1="0" x2="32" y2="32">
                    <stop stopColor="#6366f1"/>
                    <stop offset="1" stopColor="#8b5cf6"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <div>
              <h1>Marketing Agent System</h1>
              <p>AI-Powered Campaign Generation</p>
            </div>
          </div>
          <div className="header-right">
            <div className="stat-badge">
              <span className="stat-label">Total Campaigns</span>
              <span className="stat-value">{campaigns.length}</span>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="app-main">
        <div className="main-grid">
          {/* Left Column - Form */}
          <aside className="sidebar">
            <CampaignForm onCampaignCreated={handleCampaignCreated} />

            {/* Campaign List */}
            {campaigns.length > 0 && (
              <div className="campaign-list">
                <h3>Recent Campaigns</h3>
                {campaigns.slice(0, 10).map((campaign: Campaign) => (
                  <button
                    key={campaign.id}
                    className={`campaign-item ${selectedCampaign === campaign.id ? 'active' : ''}`}
                    onClick={() => setSelectedCampaign(campaign.id)}
                  >
                    <div className="campaign-item-header">
                      <span className="campaign-url">{new URL(campaign.category_url).hostname}</span>
                      <span className={`status-dot status-${campaign.status}`}></span>
                    </div>
                    <div className="campaign-item-meta">
                      <span className="campaign-date">
                        {new Date(campaign.created_at).toLocaleDateString()}
                      </span>
                      {campaign.budget && (
                        <span className="campaign-budget">£{campaign.budget}</span>
                      )}
                    </div>
                  </button>
                ))}
              </div>
            )}
          </aside>

          {/* Right Column - Progress or Results */}
          <section className="content">
            {isRunning && selectedCampaign ? (
              <CampaignProgress
                campaignId={selectedCampaign}
                onComplete={handleProgressComplete}
              />
            ) : isLoading ? (
              <div className="loading-state">
                <div className="loading-spinner"></div>
                <p>Loading campaign results...</p>
              </div>
            ) : campaignResults ? (
              <CampaignResults results={campaignResults} />
            ) : (
              <div className="empty-state">
                <svg width="64" height="64" viewBox="0 0 64 64" fill="none">
                  <circle cx="32" cy="32" r="30" stroke="currentColor" strokeWidth="2" opacity="0.2"/>
                  <path d="M32 16V32L42 42" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
                </svg>
                <h3>No Campaign Selected</h3>
                <p>Create a new campaign or select one from the list to view results</p>
              </div>
            )}
          </section>
        </div>
      </main>
    </div>
  );
}

export default App;
