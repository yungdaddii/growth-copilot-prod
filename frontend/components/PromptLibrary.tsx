'use client';

import React, { useState } from 'react';
import { 
  X, ChevronDown, ChevronRight, Search, Sparkles, 
  TrendingUp, DollarSign, Users, BarChart3, Target,
  Zap, Globe, ShoppingCart, Brain, LineChart, Filter,
  Copy, BookOpen
} from 'lucide-react';

interface Prompt {
  text: string;
  badge?: string; // e.g., "Popular", "New", "Pro"
}

interface Category {
  id: string;
  name: string;
  icon: React.ReactNode;
  prompts: Prompt[];
}

interface PromptLibraryProps {
  isOpen: boolean;
  onClose: () => void;
  onSelectPrompt: (prompt: string) => void;
}

export function PromptLibrary({ isOpen, onClose, onSelectPrompt }: PromptLibraryProps) {
  const [searchQuery, setSearchQuery] = useState('');
  const [expandedCategories, setExpandedCategories] = useState<string[]>(['acquisition']);

  const categories: Category[] = [
    {
      id: 'acquisition',
      name: 'Acquisition & Channel Performance',
      icon: <Target className="w-4 h-4" />,
      prompts: [
        { text: "What's my CAC by channel over the last 6 months?", badge: "Popular" },
        { text: "Show me the LTV:CAC ratio for each acquisition channel" },
        { text: "Which channels have the highest ROI?" },
        { text: "What's my cost per lead across all channels?" },
        { text: "Show me channel performance trends month-over-month" },
        { text: "Which campaigns are driving the most qualified leads?" },
        { text: "What's my average deal size by channel?" },
        { text: "Compare paid vs organic acquisition costs" },
        { text: "Which channels have the shortest sales cycles?" },
        { text: "Show me attribution models comparison" },
      ]
    },
    {
      id: 'conversion',
      name: 'Conversion & Funnel Optimization',
      icon: <TrendingUp className="w-4 h-4" />,
      prompts: [
        { text: "Where are the biggest drop-offs in my funnel?", badge: "Popular" },
        { text: "What's my visitor-to-lead conversion rate by landing page?" },
        { text: "Show me conversion rates by device type" },
        { text: "What's my trial-to-paid conversion rate?" },
        { text: "Which lead magnets have the highest conversion rates?" },
        { text: "What's my shopping cart abandonment rate?" },
        { text: "Show me conversion rates by traffic source and campaign" },
        { text: "What's killing my checkout conversion?" },
        { text: "Compare form completion rates across pages" },
        { text: "Show me micro-conversion improvements" },
      ]
    },
    {
      id: 'retention',
      name: 'Retention & Engagement',
      icon: <Users className="w-4 h-4" />,
      prompts: [
        { text: "What's my monthly churn rate?", badge: "Critical" },
        { text: "Show me user engagement metrics by cohort" },
        { text: "What's my product adoption rate for new features?" },
        { text: "Which user segments have the highest retention?" },
        { text: "What's my NPS score trend?" },
        { text: "Show me customer reactivation campaign performance" },
        { text: "What's my average customer lifetime by segment?" },
        { text: "Identify at-risk customers likely to churn" },
        { text: "What features correlate with long-term retention?" },
        { text: "Show me expansion revenue opportunities" },
      ]
    },
    {
      id: 'content',
      name: 'Content & SEO Performance',
      icon: <Globe className="w-4 h-4" />,
      prompts: [
        { text: "Which blog posts drive the most conversions?" },
        { text: "What keywords are my competitors ranking for that I'm not?", badge: "Competitive" },
        { text: "Show me my domain authority growth" },
        { text: "Which pages have the highest bounce rates?" },
        { text: "What's my organic traffic growth rate?" },
        { text: "Which content types generate the most backlinks?" },
        { text: "Show me page load speeds across my site" },
        { text: "What content gaps exist vs competitors?" },
        { text: "Which keywords have the highest commercial intent?" },
        { text: "Show me featured snippet opportunities" },
      ]
    },
    {
      id: 'revenue',
      name: 'Revenue & Growth Metrics',
      icon: <DollarSign className="w-4 h-4" />,
      prompts: [
        { text: "What's my MRR growth rate?", badge: "Essential" },
        { text: "Show me revenue by customer segment" },
        { text: "What's my average revenue per user (ARPU)?" },
        { text: "Which products have the highest attach rates?" },
        { text: "What's my expansion revenue from existing customers?" },
        { text: "Show me revenue attribution by first touch vs last touch" },
        { text: "What's my payback period by channel?" },
        { text: "Calculate my unit economics by product" },
        { text: "What's my quick ratio (growth efficiency)?" },
        { text: "Show me revenue concentration risk" },
      ]
    },
    {
      id: 'testing',
      name: 'Testing & Experimentation',
      icon: <Brain className="w-4 h-4" />,
      prompts: [
        { text: "Which A/B tests had the biggest impact on conversion?" },
        { text: "Show me all active experiments and their performance" },
        { text: "What elements should I test next based on impact potential?" },
        { text: "What's the statistical significance of my current tests?" },
        { text: "Show me test velocity by team/quarter" },
        { text: "Which tests failed and what can we learn?" },
        { text: "Calculate sample size needed for my next test" },
        { text: "Show me personalization opportunities" },
      ]
    },
    {
      id: 'competitive',
      name: 'Competitive & Market Analysis',
      icon: <BarChart3 className="w-4 h-4" />,
      prompts: [
        { text: "How does my growth rate compare to competitors?", badge: "Insight" },
        { text: "What's my share of voice in my market?" },
        { text: "Show me competitor pricing changes" },
        { text: "What marketing channels are competitors using that I'm not?" },
        { text: "How does my conversion rate benchmark against industry?" },
        { text: "Track competitor feature launches" },
        { text: "What's my relative market position?" },
        { text: "Show me competitive gaps and opportunities" },
      ]
    },
    {
      id: 'budget',
      name: 'Budget & Resource Allocation',
      icon: <LineChart className="w-4 h-4" />,
      prompts: [
        { text: "What's my marketing efficiency ratio (MER)?", badge: "CFO Ready" },
        { text: "Where should I reallocate budget for maximum impact?" },
        { text: "Show me spend vs revenue by channel" },
        { text: "What's my return on ad spend (ROAS) by campaign?" },
        { text: "Which channels are underperforming relative to spend?" },
        { text: "Calculate my blended CAC including all costs" },
        { text: "What's my marketing as % of revenue?" },
        { text: "Show me diminishing returns by channel" },
      ]
    },
    {
      id: 'product',
      name: 'Product & Feature Analytics',
      icon: <Zap className="w-4 h-4" />,
      prompts: [
        { text: "Which features drive the most engagement?" },
        { text: "What's the adoption rate of our latest feature?" },
        { text: "Show me feature usage by customer segment" },
        { text: "Which features correlate with upgrades?" },
        { text: "What's our time to first value?" },
        { text: "Show me the user journey to 'aha moment'" },
        { text: "Which features have the highest stickiness?" },
        { text: "Identify unused features to sunset" },
      ]
    },
    {
      id: 'email',
      name: 'Email & Marketing Automation',
      icon: <ShoppingCart className="w-4 h-4" />,
      prompts: [
        { text: "What's my email open rate by segment?" },
        { text: "Which email campaigns drive the most revenue?" },
        { text: "Show me optimal send times by audience" },
        { text: "What's my email list growth rate?" },
        { text: "Which automation flows have the highest ROI?" },
        { text: "Show me email fatigue indicators" },
        { text: "What subject lines perform best?" },
        { text: "Compare email vs SMS performance" },
      ]
    },
    {
      id: 'social',
      name: 'Social & Community',
      icon: <Users className="w-4 h-4" />,
      prompts: [
        { text: "What's my social media engagement rate?" },
        { text: "Which social posts drive the most traffic?" },
        { text: "Show me community growth metrics" },
        { text: "What's my share of voice on social?" },
        { text: "Which influencers drive the most conversions?" },
        { text: "Track brand sentiment over time" },
        { text: "What content gets the most shares?" },
        { text: "Show me viral coefficient by campaign" },
      ]
    },
    {
      id: 'ai-optimization',
      name: 'AI & Search Optimization',
      icon: <Brain className="w-4 h-4" />,
      prompts: [
        { text: "How visible am I to ChatGPT and Claude?", badge: "New" },
        { text: "What AI crawlers am I blocking?" },
        { text: "Optimize my content for AI search" },
        { text: "Show me AI-friendly schema markup opportunities" },
        { text: "What questions do AI models answer about my brand?" },
        { text: "Compare my AI visibility vs competitors" },
        { text: "Generate AI-optimized meta descriptions" },
        { text: "What's my llms.txt compliance score?" },
      ]
    },
  ];

  const toggleCategory = (categoryId: string) => {
    setExpandedCategories(prev =>
      prev.includes(categoryId)
        ? prev.filter(id => id !== categoryId)
        : [...prev, categoryId]
    );
  };

  const filteredCategories = categories.map(category => ({
    ...category,
    prompts: category.prompts.filter(prompt =>
      prompt.text.toLowerCase().includes(searchQuery.toLowerCase())
    )
  })).filter(category => 
    searchQuery === '' || category.prompts.length > 0
  );

  const handlePromptClick = (prompt: string) => {
    onSelectPrompt(prompt);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div style={{
      position: 'fixed',
      right: 0,
      top: 0,
      height: '100vh',
      width: '400px',
      backgroundColor: '#1a1a1a',
      borderLeft: '1px solid rgba(255,255,255,0.1)',
      display: 'flex',
      flexDirection: 'column',
      zIndex: 1000,
      boxShadow: '-4px 0 24px rgba(0,0,0,0.3)'
    }}>
      {/* Header */}
      <div style={{
        padding: '16px 20px',
        borderBottom: '1px solid rgba(255,255,255,0.1)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        backgroundColor: '#1f1f1f'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <BookOpen size={20} style={{ color: '#ab68ff' }} />
          <h2 style={{ 
            fontSize: '16px', 
            fontWeight: '600',
            color: '#fff',
            margin: 0 
          }}>
            Prompt Library
          </h2>
          <span style={{
            padding: '2px 8px',
            backgroundColor: 'rgba(171, 104, 255, 0.2)',
            color: '#ab68ff',
            fontSize: '11px',
            borderRadius: '12px',
            fontWeight: '500'
          }}>
            {categories.reduce((acc, cat) => acc + cat.prompts.length, 0)} prompts
          </span>
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
          <X size={20} style={{ color: 'rgba(255,255,255,0.5)' }} />
        </button>
      </div>

      {/* Search */}
      <div style={{ padding: '12px 16px', borderBottom: '1px solid rgba(255,255,255,0.1)' }}>
        <div style={{
          position: 'relative',
          display: 'flex',
          alignItems: 'center'
        }}>
          <Search size={16} style={{
            position: 'absolute',
            left: '12px',
            color: 'rgba(255,255,255,0.4)'
          }} />
          <input
            type="text"
            placeholder="Search prompts..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            style={{
              width: '100%',
              padding: '8px 12px 8px 36px',
              backgroundColor: 'rgba(255,255,255,0.05)',
              border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: '8px',
              color: '#fff',
              fontSize: '14px',
              outline: 'none'
            }}
          />
        </div>
      </div>

      {/* Categories */}
      <div style={{
        flex: 1,
        overflowY: 'auto',
        padding: '8px'
      }}>
        {filteredCategories.map(category => (
          <div key={category.id} style={{ marginBottom: '4px' }}>
            <button
              onClick={() => toggleCategory(category.id)}
              style={{
                width: '100%',
                padding: '10px 12px',
                backgroundColor: expandedCategories.includes(category.id) 
                  ? 'rgba(171, 104, 255, 0.1)' 
                  : 'transparent',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                gap: '8px',
                color: '#fff',
                fontSize: '14px',
                fontWeight: '500',
                transition: 'all 0.2s'
              }}
              onMouseEnter={(e) => {
                if (!expandedCategories.includes(category.id)) {
                  e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.05)';
                }
              }}
              onMouseLeave={(e) => {
                if (!expandedCategories.includes(category.id)) {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }
              }}
            >
              {expandedCategories.includes(category.id) ? (
                <ChevronDown size={16} style={{ color: 'rgba(255,255,255,0.5)' }} />
              ) : (
                <ChevronRight size={16} style={{ color: 'rgba(255,255,255,0.5)' }} />
              )}
              {category.icon}
              <span style={{ flex: 1, textAlign: 'left' }}>{category.name}</span>
              <span style={{
                fontSize: '12px',
                color: 'rgba(255,255,255,0.4)'
              }}>
                {category.prompts.length}
              </span>
            </button>

            {expandedCategories.includes(category.id) && (
              <div style={{ paddingLeft: '12px', paddingRight: '4px', paddingTop: '4px' }}>
                {category.prompts.map((prompt, index) => (
                  <button
                    key={index}
                    onClick={() => handlePromptClick(prompt.text)}
                    style={{
                      width: '100%',
                      padding: '8px 12px',
                      marginBottom: '2px',
                      backgroundColor: 'rgba(255,255,255,0.03)',
                      border: '1px solid rgba(255,255,255,0.08)',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '8px',
                      color: 'rgba(255,255,255,0.8)',
                      fontSize: '13px',
                      textAlign: 'left',
                      transition: 'all 0.2s',
                      position: 'relative'
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(171, 104, 255, 0.15)';
                      e.currentTarget.style.borderColor = 'rgba(171, 104, 255, 0.3)';
                      e.currentTarget.style.color = '#fff';
                    }}
                    onMouseLeave={(e) => {
                      e.currentTarget.style.backgroundColor = 'rgba(255,255,255,0.03)';
                      e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)';
                      e.currentTarget.style.color = 'rgba(255,255,255,0.8)';
                    }}
                  >
                    <div style={{ flex: 1 }}>
                      {prompt.text}
                    </div>
                    {prompt.badge && (
                      <span style={{
                        padding: '2px 6px',
                        backgroundColor: prompt.badge === 'Popular' ? 'rgba(34, 197, 94, 0.2)' :
                                       prompt.badge === 'New' ? 'rgba(59, 130, 246, 0.2)' :
                                       prompt.badge === 'Critical' ? 'rgba(239, 68, 68, 0.2)' :
                                       'rgba(171, 104, 255, 0.2)',
                        color: prompt.badge === 'Popular' ? '#22c55e' :
                               prompt.badge === 'New' ? '#3b82f6' :
                               prompt.badge === 'Critical' ? '#ef4444' :
                               '#ab68ff',
                        fontSize: '10px',
                        borderRadius: '4px',
                        fontWeight: '600',
                        textTransform: 'uppercase',
                        letterSpacing: '0.5px'
                      }}>
                        {prompt.badge}
                      </span>
                    )}
                  </button>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Footer Tips */}
      <div style={{
        padding: '12px 16px',
        borderTop: '1px solid rgba(255,255,255,0.1)',
        backgroundColor: '#1f1f1f'
      }}>
        <div style={{
          display: 'flex',
          alignItems: 'center',
          gap: '8px',
          fontSize: '12px',
          color: 'rgba(255,255,255,0.5)'
        }}>
          <Sparkles size={14} style={{ color: '#ab68ff' }} />
          <span>Click any prompt to analyze instantly</span>
        </div>
      </div>
    </div>
  );
}