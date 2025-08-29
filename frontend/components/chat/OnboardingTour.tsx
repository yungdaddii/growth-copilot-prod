'use client';

import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  X, ChevronRight, Check, Sparkles, 
  Target, DollarSign, Clock, ArrowRight 
} from 'lucide-react';

interface TourStep {
  id: string;
  title: string;
  description: string;
  target: string; // CSS selector for element to highlight
  position: 'top' | 'bottom' | 'left' | 'right';
  action?: {
    label: string;
    onClick: () => void;
  };
}

interface OnboardingTourProps {
  onComplete: () => void;
  onSkip: () => void;
}

export default function OnboardingTour({ onComplete, onSkip }: OnboardingTourProps) {
  const [currentStep, setCurrentStep] = useState(0);
  const [highlightPosition, setHighlightPosition] = useState({ top: 0, left: 0, width: 0, height: 0 });

  const steps: TourStep[] = [
    {
      id: 'welcome',
      title: 'Find $100K+ in Hidden Revenue 💰',
      description: 'Growth Co-pilot analyzes any website in 60 seconds and shows you exactly how to increase conversions',
      target: '.main-container',
      position: 'bottom'
    },
    {
      id: 'input',
      title: 'Enter Any Domain',
      description: 'Type your website or a competitor\'s domain. We\'ll analyze everything from conversion flows to pricing strategy.',
      target: '.domain-input',
      position: 'top',
      action: {
        label: 'Try stripe.com',
        onClick: () => {
          const input = document.querySelector('.domain-input') as HTMLInputElement;
          if (input) {
            input.value = 'stripe.com';
            input.dispatchEvent(new Event('input', { bubbles: true }));
          }
        }
      }
    },
    {
      id: 'examples',
      title: 'Or Click an Example',
      description: 'Not sure where to start? Click any example domain to see instant analysis.',
      target: '.example-prompts',
      position: 'top'
    },
    {
      id: 'analysis',
      title: 'Get Actionable Insights',
      description: 'We don\'t just find problems - we calculate exact revenue impact and give you the fix with implementation time.',
      target: '.chat-messages',
      position: 'right'
    },
    {
      id: 'value',
      title: 'What Makes Us Different',
      description: 'Unlike generic AI, we use real traffic data, browser testing, and competitor analysis to find opportunities others miss.',
      target: '.main-container',
      position: 'bottom'
    }
  ];

  useEffect(() => {
    updateHighlightPosition();
    window.addEventListener('resize', updateHighlightPosition);
    return () => window.removeEventListener('resize', updateHighlightPosition);
  }, [currentStep]);

  const updateHighlightPosition = () => {
    const step = steps[currentStep];
    const element = document.querySelector(step.target);
    if (element) {
      const rect = element.getBoundingClientRect();
      setHighlightPosition({
        top: rect.top - 8,
        left: rect.left - 8,
        width: rect.width + 16,
        height: rect.height + 16
      });
    }
  };

  const nextStep = () => {
    if (currentStep < steps.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete();
    }
  };

  const prevStep = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const goToStep = (index: number) => {
    setCurrentStep(index);
  };

  const currentStepData = steps[currentStep];

  const getTooltipPosition = () => {
    const pos = highlightPosition;
    const tooltip = { top: 0, left: 0 };

    switch (currentStepData.position) {
      case 'top':
        tooltip.top = pos.top - 20;
        tooltip.left = pos.left + pos.width / 2;
        break;
      case 'bottom':
        tooltip.top = pos.top + pos.height + 20;
        tooltip.left = pos.left + pos.width / 2;
        break;
      case 'left':
        tooltip.top = pos.top + pos.height / 2;
        tooltip.left = pos.left - 20;
        break;
      case 'right':
        tooltip.top = pos.top + pos.height / 2;
        tooltip.left = pos.left + pos.width + 20;
        break;
    }

    return tooltip;
  };

  return (
    <AnimatePresence>
      {/* Backdrop */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 bg-black/50 z-40"
        onClick={onSkip}
      />

      {/* Highlight Box */}
      <motion.div
        className="fixed z-50 pointer-events-none border-2 border-blue-500 rounded-lg"
        initial={false}
        animate={{
          top: highlightPosition.top,
          left: highlightPosition.left,
          width: highlightPosition.width,
          height: highlightPosition.height
        }}
        transition={{ type: 'spring', damping: 20 }}
      >
        <div className="absolute inset-0 bg-blue-500/10 rounded-lg animate-pulse" />
      </motion.div>

      {/* Tooltip */}
      <motion.div
        className="fixed z-50 bg-white dark:bg-gray-900 rounded-xl shadow-2xl p-6 max-w-md"
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ 
          opacity: 1, 
          scale: 1,
          ...getTooltipPosition()
        }}
        exit={{ opacity: 0, scale: 0.9 }}
        style={{
          transform: `translate(${
            currentStepData.position === 'left' ? '-100%' :
            currentStepData.position === 'right' ? '0%' : '-50%'
          }, ${
            currentStepData.position === 'top' ? '-100%' :
            currentStepData.position === 'bottom' ? '0%' : '-50%'
          })`
        }}
      >
        {/* Progress Dots */}
        <div className="flex gap-1 mb-4">
          {steps.map((_, index) => (
            <button
              key={index}
              onClick={() => goToStep(index)}
              className={`h-2 transition-all ${
                index === currentStep 
                  ? 'w-8 bg-blue-600' 
                  : index < currentStep
                  ? 'w-2 bg-green-500'
                  : 'w-2 bg-gray-300 dark:bg-gray-700'
              } rounded-full`}
            />
          ))}
        </div>

        {/* Content */}
        <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 mb-2">
          {currentStepData.title}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {currentStepData.description}
        </p>

        {/* Action Button */}
        {currentStepData.action && (
          <button
            onClick={currentStepData.action.onClick}
            className="w-full mb-4 px-4 py-2 bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 font-medium rounded-lg hover:bg-blue-200 dark:hover:bg-blue-900/50 transition-colors"
          >
            {currentStepData.action.label}
          </button>
        )}

        {/* Navigation */}
        <div className="flex items-center justify-between">
          <button
            onClick={onSkip}
            className="text-sm text-gray-500 hover:text-gray-700 dark:hover:text-gray-300"
          >
            Skip tour
          </button>
          
          <div className="flex gap-2">
            {currentStep > 0 && (
              <button
                onClick={prevStep}
                className="px-3 py-1.5 text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 rounded-lg transition-colors"
              >
                Back
              </button>
            )}
            <button
              onClick={nextStep}
              className="px-4 py-1.5 bg-blue-600 text-white text-sm font-medium rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-1"
            >
              {currentStep === steps.length - 1 ? (
                <>
                  Start Analyzing
                  <Check className="w-4 h-4" />
                </>
              ) : (
                <>
                  Next
                  <ChevronRight className="w-4 h-4" />
                </>
              )}
            </button>
          </div>
        </div>
      </motion.div>

      {/* Feature Callouts (shown on first step) */}
      {currentStep === 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3 }}
          className="fixed bottom-8 left-1/2 -translate-x-1/2 z-50 flex gap-4"
        >
          {[
            { icon: Target, label: 'Real Browser Testing', color: 'text-green-600' },
            { icon: DollarSign, label: 'Revenue Impact', color: 'text-blue-600' },
            { icon: Clock, label: '60 Second Analysis', color: 'text-purple-600' }
          ].map((feature, index) => (
            <motion.div
              key={feature.label}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: 0.4 + index * 0.1 }}
              className="bg-white dark:bg-gray-800 rounded-lg px-3 py-2 shadow-lg flex items-center gap-2"
            >
              <feature.icon className={`w-4 h-4 ${feature.color}`} />
              <span className="text-sm font-medium">{feature.label}</span>
            </motion.div>
          ))}
        </motion.div>
      )}
    </AnimatePresence>
  );
}