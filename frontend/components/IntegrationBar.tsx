'use client';

import React, { useState } from 'react';
import { 
  Zap, ChevronDown, BarChart3, Search, Users, 
  TrendingUp, Shield, ExternalLink, Check, Sparkles
} from 'lucide-react';

interface Integration {
  id: string;
  name: string;
  icon: React.ReactNode;
  connected: boolean;
  description: string;
  metrics: number;
}

interface IntegrationBarProps {
  onConnect: (integrationId: string) => void;
}

export function IntegrationBar({ onConnect }: IntegrationBarProps) {
  const [expanded, setExpanded] = useState(false);
  
  // In production, this would come from your auth state
  const [integrations, setIntegrations] = useState<Integration[]>([
    {
      id: 'google-analytics',
      name: 'Google Analytics',
      icon: <BarChart3 className="w-4 h-4" />,
      connected: false,
      description: 'Real traffic & conversion data',
      metrics: 50
    },
    {
      id: 'search-console',
      name: 'Search Console',
      icon: <Search className="w-4 h-4" />,
      connected: false,
      description: 'SEO performance & rankings',
      metrics: 30
    },
    {
      id: 'meta-ads',
      name: 'Meta Ads',
      icon: <Users className="w-4 h-4" />,
      connected: false,
      description: 'Ad performance & ROAS',
      metrics: 40
    },
    {
      id: 'google-ads',
      name: 'Google Ads',
      icon: <TrendingUp className="w-4 h-4" />,
      connected: false,
      description: 'PPC campaigns & keywords',
      metrics: 35
    }
  ]);

  const connectedCount = integrations.filter(i => i.connected).length;
  const hasConnections = connectedCount > 0;

  const handleConnect = async (integrationId: string) => {
    // This will trigger OAuth flow
    onConnect(integrationId);
    
    // Update UI optimistically
    setIntegrations(prev => 
      prev.map(i => i.id === integrationId ? { ...i, connected: true } : i)
    );
  };

  return (
    <div className="w-full max-w-2xl mx-auto mb-3">
      {/* Collapsed Bar */}
      <div 
        onClick={() => setExpanded(!expanded)}
        className={`
          relative cursor-pointer rounded-xl p-3 transition-all
          ${hasConnections 
            ? 'bg-gradient-to-r from-green-500/10 to-green-600/10 border border-green-500/30' 
            : 'bg-gradient-to-r from-purple-500/10 to-purple-600/10 border border-purple-500/20'
          }
          hover:shadow-lg
        `}
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className={`p-1.5 rounded-lg ${
              hasConnections ? 'bg-green-500/20' : 'bg-purple-500/20'
            }`}>
              {hasConnections ? (
                <Zap className="w-4 h-4 text-green-400" />
              ) : (
                <Sparkles className="w-4 h-4 text-purple-400" />
              )}
            </div>
            
            <div>
              <div className={`text-sm font-medium ${
                hasConnections ? 'text-green-400' : 'text-gray-200'
              }`}>
                {hasConnections 
                  ? `${connectedCount} Integration${connectedCount > 1 ? 's' : ''} Active`
                  : 'Connect Your Data for 10x Better Insights'
                }
              </div>
              {!hasConnections && (
                <div className="text-xs text-gray-500">
                  See real traffic, conversions & revenue
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center gap-2">
            {/* Status dots */}
            <div className="flex gap-1">
              {integrations.map(integration => (
                <div
                  key={integration.id}
                  className={`w-1.5 h-1.5 rounded-full ${
                    integration.connected ? 'bg-green-400' : 'bg-gray-600'
                  }`}
                  title={integration.name}
                />
              ))}
            </div>
            
            <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${
              expanded ? 'rotate-180' : ''
            }`} />
          </div>
        </div>
      </div>

      {/* Expanded Panel */}
      {expanded && (
        <div className="mt-2 bg-gray-800/50 backdrop-blur border border-gray-700 rounded-xl p-4 animate-fadeIn">
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-semibold text-gray-200">Available Integrations</h3>
            <div className="flex items-center gap-1 text-xs text-gray-500">
              <Shield className="w-3 h-3" />
              <span>Secure OAuth</span>
            </div>
          </div>

          <div className="space-y-2">
            {integrations.map(integration => (
              <div
                key={integration.id}
                className={`
                  flex items-center justify-between p-3 rounded-lg transition-all
                  ${integration.connected 
                    ? 'bg-green-500/10 border border-green-500/30' 
                    : 'bg-gray-700/50 border border-gray-600 hover:bg-gray-700'
                  }
                `}
              >
                <div className="flex items-center gap-3">
                  <div className={`p-1.5 rounded-lg ${
                    integration.connected ? 'bg-green-500/20' : 'bg-gray-600'
                  }`}>
                    {integration.icon}
                  </div>
                  
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-sm font-medium text-gray-200">
                        {integration.name}
                      </span>
                      {integration.connected && (
                        <Check className="w-3 h-3 text-green-400" />
                      )}
                    </div>
                    <div className="text-xs text-gray-500">
                      {integration.description} • {integration.metrics}+ metrics
                    </div>
                  </div>
                </div>

                {!integration.connected && (
                  <button
                    onClick={(e) => {
                      e.stopPropagation();
                      handleConnect(integration.id);
                    }}
                    className="px-3 py-1 bg-purple-600 hover:bg-purple-700 text-white text-xs rounded-lg font-medium flex items-center gap-1 transition-colors"
                  >
                    Connect
                    <ExternalLink className="w-3 h-3" />
                  </button>
                )}
              </div>
            ))}
          </div>

          {!hasConnections && (
            <div className="mt-3 p-3 bg-purple-500/10 border border-purple-500/20 rounded-lg">
              <div className="text-xs text-gray-300">
                <div className="font-medium text-purple-400 mb-1">Why connect?</div>
                <div className="space-y-0.5 text-gray-400">
                  <div>• Actual visitor numbers, not estimates</div>
                  <div>• Real conversion rates & revenue</div>
                  <div>• Personalized recommendations</div>
                </div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}