'use client';

import React, { useState } from 'react';
import { 
  Plus, Check, AlertCircle, TrendingUp, Users, Search, 
  BarChart3, Lock, ChevronDown, X, Sparkles, ExternalLink,
  Zap, Shield, RefreshCw
} from 'lucide-react';

export default function IntegrationMockupPage() {
  const [showIntegrations, setShowIntegrations] = useState(false);
  const [connectedIntegrations, setConnectedIntegrations] = useState<string[]>([]);
  const [expandedIntegration, setExpandedIntegration] = useState<string | null>(null);

  const integrations = [
    {
      id: 'google-analytics',
      name: 'Google Analytics',
      icon: <BarChart3 className="w-5 h-5" />,
      status: connectedIntegrations.includes('google-analytics') ? 'connected' : 'not_connected',
      description: 'Your actual traffic & conversion data',
      benefits: [
        'Real visitor numbers',
        'Conversion rates',
        'User behavior flow',
        'Revenue tracking'
      ],
      color: 'orange',
      dataPoints: '50+ metrics'
    },
    {
      id: 'search-console',
      name: 'Search Console',
      icon: <Search className="w-5 h-5" />,
      status: connectedIntegrations.includes('search-console') ? 'connected' : 'not_connected',
      description: 'SEO performance & rankings',
      benefits: [
        'Keyword rankings',
        'Click-through rates',
        'Search impressions',
        'Index coverage'
      ],
      color: 'blue',
      dataPoints: '30+ metrics'
    },
    {
      id: 'facebook-ads',
      name: 'Meta Ads',
      icon: <Users className="w-5 h-5" />,
      status: connectedIntegrations.includes('facebook-ads') ? 'connected' : 'not_connected',
      description: 'Ad performance & ROAS',
      benefits: [
        'Ad spend & ROAS',
        'Audience insights',
        'Creative performance',
        'Conversion tracking'
      ],
      color: 'blue',
      dataPoints: '40+ metrics'
    },
    {
      id: 'google-ads',
      name: 'Google Ads',
      icon: <TrendingUp className="w-5 h-5" />,
      status: connectedIntegrations.includes('google-ads') ? 'connected' : 'not_connected',
      description: 'PPC campaigns & keywords',
      benefits: [
        'Campaign performance',
        'Keyword quality scores',
        'Cost per conversion',
        'Competitor insights'
      ],
      color: 'green',
      dataPoints: '35+ metrics'
    }
  ];

  const handleConnect = (integrationId: string) => {
    // Simulate OAuth flow
    setTimeout(() => {
      setConnectedIntegrations([...connectedIntegrations, integrationId]);
    }, 1500);
  };

  const connectedCount = connectedIntegrations.length;
  const totalIntegrations = integrations.length;

  return (
    <div className="min-h-screen bg-gray-900 text-white">
      {/* Header */}
      <div className="border-b border-gray-800 p-4">
        <div className="max-w-6xl mx-auto flex items-center justify-between">
          <h1 className="text-xl font-semibold">Integration Mockup</h1>
          <a href="/" className="text-gray-400 hover:text-white">Back to App</a>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-4xl mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Hey there. Ready to analyze?</h1>
          
          {/* Example Prompts */}
          <div className="grid grid-cols-2 gap-3 max-w-2xl mx-auto mb-8">
            <button className="p-3 bg-gray-800 rounded-lg hover:bg-gray-700 text-left">
              <div className="font-medium">stripe.com vs square.com</div>
              <div className="text-sm text-gray-400">Compare payment platforms</div>
            </button>
            <button className="p-3 bg-gray-800 rounded-lg hover:bg-gray-700 text-left">
              <div className="font-medium">Find revenue leaks</div>
              <div className="text-sm text-gray-400">shopify.com e-commerce analysis</div>
            </button>
            <button className="p-3 bg-gray-800 rounded-lg hover:bg-gray-700 text-left">
              <div className="font-medium">notion.so growth tactics</div>
              <div className="text-sm text-gray-400">SaaS optimization strategies</div>
            </button>
            <button className="p-3 bg-gray-800 rounded-lg hover:bg-gray-700 text-left">
              <div className="font-medium">SEO audit</div>
              <div className="text-sm text-gray-400">techcrunch.com content strategy</div>
            </button>
          </div>
        </div>

        {/* Integration Status Bar - THE KEY COMPONENT */}
        <div className="mb-4">
          <div 
            className={`
              bg-gradient-to-r from-gray-800 to-gray-850 
              border ${connectedCount > 0 ? 'border-green-500/30' : 'border-gray-700'} 
              rounded-xl p-4 cursor-pointer transition-all
              ${showIntegrations ? 'shadow-2xl' : 'hover:shadow-lg'}
            `}
            onClick={() => setShowIntegrations(!showIntegrations)}
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                {connectedCount > 0 ? (
                  <>
                    <div className="p-2 bg-green-500/20 rounded-lg">
                      <Zap className="w-5 h-5 text-green-400" />
                    </div>
                    <div>
                      <div className="font-medium text-green-400">
                        {connectedCount} Integration{connectedCount !== 1 ? 's' : ''} Connected
                      </div>
                      <div className="text-xs text-gray-400">
                        Analyzing with your real data
                      </div>
                    </div>
                  </>
                ) : (
                  <>
                    <div className="p-2 bg-purple-500/20 rounded-lg">
                      <Sparkles className="w-5 h-5 text-purple-400" />
                    </div>
                    <div>
                      <div className="font-medium">Connect Your Data Sources</div>
                      <div className="text-xs text-gray-400">
                        Get 10x more accurate insights with your real data
                      </div>
                    </div>
                  </>
                )}
              </div>
              
              <div className="flex items-center gap-3">
                {/* Mini status indicators */}
                <div className="flex gap-1">
                  {integrations.map((integration) => (
                    <div
                      key={integration.id}
                      className={`
                        w-2 h-2 rounded-full
                        ${connectedIntegrations.includes(integration.id) 
                          ? 'bg-green-400' 
                          : 'bg-gray-600'}
                      `}
                      title={integration.name}
                    />
                  ))}
                </div>
                <ChevronDown 
                  className={`w-5 h-5 text-gray-400 transition-transform ${
                    showIntegrations ? 'rotate-180' : ''
                  }`} 
                />
              </div>
            </div>
          </div>

          {/* Expanded Integration Panel */}
          {showIntegrations && (
            <div className="mt-4 bg-gray-850 border border-gray-700 rounded-xl p-6 animate-fadeIn">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold">Data Integrations</h3>
                <div className="flex items-center gap-2 text-sm text-gray-400">
                  <Shield className="w-4 h-4" />
                  <span>Secure OAuth • Read-only access</span>
                </div>
              </div>

              <div className="grid gap-4">
                {integrations.map((integration) => (
                  <div
                    key={integration.id}
                    className={`
                      border rounded-lg p-4 transition-all
                      ${connectedIntegrations.includes(integration.id)
                        ? 'border-green-500/30 bg-green-500/5'
                        : 'border-gray-700 bg-gray-800/50 hover:bg-gray-800'}
                    `}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start gap-3">
                        <div className={`
                          p-2 rounded-lg
                          ${connectedIntegrations.includes(integration.id)
                            ? 'bg-green-500/20'
                            : 'bg-gray-700'}
                        `}>
                          {integration.icon}
                        </div>
                        <div className="flex-1">
                          <div className="flex items-center gap-2 mb-1">
                            <h4 className="font-medium">{integration.name}</h4>
                            {connectedIntegrations.includes(integration.id) && (
                              <span className="px-2 py-0.5 bg-green-500/20 text-green-400 text-xs rounded-full">
                                Connected
                              </span>
                            )}
                          </div>
                          <p className="text-sm text-gray-400 mb-2">
                            {integration.description}
                          </p>
                          
                          {expandedIntegration === integration.id && (
                            <div className="mt-3 pt-3 border-t border-gray-700">
                              <div className="text-xs text-gray-400 mb-2">This integration provides:</div>
                              <div className="grid grid-cols-2 gap-2">
                                {integration.benefits.map((benefit, idx) => (
                                  <div key={idx} className="flex items-center gap-1 text-xs">
                                    <Check className="w-3 h-3 text-green-400" />
                                    <span>{benefit}</span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center gap-2">
                        <button
                          onClick={(e) => {
                            e.stopPropagation();
                            setExpandedIntegration(
                              expandedIntegration === integration.id ? null : integration.id
                            );
                          }}
                          className="text-gray-400 hover:text-white"
                        >
                          <ChevronDown 
                            className={`w-4 h-4 transition-transform ${
                              expandedIntegration === integration.id ? 'rotate-180' : ''
                            }`}
                          />
                        </button>
                        {connectedIntegrations.includes(integration.id) ? (
                          <button className="px-3 py-1 bg-gray-700 text-gray-400 rounded-lg text-sm">
                            <RefreshCw className="w-4 h-4" />
                          </button>
                        ) : (
                          <button
                            onClick={() => handleConnect(integration.id)}
                            className="px-4 py-1.5 bg-purple-600 hover:bg-purple-700 rounded-lg text-sm font-medium flex items-center gap-1"
                          >
                            Connect
                            <ExternalLink className="w-3 h-3" />
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Benefits of connecting */}
              {connectedCount === 0 && (
                <div className="mt-6 p-4 bg-purple-500/10 border border-purple-500/30 rounded-lg">
                  <div className="flex items-start gap-3">
                    <Sparkles className="w-5 h-5 text-purple-400 mt-0.5" />
                    <div>
                      <div className="font-medium text-purple-400 mb-1">
                        Why connect your data?
                      </div>
                      <ul className="text-sm text-gray-300 space-y-1">
                        <li>• See actual visitor numbers, not estimates</li>
                        <li>• Track real conversion rates and revenue</li>
                        <li>• Compare your metrics to competitors</li>
                        <li>• Get personalized optimization recommendations</li>
                      </ul>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Chat Input */}
        <div className="relative">
          <input
            type="text"
            placeholder={
              connectedCount > 0 
                ? "Analyze with your connected data..." 
                : "Enter a domain to analyze (e.g., stripe.com)"
            }
            className="w-full px-4 py-4 bg-gray-800 border border-gray-700 rounded-xl pr-12 focus:outline-none focus:border-purple-500"
          />
          <button className="absolute right-2 top-1/2 -translate-y-1/2 p-2 bg-purple-600 rounded-lg hover:bg-purple-700">
            <TrendingUp className="w-5 h-5" />
          </button>
        </div>

        {/* Trust indicators */}
        <div className="mt-4 flex items-center justify-center gap-6 text-xs text-gray-500">
          <div className="flex items-center gap-1">
            <Lock className="w-3 h-3" />
            <span>Bank-level encryption</span>
          </div>
          <div className="flex items-center gap-1">
            <Shield className="w-3 h-3" />
            <span>Read-only access</span>
          </div>
          <div className="flex items-center gap-1">
            <RefreshCw className="w-3 h-3" />
            <span>Revoke anytime</span>
          </div>
        </div>
      </div>
    </div>
  );
}