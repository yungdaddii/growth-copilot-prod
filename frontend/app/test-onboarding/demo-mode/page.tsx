'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { ArrowLeft, Play, Pause, RotateCcw, Sparkles, ChevronRight } from 'lucide-react';

export default function DemoModeTestPage() {
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);

  const demoSteps = [
    { time: '0:00', type: 'user', message: 'Analyze notion.so' },
    { time: '0:01', type: 'bot', message: '🔍 Scanning notion.so and identifying competitors...' },
    { time: '0:03', type: 'bot', message: '⚡ Found 3 critical conversion blockers worth $847K/year', highlight: true },
    { 
      time: '0:05', 
      type: 'result',
      title: '🚨 Your signup form has 11 required fields',
      detail: 'Competitors average 3 fields. Each extra field costs ~7% in conversions.',
      impact: '$34,000/month',
      fix: 'Reduce to email + password only'
    },
    {
      time: '0:07',
      type: 'result', 
      title: '💰 No transparent pricing page',
      detail: '67% of B2B buyers eliminate vendors without public pricing.',
      impact: '$52,000/month',
      fix: 'Add 3-tier pricing page'
    },
    { time: '0:10', type: 'bot', message: '✅ Analysis complete! Found $104K/month in quick wins.', highlight: true }
  ];

  const playDemo = () => {
    setIsPlaying(true);
    setCurrentStep(0);
    
    // Simulate playing through steps
    let step = 0;
    const interval = setInterval(() => {
      step++;
      setCurrentStep(step);
      
      if (step >= demoSteps.length - 1) {
        clearInterval(interval);
        setIsPlaying(false);
      }
    }, 2000);
  };

  const resetDemo = () => {
    setCurrentStep(0);
    setIsPlaying(false);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950">
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
            <h1 className="text-lg font-semibold">Demo Mode Test</h1>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-8 grid gap-8 lg:grid-cols-2">
        {/* Left: Mockup */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Demo Mockup</h2>
          
          {/* Demo Container */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
            {/* Demo Header */}
            <div className="border-b border-gray-200 dark:border-gray-700 p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                  <Sparkles className="w-5 h-5 text-white" />
                </div>
                <div>
                  <h3 className="font-semibold">See Growth Co-pilot in Action</h3>
                  <p className="text-sm text-gray-500">10-second demo • Real analysis</p>
                </div>
              </div>
              
              {/* Playback Controls */}
              <div className="flex items-center gap-2">
                <button
                  onClick={isPlaying ? () => setIsPlaying(false) : playDemo}
                  className="p-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
                >
                  {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </button>
                <button
                  onClick={resetDemo}
                  className="p-2 bg-gray-200 dark:bg-gray-700 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600"
                >
                  <RotateCcw className="w-4 h-4" />
                </button>
              </div>
            </div>

            {/* Demo Timeline */}
            <div className="px-4 py-2 bg-gray-50 dark:bg-gray-900/50">
              <div className="flex items-center gap-2">
                <span className="text-xs text-gray-500">{demoSteps[currentStep]?.time || '0:00'}</span>
                <div className="flex-1 h-1 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
                  <div 
                    className="h-full bg-blue-600 transition-all duration-1000"
                    style={{ width: `${(currentStep / (demoSteps.length - 1)) * 100}%` }}
                  />
                </div>
                <span className="text-xs text-gray-500">0:10</span>
              </div>
            </div>

            {/* Demo Messages */}
            <div className="p-4 space-y-3 min-h-[400px] max-h-[400px] overflow-y-auto">
              {demoSteps.slice(0, currentStep + 1).map((step, index) => {
                if (step.type === 'user') {
                  return (
                    <div key={index} className="flex justify-end">
                      <div className="bg-blue-600 text-white px-4 py-2 rounded-2xl rounded-br-sm max-w-xs">
                        {step.message}
                      </div>
                    </div>
                  );
                }
                
                if (step.type === 'bot') {
                  return (
                    <div key={index} className="flex justify-start">
                      <div className={`px-4 py-2 rounded-2xl rounded-bl-sm max-w-md ${
                        step.highlight 
                          ? 'bg-gradient-to-r from-amber-50 to-orange-50 dark:from-amber-900/20 dark:to-orange-900/20 border border-amber-200 dark:border-amber-800 font-medium'
                          : 'bg-gray-100 dark:bg-gray-700'
                      }`}>
                        {step.message}
                      </div>
                    </div>
                  );
                }
                
                if (step.type === 'result') {
                  return (
                    <div key={index} className="bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-750 dark:to-gray-800 rounded-lg p-4 border border-gray-200 dark:border-gray-600">
                      <div className="flex items-start justify-between mb-2">
                        <h4 className="font-semibold">{step.title}</h4>
                        <span className="px-2 py-1 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400 text-sm font-semibold rounded">
                          {step.impact}
                        </span>
                      </div>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-2">{step.detail}</p>
                      <p className="text-sm text-green-600 dark:text-green-400 font-medium">
                        Fix: {step.fix}
                      </p>
                    </div>
                  );
                }
                
                return null;
              })}
              
              {/* Call to Action - Shows after demo completes */}
              {currentStep >= demoSteps.length - 1 && (
                <div className="mt-6 p-4 bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
                  <h4 className="font-semibold mb-2">Ready to find YOUR hidden revenue?</h4>
                  <p className="text-sm text-gray-600 dark:text-gray-400 mb-3">
                    Get the same analysis for your website in 60 seconds
                  </p>
                  <button className="w-full px-4 py-2 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-medium rounded-lg hover:shadow-lg transition-all flex items-center justify-center gap-2">
                    Analyze My Site
                    <ChevronRight className="w-4 h-4" />
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Right: Implementation Details */}
        <div>
          <h2 className="text-xl font-semibold mb-4">Implementation Details</h2>
          
          <div className="bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700 p-6 space-y-6">
            <div>
              <h3 className="font-semibold mb-3">How It Works</h3>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li className="flex items-start gap-2">
                  <span className="text-green-500 mt-0.5">✓</span>
                  <span>Auto-plays when user lands on page (can be disabled)</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500 mt-0.5">✓</span>
                  <span>Shows real analysis results with actual dollar amounts</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500 mt-0.5">✓</span>
                  <span>10-second duration to maintain attention</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-500 mt-0.5">✓</span>
                  <span>Ends with clear CTA to analyze their own site</span>
                </li>
              </ul>
            </div>

            <div>
              <h3 className="font-semibold mb-3">Key Messages</h3>
              <ol className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li>1. "Found 3 critical blockers worth $847K/year"</li>
                <li>2. Specific issue: "11 required fields in signup"</li>
                <li>3. Competitor comparison: "Competitors average 3 fields"</li>
                <li>4. Clear fix: "Reduce to email + password only"</li>
                <li>5. Impact quantified: "$34,000/month"</li>
              </ol>
            </div>

            <div>
              <h3 className="font-semibold mb-3">User Options</h3>
              <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                <li>• Can pause/play at any time</li>
                <li>• Can reset and replay</li>
                <li>• Can skip to enter their domain</li>
                <li>• Can click "Analyze My Site" CTA</li>
              </ul>
            </div>

            <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-700">
              <h3 className="font-semibold text-blue-700 dark:text-blue-300 mb-2">Expected Impact</h3>
              <p className="text-sm text-blue-600 dark:text-blue-400">
                Shows value in 10 seconds → 3x higher activation rate → Users understand ROI before entering domain
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}