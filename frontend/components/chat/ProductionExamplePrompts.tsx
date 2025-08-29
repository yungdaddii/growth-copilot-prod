'use client';

import React, { useState } from 'react';
import { ChevronRight, Sparkles } from 'lucide-react';

interface ProductionExamplePromptsProps {
  onSelectPrompt: (prompt: string) => void;
  isVisible: boolean;
}

export default function ProductionExamplePrompts({ onSelectPrompt, isVisible }: ProductionExamplePromptsProps) {
  const [hoveredPrompt, setHoveredPrompt] = useState<number | null>(null);

  // Simplified, focused prompts
  const examplePrompts = [
    {
      category: 'Popular',
      prompts: [
        { text: 'stripe.com vs square.com', label: 'Compare payment platforms' },
        { text: 'Find revenue leaks on shopify.com', label: 'E-commerce analysis' },
        { text: 'notion.so growth opportunities', label: 'SaaS growth tactics' },
        { text: 'SEO audit for techcrunch.com', label: 'Content strategy' }
      ]
    }
  ];

  if (!isVisible) return null;

  return (
    <div className="w-full max-w-3xl mx-auto px-4 py-3">
        <div className="flex items-center gap-2 mb-3 text-sm text-gray-500 dark:text-gray-400">
          <Sparkles className="w-4 h-4" />
          <span>Try these examples:</span>
        </div>
        
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {examplePrompts[0].prompts.map((prompt, index) => (
            <button
              key={index}
              onClick={() => onSelectPrompt(prompt.text)}
              onMouseEnter={() => setHoveredPrompt(index)}
              onMouseLeave={() => setHoveredPrompt(null)}
              className={`
                relative text-left p-3 rounded-lg border transition-all
                ${hoveredPrompt === index 
                  ? 'border-blue-400 dark:border-blue-600 bg-blue-50/50 dark:bg-blue-900/20' 
                  : 'border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 hover:border-gray-300 dark:hover:border-gray-600'
                }
              `}
            >
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="font-medium text-sm text-gray-900 dark:text-gray-100">
                    {prompt.text}
                  </div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                    {prompt.label}
                  </div>
                </div>
                <ChevronRight className={`
                  w-4 h-4 transition-all mt-0.5
                  ${hoveredPrompt === index 
                    ? 'text-blue-500 translate-x-0.5' 
                    : 'text-gray-400 opacity-50'
                  }
                `} />
              </div>
            </button>
          ))}
        </div>
      </div>
  );
}