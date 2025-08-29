'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Search, Sparkles, TrendingUp, Target, DollarSign, ChevronRight, Play } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

export default function ExamplePromptsTestPage() {
  const [selectedPrompt, setSelectedPrompt] = useState('');
  const [hoveredCategory, setHoveredCategory] = useState<string | null>(null);
  const [inputValue, setInputValue] = useState('');
  const [isInputFocused, setIsInputFocused] = useState(false);

  // Inspired by Claude's categorized suggestions
  const promptCategories = {
    competitive: {
      title: '🥊 Competitive Analysis',
      icon: Target,
      prompts: [
        { text: 'stripe.com vs square.com', subtext: 'Payment giants compared' },
        { text: 'notion.so vs coda.io', subtext: 'Workspace tool battle' },
        { text: 'shopify.com vs bigcommerce', subtext: 'E-commerce platforms' },
        { text: 'slack.com vs teams', subtext: 'Communication showdown' }
      ]
    },
    revenue: {
      title: '💰 Revenue Opportunities',
      icon: DollarSign,
      prompts: [
        { text: 'Find $100K+ leaks on [domain]', subtext: 'Conversion blockers' },
        { text: 'Analyze checkout flow', subtext: 'Cart abandonment issues' },
        { text: 'Pricing page problems', subtext: 'Optimize for conversion' },
        { text: 'Trust signal audit', subtext: 'Build buyer confidence' }
      ]
    },
    growth: {
      title: '📈 Growth Tactics',
      icon: TrendingUp,
      prompts: [
        { text: 'SEO opportunities', subtext: 'Untapped keywords' },
        { text: 'Traffic channel gaps', subtext: 'Where competitors win' },
        { text: 'Content strategy audit', subtext: 'Missing topics' },
        { text: 'AI search optimization', subtext: 'ChatGPT visibility' }
      ]
    }
  };

  // Animated placeholder text (like ChatGPT)
  const placeholderExamples = [
    'stripe.com vs square.com',
    'Find revenue leaks on shopify.com',
    'SEO audit for notion.so',
    'Analyze tesla.com checkout'
  ];

  const [placeholderIndex, setPlaceholderIndex] = useState(0);

  React.useEffect(() => {
    const interval = setInterval(() => {
      setPlaceholderIndex((prev) => (prev + 1) % placeholderExamples.length);
    }, 3000);
    return () => clearInterval(interval);
  }, []);

  const handlePromptClick = (prompt: string) => {
    setSelectedPrompt(prompt);
    setInputValue(prompt);
    // In production, this would trigger the analysis
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-gray-50 to-white dark:from-gray-900 dark:to-gray-950">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-800 bg-white/80 dark:bg-gray-950/80 backdrop-blur-sm sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Link 
              href="/test-onboarding"
              className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Test Menu
            </Link>
            <div className="h-6 w-px bg-gray-300 dark:bg-gray-700" />
            <h1 className="text-lg font-semibold">Example Prompts Test</h1>
          </div>
        </div>
      </div>

      <div className="max-w-4xl mx-auto px-4 py-8">
        {/* Hero Section */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-full border border-blue-200 dark:border-blue-800 mb-4"
          >
            <Sparkles className="w-4 h-4 text-blue-600 dark:text-blue-400" />
            <span className="text-sm font-medium text-blue-700 dark:text-blue-300">
              AI Revenue Intelligence
            </span>
          </motion.div>
          
          <h1 className="text-4xl font-bold text-gray-900 dark:text-gray-100 mb-4">
            Find <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Hidden Revenue</span> in 60 Seconds
          </h1>
          
          <p className="text-lg text-gray-600 dark:text-gray-400">
            Enter any domain or click an example to start
          </p>
        </div>

        {/* Input Section with Animated Placeholder */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="relative mb-12"
        >
          <div className={`relative rounded-2xl border-2 transition-all ${
            isInputFocused 
              ? 'border-blue-500 shadow-lg shadow-blue-500/20' 
              : 'border-gray-200 dark:border-gray-700'
          }`}>
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            
            <input
              type="text"
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onFocus={() => setIsInputFocused(true)}
              onBlur={() => setIsInputFocused(false)}
              placeholder={placeholderExamples[placeholderIndex]}
              className="w-full pl-12 pr-32 py-4 bg-transparent text-lg focus:outline-none"
            />
            
            <button className="absolute right-2 top-1/2 -translate-y-1/2 px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium rounded-xl hover:shadow-lg transition-all">
              Analyze
            </button>
          </div>
          
          {/* Animated hint text */}
          <AnimatePresence mode="wait">
            <motion.p
              key={placeholderIndex}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -10 }}
              className="absolute -bottom-6 left-12 text-sm text-gray-500"
            >
              Try: <span className="font-mono text-blue-600 dark:text-blue-400">{placeholderExamples[placeholderIndex]}</span>
            </motion.p>
          </AnimatePresence>
        </motion.div>

        {/* Quick Demo Button */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="flex justify-center mb-8"
        >
          <button className="group flex items-center gap-3 px-6 py-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 hover:border-blue-400 dark:hover:border-blue-600 hover:shadow-lg transition-all">
            <div className="p-2 bg-gradient-to-br from-amber-400 to-orange-500 rounded-lg">
              <Play className="w-4 h-4 text-white" />
            </div>
            <div className="text-left">
              <div className="font-semibold text-gray-900 dark:text-gray-100">
                Watch 10-Second Demo
              </div>
              <div className="text-xs text-gray-500">See real analysis in action</div>
            </div>
            <ChevronRight className="w-5 h-5 text-gray-400 group-hover:translate-x-1 transition-transform" />
          </button>
        </motion.div>

        {/* Category Cards */}
        <div className="grid gap-6 md:grid-cols-3 mb-8">
          {Object.entries(promptCategories).map(([key, category], categoryIndex) => {
            const Icon = category.icon;
            return (
              <motion.div
                key={key}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 + categoryIndex * 0.1 }}
                onMouseEnter={() => setHoveredCategory(key)}
                onMouseLeave={() => setHoveredCategory(null)}
                className="relative"
              >
                <div className={`bg-white dark:bg-gray-800 rounded-xl border transition-all ${
                  hoveredCategory === key 
                    ? 'border-blue-400 dark:border-blue-600 shadow-xl shadow-blue-500/10' 
                    : 'border-gray-200 dark:border-gray-700'
                }`}>
                  {/* Category Header */}
                  <div className="p-4 border-b border-gray-100 dark:border-gray-700">
                    <div className="flex items-center gap-3">
                      <div className={`p-2 rounded-lg transition-colors ${
                        hoveredCategory === key
                          ? 'bg-gradient-to-br from-blue-500 to-purple-600'
                          : 'bg-gray-100 dark:bg-gray-700'
                      }`}>
                        <Icon className={`w-5 h-5 ${
                          hoveredCategory === key ? 'text-white' : 'text-gray-600 dark:text-gray-400'
                        }`} />
                      </div>
                      <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                        {category.title}
                      </h3>
                    </div>
                  </div>
                  
                  {/* Prompts List */}
                  <div className="p-2">
                    {category.prompts.map((prompt, index) => (
                      <button
                        key={index}
                        onClick={() => handlePromptClick(prompt.text)}
                        className="w-full text-left px-3 py-2.5 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors group"
                      >
                        <div className="flex items-center justify-between">
                          <div>
                            <div className="font-medium text-sm text-gray-900 dark:text-gray-100 group-hover:text-blue-600 dark:group-hover:text-blue-400">
                              {prompt.text}
                            </div>
                            <div className="text-xs text-gray-500 dark:text-gray-400">
                              {prompt.subtext}
                            </div>
                          </div>
                          <ChevronRight className="w-4 h-4 text-gray-400 opacity-0 group-hover:opacity-100 group-hover:translate-x-1 transition-all" />
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
                
                {/* Hover Glow Effect */}
                {hoveredCategory === key && (
                  <div className="absolute inset-0 rounded-xl bg-gradient-to-r from-blue-500/10 to-purple-500/10 pointer-events-none animate-pulse" />
                )}
              </motion.div>
            );
          })}
        </div>

        {/* Selected Prompt Display */}
        {selectedPrompt && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl border border-blue-200 dark:border-blue-700"
          >
            <h3 className="font-semibold mb-2">Ready to analyze:</h3>
            <p className="text-lg font-mono text-blue-600 dark:text-blue-400">{selectedPrompt}</p>
            <p className="text-sm text-gray-600 dark:text-gray-400 mt-2">
              This will run a comprehensive analysis including revenue opportunities, competitive gaps, and growth tactics.
            </p>
          </motion.div>
        )}

        {/* Features Grid */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.6 }}
          className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-12"
        >
          {[
            { label: 'Real Testing', value: 'Browser automation' },
            { label: 'Traffic Data', value: 'Actual visitors' },
            { label: 'Revenue Focus', value: '$100K+ findings' },
            { label: 'Quick Fixes', value: '<1 week tasks' }
          ].map((feature, index) => (
            <div key={index} className="text-center p-4 bg-gray-50 dark:bg-gray-800 rounded-lg">
              <div className="text-2xl font-bold text-gray-900 dark:text-gray-100">
                {feature.label}
              </div>
              <div className="text-sm text-gray-500 dark:text-gray-400">
                {feature.value}
              </div>
            </div>
          ))}
        </motion.div>
      </div>
    </div>
  );
}