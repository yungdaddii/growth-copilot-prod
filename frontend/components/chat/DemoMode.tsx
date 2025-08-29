'use client';

import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Sparkles, Play, X, TrendingUp, AlertCircle, DollarSign } from 'lucide-react';

interface DemoModeProps {
  onClose: () => void;
  onTryYourOwn: (domain: string) => void;
}

export default function DemoMode({ onClose, onTryYourOwn }: DemoModeProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  // Pre-recorded demo analysis results
  const demoSteps = [
    {
      type: 'user',
      message: 'Analyze notion.so',
      delay: 0
    },
    {
      type: 'assistant',
      message: '🔍 Scanning notion.so and identifying competitors...',
      delay: 1000
    },
    {
      type: 'assistant',
      message: '⚡ Found 3 critical conversion blockers worth $847K/year',
      delay: 2500,
      highlight: true
    },
    {
      type: 'result',
      title: '🚨 Your signup form has 11 required fields',
      content: 'Competitors average 3 fields. Each extra field costs you ~7% in conversions.',
      impact: '$34,000/month',
      fix: 'Reduce to email + password only',
      delay: 4000
    },
    {
      type: 'result',
      title: '💰 No transparent pricing page',
      content: '67% of B2B buyers eliminate vendors without public pricing. Slack and Monday show pricing.',
      impact: '$52,000/month',
      fix: 'Add 3-tier pricing page',
      delay: 5500
    },
    {
      type: 'result',
      title: '📱 Mobile experience broken',
      content: 'Horizontal scroll on mobile. 58% of your traffic is mobile.',
      impact: '$18,000/month',
      fix: '2-hour CSS fix',
      delay: 7000
    },
    {
      type: 'assistant',
      message: '✅ Analysis complete! Found $104K/month in quick wins that take <1 week to implement.',
      delay: 8500,
      highlight: true
    }
  ];

  const startDemo = () => {
    setIsPlaying(true);
    setCurrentStep(0);
    
    // Play through the demo
    demoSteps.forEach((step, index) => {
      setTimeout(() => {
        setCurrentStep(index + 1);
        if (index === demoSteps.length - 1) {
          setTimeout(() => setIsPlaying(false), 2000);
        }
      }, step.delay);
    });
  };

  return (
    <div className="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="bg-white dark:bg-gray-900 rounded-2xl shadow-2xl max-w-4xl w-full max-h-[90vh] overflow-hidden"
      >
        {/* Header */}
        <div className="border-b border-gray-200 dark:border-gray-700 p-6 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
              <Sparkles className="w-5 h-5 text-white" />
            </div>
            <div>
              <h2 className="text-xl font-semibold">See Growth Co-pilot in Action</h2>
              <p className="text-sm text-gray-500">Watch a 10-second demo of real analysis</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Demo Content */}
        <div className="p-6 space-y-4 max-h-[60vh] overflow-y-auto">
          {!isPlaying && currentStep === 0 && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center py-12"
            >
              <button
                onClick={startDemo}
                className="group relative inline-flex items-center gap-3 px-8 py-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-xl hover:shadow-lg transition-all hover:scale-105"
              >
                <Play className="w-5 h-5" />
                Watch 10-Second Demo
                <div className="absolute inset-0 rounded-xl bg-white opacity-0 group-hover:opacity-10 transition-opacity" />
              </button>
              <p className="mt-4 text-sm text-gray-500">
                See how we find $100K+ in monthly revenue opportunities
              </p>
            </motion.div>
          )}

          {/* Demo Messages */}
          <AnimatePresence mode="sync">
            {demoSteps.slice(0, currentStep).map((step, index) => {
              if (step.type === 'user') {
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: 20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex justify-end"
                  >
                    <div className="bg-blue-600 text-white px-4 py-2 rounded-2xl rounded-br-sm max-w-xs">
                      {step.message}
                    </div>
                  </motion.div>
                );
              }

              if (step.type === 'assistant') {
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, x: -20 }}
                    animate={{ opacity: 1, x: 0 }}
                    className="flex justify-start"
                  >
                    <div className={`px-4 py-2 rounded-2xl rounded-bl-sm max-w-md ${
                      step.highlight 
                        ? 'bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border border-amber-200 dark:border-amber-800 font-medium'
                        : 'bg-gray-100 dark:bg-gray-800'
                    }`}>
                      {step.message}
                    </div>
                  </motion.div>
                );
              }

              if (step.type === 'result') {
                return (
                  <motion.div
                    key={index}
                    initial={{ opacity: 0, y: 20, scale: 0.95 }}
                    animate={{ opacity: 1, y: 0, scale: 1 }}
                    className="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-850 rounded-xl p-4 border border-gray-200 dark:border-gray-700"
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="font-semibold text-gray-900 dark:text-gray-100">
                        {step.title}
                      </h3>
                      <span className="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-sm font-semibold rounded">
                        {step.impact}
                      </span>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                      {step.content}
                    </p>
                    <div className="flex items-center gap-2 text-sm">
                      <span className="text-green-600 dark:text-green-400 font-medium">
                        Fix: {step.fix}
                      </span>
                    </div>
                  </motion.div>
                );
              }

              return null;
            })}
          </AnimatePresence>

          {/* Call to Action */}
          {!isPlaying && currentStep > 0 && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="mt-8 p-6 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-xl border border-blue-200 dark:border-blue-800"
            >
              <h3 className="text-lg font-semibold mb-2">Ready to find YOUR hidden revenue?</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                Get the same analysis for your website in 60 seconds
              </p>
              <div className="flex gap-3">
                <button
                  onClick={() => onTryYourOwn('')}
                  className="px-6 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium rounded-lg hover:shadow-lg transition-all"
                >
                  Analyze My Site
                </button>
                <button
                  onClick={() => startDemo()}
                  className="px-6 py-2 bg-gray-200 dark:bg-gray-700 font-medium rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors"
                >
                  Replay Demo
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </motion.div>
    </div>
  );
}