'use client'

import { useState, useEffect } from 'react'
import { X, Check, AlertCircle, ExternalLink, Plug } from 'lucide-react'

interface Integration {
  id: string
  name: string
  description: string
  icon: string
  connected: boolean
  category: 'ads' | 'crm' | 'analytics'
  comingSoon?: boolean
}

interface IntegrationsPanelProps {
  isOpen: boolean
  onClose: () => void
}

export function IntegrationsPanel({ isOpen, onClose }: IntegrationsPanelProps) {
  const [integrations, setIntegrations] = useState<Integration[]>([
    {
      id: 'google-ads',
      name: 'Google Ads',
      description: 'Connect your Google Ads account to analyze campaign performance and identify wasted spend',
      icon: '🔍',
      connected: false,
      category: 'ads'
    },
    {
      id: 'facebook-ads',
      name: 'Facebook Ads',
      description: 'Analyze Meta advertising campaigns across Facebook and Instagram',
      icon: '📘',
      connected: false,
      category: 'ads',
      comingSoon: true
    },
    {
      id: 'salesforce',
      name: 'Salesforce',
      description: 'Track leads and opportunities through your sales funnel',
      icon: '☁️',
      connected: false,
      category: 'crm',
      comingSoon: true
    },
    {
      id: 'hubspot',
      name: 'HubSpot',
      description: 'Monitor marketing automation and CRM performance',
      icon: '🧡',
      connected: false,
      category: 'crm',
      comingSoon: true
    },
    {
      id: 'google-analytics',
      name: 'Google Analytics',
      description: 'Deep dive into website traffic and user behavior',
      icon: '📊',
      connected: false,
      category: 'analytics',
      comingSoon: true
    }
  ])

  const [connecting, setConnecting] = useState<string | null>(null)

  const handleConnect = async (integrationId: string) => {
    if (integrationId === 'google-ads') {
      setConnecting(integrationId)
      
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        // Get OAuth URL from backend
        const response = await fetch(`${apiUrl}/api/integrations/google-ads/auth-url`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: localStorage.getItem('session_id') || crypto.randomUUID()
          })
        })

        if (response.ok) {
          const data = await response.json()
          // Save session_id before redirect
          const sessionId = localStorage.getItem('session_id')
          if (!sessionId) {
            localStorage.setItem('session_id', crypto.randomUUID())
          }
          // Redirect in same window for better UX
          window.location.href = data.auth_url
        }
      } catch (error) {
        console.error('Failed to connect:', error)
        setConnecting(null)
      }
    }
  }

  const handleDisconnect = async (integrationId: string) => {
    if (confirm('Are you sure you want to disconnect this integration?')) {
      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/api/integrations/google-ads/disconnect`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            session_id: localStorage.getItem('session_id')
          })
        })

        if (response.ok) {
          setIntegrations(prev => prev.map(i => 
            i.id === integrationId ? { ...i, connected: false } : i
          ))
        }
      } catch (error) {
        console.error('Failed to disconnect:', error)
      }
    }
  }

  // Check connection status on mount and handle OAuth callback
  useEffect(() => {
    const checkConnectionStatus = async () => {
      // Check if we're returning from OAuth
      const urlParams = new URLSearchParams(window.location.search)
      const googleAdsConnected = urlParams.get('google_ads_connected')
      
      if (googleAdsConnected === 'true') {
        // Update state to show connected
        setIntegrations(prev => prev.map(i => 
          i.id === 'google-ads' ? { ...i, connected: true } : i
        ))
        // Clean up URL
        window.history.replaceState({}, document.title, window.location.pathname)
        // Auto-open integrations panel to show success
        if (!isOpen) {
          // Small delay to ensure component is ready
          setTimeout(() => {
            const event = new CustomEvent('openIntegrations')
            window.dispatchEvent(event)
          }, 100)
        }
      }
      
      const sessionId = localStorage.getItem('session_id')
      if (!sessionId) {
        const newSessionId = crypto.randomUUID()
        localStorage.setItem('session_id', newSessionId)
        return
      }

      try {
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'
        const response = await fetch(`${apiUrl}/api/integrations/google-ads/status?session_id=${sessionId}`)
        if (response.ok) {
          const status = await response.json()
          if (status.connected) {
            setIntegrations(prev => prev.map(i => 
              i.id === 'google-ads' ? { ...i, connected: true } : i
            ))
          }
        }
      } catch (error) {
        console.error('Failed to check connection status:', error)
      }
    }

    checkConnectionStatus()
  }, [isOpen])

  if (!isOpen) return null

  const adIntegrations = integrations.filter(i => i.category === 'ads')
  const crmIntegrations = integrations.filter(i => i.category === 'crm')
  const analyticsIntegrations = integrations.filter(i => i.category === 'analytics')

  return (
    <>
      {/* Backdrop */}
      <div 
        style={{
          position: 'fixed',
          inset: 0,
          backgroundColor: 'rgba(0,0,0,0.5)',
          zIndex: 40
        }}
        onClick={onClose}
      />
      
      {/* Panel */}
      <div style={{
        position: 'fixed',
        right: 0,
        top: 0,
        bottom: 0,
        width: '400px',
        backgroundColor: '#171717',
        borderLeft: '1px solid rgba(255,255,255,0.1)',
        zIndex: 50,
        display: 'flex',
        flexDirection: 'column',
        transform: 'translateX(0)',
        transition: 'transform 0.3s ease'
      }}>
        {/* Header */}
        <div style={{
          padding: '16px 20px',
          borderBottom: '1px solid rgba(255,255,255,0.1)',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <Plug size={20} color="#ab68ff" />
            <h2 style={{ 
              fontSize: '18px', 
              fontWeight: '600',
              color: 'white',
              margin: 0
            }}>
              Integrations
            </h2>
          </div>
          <button
            onClick={onClose}
            style={{
              background: 'none',
              border: 'none',
              cursor: 'pointer',
              padding: '4px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center'
            }}
          >
            <X size={20} color="rgba(255,255,255,0.5)" />
          </button>
        </div>

        {/* Content */}
        <div style={{
          flex: 1,
          overflowY: 'auto',
          padding: '20px'
        }}>
          {/* Advertising Platforms */}
          <div style={{ marginBottom: '32px' }}>
            <h3 style={{
              fontSize: '12px',
              fontWeight: '600',
              color: 'rgba(255,255,255,0.5)',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              marginBottom: '12px'
            }}>
              Advertising Platforms
            </h3>
            {adIntegrations.map(integration => (
              <IntegrationCard
                key={integration.id}
                integration={integration}
                onConnect={() => handleConnect(integration.id)}
                onDisconnect={() => handleDisconnect(integration.id)}
                isConnecting={connecting === integration.id}
              />
            ))}
          </div>

          {/* CRM Systems */}
          <div style={{ marginBottom: '32px' }}>
            <h3 style={{
              fontSize: '12px',
              fontWeight: '600',
              color: 'rgba(255,255,255,0.5)',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              marginBottom: '12px'
            }}>
              CRM Systems
            </h3>
            {crmIntegrations.map(integration => (
              <IntegrationCard
                key={integration.id}
                integration={integration}
                onConnect={() => handleConnect(integration.id)}
                onDisconnect={() => handleDisconnect(integration.id)}
                isConnecting={connecting === integration.id}
              />
            ))}
          </div>

          {/* Analytics Tools */}
          <div style={{ marginBottom: '32px' }}>
            <h3 style={{
              fontSize: '12px',
              fontWeight: '600',
              color: 'rgba(255,255,255,0.5)',
              textTransform: 'uppercase',
              letterSpacing: '0.5px',
              marginBottom: '12px'
            }}>
              Analytics Tools
            </h3>
            {analyticsIntegrations.map(integration => (
              <IntegrationCard
                key={integration.id}
                integration={integration}
                onConnect={() => handleConnect(integration.id)}
                onDisconnect={() => handleDisconnect(integration.id)}
                isConnecting={connecting === integration.id}
              />
            ))}
          </div>
        </div>

        {/* Footer */}
        <div style={{
          padding: '16px 20px',
          borderTop: '1px solid rgba(255,255,255,0.1)',
          backgroundColor: 'rgba(171,104,255,0.05)'
        }}>
          <p style={{
            fontSize: '12px',
            color: 'rgba(255,255,255,0.6)',
            margin: 0,
            lineHeight: '1.5'
          }}>
            <AlertCircle size={14} style={{ display: 'inline', verticalAlign: 'text-bottom', marginRight: '6px' }} />
            Once connected, you can ask questions about your ad campaigns, CRM data, and analytics directly in the chat.
          </p>
        </div>
      </div>
    </>
  )
}

function IntegrationCard({ 
  integration, 
  onConnect, 
  onDisconnect, 
  isConnecting 
}: {
  integration: Integration
  onConnect: () => void
  onDisconnect: () => void
  isConnecting: boolean
}) {
  return (
    <div style={{
      backgroundColor: 'rgba(255,255,255,0.03)',
      border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: '8px',
      padding: '16px',
      marginBottom: '12px',
      transition: 'all 0.2s'
    }}>
      <div style={{ display: 'flex', alignItems: 'start', gap: '12px' }}>
        <div style={{
          fontSize: '24px',
          lineHeight: '1'
        }}>
          {integration.icon}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px',
            marginBottom: '4px'
          }}>
            <h4 style={{
              fontSize: '14px',
              fontWeight: '600',
              color: 'white',
              margin: 0
            }}>
              {integration.name}
            </h4>
            {integration.connected && (
              <span style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '4px',
                fontSize: '11px',
                color: '#10a37f',
                backgroundColor: 'rgba(16,163,127,0.1)',
                padding: '2px 6px',
                borderRadius: '4px'
              }}>
                <Check size={10} />
                Connected
              </span>
            )}
            {integration.comingSoon && (
              <span style={{
                fontSize: '11px',
                color: 'rgba(255,255,255,0.5)',
                backgroundColor: 'rgba(255,255,255,0.1)',
                padding: '2px 6px',
                borderRadius: '4px'
              }}>
                Coming Soon
              </span>
            )}
          </div>
          <p style={{
            fontSize: '12px',
            color: 'rgba(255,255,255,0.6)',
            margin: '4px 0 12px 0',
            lineHeight: '1.4'
          }}>
            {integration.description}
          </p>
          {!integration.comingSoon && (
            <button
              onClick={integration.connected ? onDisconnect : onConnect}
              disabled={isConnecting}
              style={{
                padding: '6px 12px',
                backgroundColor: integration.connected 
                  ? 'transparent'
                  : isConnecting 
                    ? 'rgba(171,104,255,0.5)' 
                    : '#ab68ff',
                color: integration.connected ? 'rgba(255,255,255,0.7)' : 'white',
                border: integration.connected ? '1px solid rgba(255,255,255,0.2)' : 'none',
                borderRadius: '6px',
                cursor: isConnecting ? 'not-allowed' : 'pointer',
                fontSize: '13px',
                fontWeight: '500',
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                transition: 'all 0.2s'
              }}
            >
              {isConnecting ? (
                <>Connecting...</>
              ) : integration.connected ? (
                <>Disconnect</>
              ) : (
                <>
                  Connect
                  <ExternalLink size={12} />
                </>
              )}
            </button>
          )}
        </div>
      </div>
    </div>
  )
}