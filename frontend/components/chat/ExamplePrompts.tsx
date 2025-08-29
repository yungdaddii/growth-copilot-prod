'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Zap, TrendingUp, Users, Search, DollarSign, 
  Target, Gauge, Globe, Sparkles, ArrowRight 
} from 'lucide-react';

interface ExamplePromptsProps {
  onSelectPrompt: (domain: string) => void;
  currentDomain?: string;
}

export default function ExamplePrompts({ onSelectPrompt, currentDomain }: ExamplePromptsProps) {
  const [selectedCategory, setSelectedCategory] = useState<string>('popular');
  const [animatedText, setAnimatedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  const [categories, setCategories] = useState({
    popular: {
      label: 'Popular Sites',
      icon: TrendingUp,
      examples: [
        { domain: 'stripe.com', description: 'Payment platform', impact: '$2.4M/year opportunity' },
        { domain: 'notion.so', description: 'Workspace tool', impact: '$1.8M/year opportunity' },
        { domain: 'linear.app', description: 'Issue tracking', impact: '$980K/year opportunity' },
        { domain: 'vercel.com', description: 'Deployment platform', impact: '$1.5M/year opportunity' }
      ]
    },
    competitors: {
      label: 'Your Competitors',
      icon: Users,
      examples: [] as Array<{ domain: string; description: string; impact: string }> // Will be populated based on user's domain
    },
    industries: {
      label: 'By Industry',
      icon: Globe,
      examples: [
        { domain: 'shopify.com', description: 'E-commerce leader', impact: 'See their strategy' },
        { domain: 'hubspot.com', description: 'Marketing automation', impact: 'Growth tactics' },
        { domain: 'monday.com', description: 'Project management', impact: 'Conversion secrets' },
        { domain: 'mailchimp.com', description: 'Email marketing', impact: 'Pricing strategy' }
      ]
    }
  });

  // Smart competitor suggestions based on user's domain
  useEffect(() => {
    if (currentDomain) {
      // This would be enhanced with actual competitor detection
      const competitorSuggestions = getSmartCompetitorSuggestions(currentDomain);
      setCategories(prev => ({
        ...prev,
        competitors: {
          ...prev.competitors,
          examples: competitorSuggestions
        }
      }));
    }
  }, [currentDomain]);

  // Animated placeholder text
  useEffect(() => {
    const examples = [
      'shopify.com',
      'stripe.com',
      'notion.so',
      'slack.com',
      'your-competitor.com'
    ];
    
    let currentIndex = 0;
    const typeWriter = () => {
      const example = examples[currentIndex];
      let charIndex = 0;
      
      setIsTyping(true);
      setAnimatedText('');
      
      const typeInterval = setInterval(() => {
        if (charIndex < example.length) {
          setAnimatedText(prev => prev + example[charIndex]);
          charIndex++;
        } else {
          clearInterval(typeInterval);
          setIsTyping(false);
          
          setTimeout(() => {
            currentIndex = (currentIndex + 1) % examples.length;
            setTimeout(typeWriter, 500);
          }, 2000);
        }
      }, 50);
    };

    typeWriter();
    
    return () => {
      setAnimatedText('');
    };
  }, []);

  function getSmartCompetitorSuggestions(domain: string): any[] {
    // Smart logic to suggest competitors based on domain
    const suggestions: Record<string, any[]> = {
      'stripe.com': [
        { domain: 'square.com', description: 'Payment competitor', impact: 'Compare strategies' },
        { domain: 'adyen.com', description: 'Enterprise payments', impact: 'Enterprise tactics' },
        { domain: 'paddle.com', description: 'SaaS payments', impact: 'SaaS focus' }
      ],
      'notion.so': [
        { domain: 'coda.io', description: 'Doc competitor', impact: 'Feature comparison' },
        { domain: 'airtable.com', description: 'Database focus', impact: 'Different approach' },
        { domain: 'clickup.com', description: 'All-in-one', impact: 'Marketing tactics' }
      ]
    };

    return suggestions[domain] || [
      { domain: 'competitor1.com', description: 'Main competitor', impact: 'Analyze strategy' },
      { domain: 'competitor2.com', description: 'Rising player', impact: 'Growth tactics' }
    ];
  }

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      {/* Animated Input Placeholder */}
      <div className="relative">
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="flex items-center gap-2 text-gray-400">
            <span className="text-sm">Try:</span>
            <span className="font-mono text-blue-600 dark:text-blue-400">
              {animatedText}
              {isTyping && (
                <motion.span
                  animate={{ opacity: [1, 0] }}
                  transition={{ duration: 0.5, repeat: Infinity }}
                  className="inline-block w-0.5 h-4 bg-blue-600 dark:bg-blue-400 ml-0.5"
                />
              )}
            </span>
          </div>
        </div>
      </div>

      {/* Quick Start Banner */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl p-4 border border-blue-200 dark:border-blue-800"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm">
              <Sparkles className="w-5 h-5 text-blue-600 dark:text-blue-400" />
            </div>
            <div>
              <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                Start with an example
              </h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Click any domain below to see instant analysis
              </p>
            </div>
          </div>
          <button
            onClick={() => onSelectPrompt('demo')}
            className="px-4 py-2 bg-white dark:bg-gray-800 text-blue-600 dark:text-blue-400 font-medium rounded-lg shadow-sm hover:shadow-md transition-all flex items-center gap-2"
          >
            <Play className="w-4 h-4" />
            Watch Demo
          </button>
        </div>
      </motion.div>

      {/* Category Tabs */}
      <div className="flex gap-2 border-b border-gray-200 dark:border-gray-700">
        {Object.entries(categories).map(([key, category]) => {
          const Icon = category.icon;
          return (
            <button
              key={key}
              onClick={() => setSelectedCategory(key)}
              className={`flex items-center gap-2 px-4 py-2 font-medium transition-all relative ${
                selectedCategory === key
                  ? 'text-blue-600 dark:text-blue-400'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              <Icon className="w-4 h-4" />
              {category.label}
              {category.examples.length > 0 && (
                <span className="ml-1 text-xs bg-gray-100 dark:bg-gray-800 px-1.5 py-0.5 rounded">
                  {category.examples.length}
                </span>
              )}
              {selectedCategory === key && (
                <motion.div
                  layoutId="activeTab"
                  className="absolute bottom-0 left-0 right-0 h-0.5 bg-blue-600 dark:bg-blue-400"
                />
              )}
            </button>
          );
        })}
      </div>

      {/* Example Cards */}
      <AnimatePresence mode="wait">
        <motion.div
          key={selectedCategory}
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
          className="grid grid-cols-1 md:grid-cols-2 gap-3"
        >
          {categories[selectedCategory as keyof typeof categories].examples.map((example, index) => (
            <motion.button
              key={example.domain}
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: index * 0.05 }}
              onClick={() => onSelectPrompt(example.domain)}
              className="group relative bg-white dark:bg-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600 hover:shadow-lg transition-all text-left"
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-gray-900 dark:text-gray-100">
                      {example.domain}
                    </span>
                    <ArrowRight className="w-4 h-4 text-gray-400 group-hover:text-blue-600 dark:group-hover:text-blue-400 group-hover:translate-x-1 transition-all" />
                  </div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">
                    {example.description}
                  </p>
                </div>
                <div className="ml-4">
                  <span className="text-xs font-medium text-green-600 dark:text-green-400 whitespace-nowrap">
                    {example.impact}
                  </span>
                </div>
              </div>
              
              {/* Hover Effect */}
              <div className="absolute inset-0 rounded-lg bg-gradient-to-r from-blue-600/5 to-purple-600/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none" />
            </motion.button>
          ))}
        </motion.div>
      </AnimatePresence>

      {/* Smart Suggestions */}
      {currentDomain && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="mt-6 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800"
        >
          <div className="flex items-start gap-3">
            <Target className="w-5 h-5 text-amber-600 dark:text-amber-400 mt-0.5" />
            <div>
              <h4 className="font-medium text-amber-900 dark:text-amber-100">
                Analyzing {currentDomain}?
              </h4>
              <p className="text-sm text-amber-700 dark:text-amber-300 mt-1">
                Try comparing with your top competitors for deeper insights
              </p>
              <div className="flex gap-2 mt-2">
                {getSmartCompetitorSuggestions(currentDomain).slice(0, 2).map(comp => (
                  <button
                    key={comp.domain}
                    onClick={() => onSelectPrompt(comp.domain)}
                    className="px-3 py-1 bg-amber-100 dark:bg-amber-800/30 text-amber-900 dark:text-amber-100 text-sm font-medium rounded hover:bg-amber-200 dark:hover:bg-amber-800/50 transition-colors"
                  >
                    vs {comp.domain}
                  </button>
                ))}
              </div>
            </div>
          </div>
        </motion.div>
      )}
    </div>
  );
}

function Play(props: React.SVGProps<SVGSVGElement>) {
  return (
    <svg
      {...props}
      xmlns="http://www.w3.org/2000/svg"
      width="24"
      height="24"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
    >
      <polygon points="5 3 19 12 5 21 5 3" />
    </svg>
  );
}