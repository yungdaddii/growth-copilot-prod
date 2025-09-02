"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { ArrowLeft, Check, Zap, TrendingUp, Shield, Sparkles, CreditCard, Loader2 } from 'lucide-react';

export default function BillingPage() {
  const router = useRouter();
  const { user, profile } = useAuth();
  const [selectedPlan, setSelectedPlan] = useState<'free' | 'pro' | 'enterprise'>('free');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!user) {
      router.push('/');
      return;
    }

    if (profile?.subscriptionTier) {
      setSelectedPlan(profile.subscriptionTier as 'free' | 'pro' | 'enterprise');
    }
  }, [user, profile, router]);

  const styles = {
    container: {
      minHeight: '100vh',
      backgroundColor: '#0a0a0a',
      color: 'white',
    },
    header: {
      borderBottom: '1px solid rgba(255, 255, 255, 0.1)',
      padding: '20px',
    },
    headerContent: {
      maxWidth: '1200px',
      margin: '0 auto',
      display: 'flex',
      alignItems: 'center',
      gap: '16px',
    },
    backButton: {
      padding: '8px',
      backgroundColor: 'transparent',
      border: '1px solid rgba(255, 255, 255, 0.2)',
      borderRadius: '8px',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      transition: 'all 0.2s',
    },
    title: {
      fontSize: '24px',
      fontWeight: '600',
    },
    content: {
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '40px 20px',
    },
    section: {
      marginBottom: '40px',
    },
    sectionTitle: {
      fontSize: '20px',
      fontWeight: '600',
      marginBottom: '12px',
      color: 'rgba(255, 255, 255, 0.9)',
    },
    sectionSubtitle: {
      fontSize: '14px',
      color: 'rgba(255, 255, 255, 0.6)',
      marginBottom: '32px',
    },
    plansGrid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
      gap: '24px',
      marginBottom: '40px',
    },
    planCard: {
      backgroundColor: '#1a1a1a',
      border: '2px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '12px',
      padding: '32px',
      position: 'relative' as const,
      transition: 'all 0.3s',
      cursor: 'pointer',
    },
    planCardActive: {
      borderColor: '#ab68ff',
      backgroundColor: 'rgba(171, 104, 255, 0.05)',
    },
    planCardRecommended: {
      borderColor: 'rgba(171, 104, 255, 0.3)',
    },
    recommendedBadge: {
      position: 'absolute' as const,
      top: '-12px',
      left: '50%',
      transform: 'translateX(-50%)',
      backgroundColor: '#ab68ff',
      color: 'white',
      padding: '4px 16px',
      borderRadius: '20px',
      fontSize: '12px',
      fontWeight: '600',
    },
    planName: {
      fontSize: '24px',
      fontWeight: '600',
      marginBottom: '8px',
    },
    planPrice: {
      display: 'flex',
      alignItems: 'baseline',
      gap: '8px',
      marginBottom: '24px',
    },
    priceAmount: {
      fontSize: '36px',
      fontWeight: '700',
      color: '#ab68ff',
    },
    pricePeriod: {
      fontSize: '16px',
      color: 'rgba(255, 255, 255, 0.6)',
    },
    planFeatures: {
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '12px',
      marginBottom: '24px',
    },
    feature: {
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      fontSize: '14px',
      color: 'rgba(255, 255, 255, 0.8)',
    },
    featureIcon: {
      flexShrink: 0,
      color: '#22c55e',
    },
    selectButton: {
      width: '100%',
      padding: '12px',
      backgroundColor: 'transparent',
      color: '#ab68ff',
      border: '2px solid #ab68ff',
      borderRadius: '8px',
      fontSize: '14px',
      fontWeight: '600',
      cursor: 'pointer',
      transition: 'all 0.2s',
    },
    selectButtonActive: {
      backgroundColor: '#ab68ff',
      color: 'white',
    },
    currentPlanBadge: {
      width: '100%',
      padding: '12px',
      backgroundColor: 'rgba(34, 197, 94, 0.1)',
      color: '#22c55e',
      border: '2px solid rgba(34, 197, 94, 0.3)',
      borderRadius: '8px',
      fontSize: '14px',
      fontWeight: '600',
      textAlign: 'center' as const,
    },
    usageCard: {
      backgroundColor: '#1a1a1a',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '12px',
      padding: '24px',
    },
    usageHeader: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '20px',
    },
    usageTitle: {
      fontSize: '16px',
      fontWeight: '600',
    },
    usageAmount: {
      fontSize: '24px',
      fontWeight: '700',
      color: '#ab68ff',
    },
    progressBar: {
      width: '100%',
      height: '8px',
      backgroundColor: 'rgba(255, 255, 255, 0.1)',
      borderRadius: '4px',
      overflow: 'hidden',
      marginBottom: '12px',
    },
    progressFill: {
      height: '100%',
      backgroundColor: '#ab68ff',
      borderRadius: '4px',
      transition: 'width 0.3s',
    },
    usageText: {
      fontSize: '14px',
      color: 'rgba(255, 255, 255, 0.6)',
    },
    paymentSection: {
      backgroundColor: '#1a1a1a',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '12px',
      padding: '24px',
    },
    paymentMethod: {
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      padding: '16px',
      backgroundColor: 'rgba(255, 255, 255, 0.02)',
      borderRadius: '8px',
      marginBottom: '16px',
    },
    paymentInfo: {
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
    },
    cardIcon: {
      padding: '8px',
      backgroundColor: 'rgba(171, 104, 255, 0.1)',
      borderRadius: '8px',
    },
    addPaymentButton: {
      width: '100%',
      padding: '12px',
      backgroundColor: 'transparent',
      color: '#ab68ff',
      border: '1px solid rgba(171, 104, 255, 0.3)',
      borderRadius: '8px',
      fontSize: '14px',
      fontWeight: '500',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '8px',
      transition: 'all 0.2s',
    },
  };

  const plans = [
    {
      id: 'free',
      name: 'Free',
      price: 0,
      analyses: 10,
      features: [
        'Basic website analysis',
        '10 analyses per month',
        'Core metrics & insights',
        'Email support',
      ],
    },
    {
      id: 'pro',
      name: 'Pro',
      price: 29,
      analyses: 100,
      recommended: true,
      features: [
        'Advanced AI-powered analysis',
        '100 analyses per month',
        'Competitor comparison',
        'Custom recommendations',
        'Priority support',
        'Export reports',
      ],
    },
    {
      id: 'enterprise',
      name: 'Enterprise',
      price: 99,
      analyses: 'Unlimited',
      features: [
        'Everything in Pro',
        'Unlimited analyses',
        'API access',
        'Custom integrations',
        'Dedicated account manager',
        'SLA guarantee',
      ],
    },
  ];

  const handleUpgrade = (planId: string) => {
    setLoading(true);
    // Simulate upgrade process
    setTimeout(() => {
      setLoading(false);
      alert(`Upgrade to ${planId} plan coming soon!`);
    }, 1500);
  };

  if (!user) {
    return null;
  }

  const currentPlan = profile?.subscriptionTier || 'free';
  const usagePercentage = profile ? (profile.monthlyAnalysesUsed / profile.monthlyAnalysesLimit) * 100 : 0;

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <div style={styles.headerContent}>
          <button
            onClick={() => router.push('/')}
            style={styles.backButton}
            onMouseEnter={(e) => {
              e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.05)';
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
            }}
          >
            <ArrowLeft size={20} color="white" />
          </button>
          <h1 style={styles.title}>Billing & Subscription</h1>
        </div>
      </div>

      <div style={styles.content}>
        {/* Current Usage */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Current Usage</h2>
          <div style={styles.usageCard}>
            <div style={styles.usageHeader}>
              <div>
                <div style={styles.usageTitle}>Monthly Analyses</div>
                <div style={styles.usageAmount}>
                  {profile?.monthlyAnalysesUsed || 0} / {profile?.monthlyAnalysesLimit || 10}
                </div>
              </div>
              <div style={{ textAlign: 'right' as const }}>
                <div style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.5)', marginBottom: '4px' }}>
                  Resets on
                </div>
                <div style={{ fontSize: '14px', fontWeight: '500' }}>
                  {new Date(new Date().getFullYear(), new Date().getMonth() + 1, 1).toLocaleDateString()}
                </div>
              </div>
            </div>
            <div style={styles.progressBar}>
              <div style={{ ...styles.progressFill, width: `${Math.min(usagePercentage, 100)}%` }} />
            </div>
            <div style={styles.usageText}>
              {usagePercentage >= 80 && (
                <span style={{ color: '#f59e0b' }}>
                  ⚠️ You've used {Math.round(usagePercentage)}% of your monthly limit
                </span>
              )}
              {usagePercentage < 80 && (
                <span>
                  {(profile?.monthlyAnalysesLimit || 10) - (profile?.monthlyAnalysesUsed || 0)} analyses remaining this month
                </span>
              )}
            </div>
          </div>
        </div>

        {/* Subscription Plans */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Subscription Plans</h2>
          <p style={styles.sectionSubtitle}>
            Choose the plan that best fits your needs. Upgrade or downgrade anytime.
          </p>
          
          <div style={styles.plansGrid}>
            {plans.map((plan) => (
              <div
                key={plan.id}
                style={{
                  ...styles.planCard,
                  ...(plan.recommended ? styles.planCardRecommended : {}),
                  ...(selectedPlan === plan.id ? styles.planCardActive : {}),
                }}
                onClick={() => setSelectedPlan(plan.id as any)}
                onMouseEnter={(e) => {
                  if (selectedPlan !== plan.id) {
                    e.currentTarget.style.borderColor = 'rgba(171, 104, 255, 0.5)';
                    e.currentTarget.style.transform = 'translateY(-4px)';
                  }
                }}
                onMouseLeave={(e) => {
                  if (selectedPlan !== plan.id) {
                    e.currentTarget.style.borderColor = plan.recommended ? 
                      'rgba(171, 104, 255, 0.3)' : 'rgba(255, 255, 255, 0.1)';
                    e.currentTarget.style.transform = 'translateY(0)';
                  }
                }}
              >
                {plan.recommended && (
                  <div style={styles.recommendedBadge}>
                    <Sparkles size={12} style={{ display: 'inline', marginRight: '4px' }} />
                    Most Popular
                  </div>
                )}
                
                <div style={styles.planName}>{plan.name}</div>
                <div style={styles.planPrice}>
                  <span style={styles.priceAmount}>${plan.price}</span>
                  <span style={styles.pricePeriod}>/month</span>
                </div>
                
                <div style={styles.planFeatures}>
                  {plan.features.map((feature, index) => (
                    <div key={index} style={styles.feature}>
                      <Check size={16} style={styles.featureIcon} />
                      <span>{feature}</span>
                    </div>
                  ))}
                </div>
                
                {currentPlan === plan.id ? (
                  <div style={styles.currentPlanBadge}>
                    Current Plan
                  </div>
                ) : (
                  <button
                    style={{
                      ...styles.selectButton,
                      ...(selectedPlan === plan.id ? styles.selectButtonActive : {}),
                    }}
                    onClick={(e) => {
                      e.stopPropagation();
                      handleUpgrade(plan.id);
                    }}
                    onMouseEnter={(e) => {
                      e.currentTarget.style.backgroundColor = '#ab68ff';
                      e.currentTarget.style.color = 'white';
                    }}
                    onMouseLeave={(e) => {
                      if (selectedPlan !== plan.id) {
                        e.currentTarget.style.backgroundColor = 'transparent';
                        e.currentTarget.style.color = '#ab68ff';
                      }
                    }}
                    disabled={loading}
                  >
                    {loading ? (
                      <>
                        <Loader2 size={16} className="animate-spin" />
                        Processing...
                      </>
                    ) : (
                      <>Upgrade to {plan.name}</>
                    )}
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Payment Methods */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Payment Methods</h2>
          <div style={styles.paymentSection}>
            {currentPlan !== 'free' ? (
              <div style={styles.paymentMethod}>
                <div style={styles.paymentInfo}>
                  <div style={styles.cardIcon}>
                    <CreditCard size={20} color="#ab68ff" />
                  </div>
                  <div>
                    <div style={{ fontSize: '14px', fontWeight: '500' }}>
                      •••• •••• •••• 4242
                    </div>
                    <div style={{ fontSize: '12px', color: 'rgba(255, 255, 255, 0.5)' }}>
                      Expires 12/25
                    </div>
                  </div>
                </div>
                <button
                  style={{
                    padding: '6px 12px',
                    backgroundColor: 'transparent',
                    color: 'rgba(255, 255, 255, 0.6)',
                    border: '1px solid rgba(255, 255, 255, 0.1)',
                    borderRadius: '6px',
                    fontSize: '12px',
                    cursor: 'pointer',
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.3)';
                    e.currentTarget.style.color = 'rgba(255, 255, 255, 0.8)';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                    e.currentTarget.style.color = 'rgba(255, 255, 255, 0.6)';
                  }}
                >
                  Update
                </button>
              </div>
            ) : (
              <div style={{ textAlign: 'center' as const, padding: '32px' }}>
                <CreditCard size={48} color="rgba(255, 255, 255, 0.2)" style={{ marginBottom: '16px' }} />
                <p style={{ fontSize: '14px', color: 'rgba(255, 255, 255, 0.6)', marginBottom: '16px' }}>
                  No payment method on file
                </p>
                <button
                  style={styles.addPaymentButton}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.backgroundColor = 'rgba(171, 104, 255, 0.05)';
                    e.currentTarget.style.borderColor = '#ab68ff';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.backgroundColor = 'transparent';
                    e.currentTarget.style.borderColor = 'rgba(171, 104, 255, 0.3)';
                  }}
                >
                  <CreditCard size={16} />
                  Add Payment Method
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}