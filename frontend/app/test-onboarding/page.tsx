'use client';

import React from 'react';
import Link from 'next/link';
import { ArrowLeft } from 'lucide-react';

export default function TestOnboardingPage() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="border-b border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-950">
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="flex items-center gap-4">
            <Link 
              href="/"
              className="flex items-center gap-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-100"
            >
              <ArrowLeft className="w-4 h-4" />
              Back to Production
            </Link>
            <div className="h-6 w-px bg-gray-300 dark:bg-gray-700" />
            <h1 className="text-lg font-semibold">Onboarding Test Environment</h1>
            <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 text-xs font-medium rounded">
              TEST MODE
            </span>
          </div>
        </div>
      </div>

      {/* Test Options */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-xl font-semibold mb-6">Onboarding Feature Tests</h2>
          
          <div className="grid gap-4 md:grid-cols-2">
            <a 
              href="/test-onboarding/demo-mode"
              className="block p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
            >
              <h3 className="font-semibold mb-2">1. Demo Mode</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Pre-recorded analysis that plays automatically, showing value in 10 seconds
              </p>
            </a>

            <a 
              href="/test-onboarding/example-prompts"
              className="block p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
            >
              <h3 className="font-semibold mb-2">2. Example Prompts</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Clickable domain examples below the input field with animated suggestions
              </p>
            </a>

            <a 
              href="/test-onboarding/interactive-tour"
              className="block p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
            >
              <h3 className="font-semibold mb-2">3. Interactive Tour</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Step-by-step walkthrough with highlights and tooltips
              </p>
            </a>

            <a 
              href="/test-onboarding/all-features"
              className="block p-4 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-500 dark:hover:border-blue-400 transition-colors"
            >
              <h3 className="font-semibold mb-2">4. All Features Combined</h3>
              <p className="text-sm text-gray-600 dark:text-gray-400">
                Test all onboarding features together as they would appear to a new user
              </p>
            </a>
          </div>
        </div>

        {/* Preview Section */}
        <div className="mt-8 bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
          <h2 className="text-xl font-semibold mb-4">Proposed Onboarding Strategy</h2>
          
          <div className="space-y-4 text-sm">
            <div>
              <h3 className="font-semibold text-blue-600 dark:text-blue-400 mb-2">
                Goal: Get users to "aha moment" in under 10 seconds
              </h3>
              <p className="text-gray-600 dark:text-gray-400">
                Show them exactly what value they'll get before they even enter their domain.
              </p>
            </div>

            <div className="space-y-2">
              <h4 className="font-semibold">Option 1: Auto-Play Demo</h4>
              <ul className="list-disc list-inside text-gray-600 dark:text-gray-400 space-y-1">
                <li>Automatically starts playing when page loads</li>
                <li>Shows real analysis finding $100K+ opportunities</li>
                <li>Highlights specific issues: signup form, pricing, mobile</li>
                <li>Ends with "Try your domain" CTA</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h4 className="font-semibold">Option 2: Example Prompts</h4>
              <ul className="list-disc list-inside text-gray-600 dark:text-gray-400 space-y-1">
                <li>Shows 4-6 popular domains users can click</li>
                <li>Animated placeholder showing "Try: stripe.com"</li>
                <li>Categories: Popular, Competitors, By Industry</li>
                <li>Smart suggestions based on what they type</li>
              </ul>
            </div>

            <div className="space-y-2">
              <h4 className="font-semibold">Option 3: Interactive Tour</h4>
              <ul className="list-disc list-inside text-gray-600 dark:text-gray-400 space-y-1">
                <li>Highlights key areas with tooltips</li>
                <li>5 quick steps showing core value props</li>
                <li>Can skip at any time</li>
                <li>Only shows for first-time users</li>
              </ul>
            </div>

            <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
              <h4 className="font-semibold text-green-700 dark:text-green-300 mb-1">
                Recommendation: Combine all three
              </h4>
              <p className="text-green-600 dark:text-green-400">
                1. Quick tour on first visit → 2. Example prompts always visible → 3. Demo available via button
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}