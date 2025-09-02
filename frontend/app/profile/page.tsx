"use client";

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/hooks/useAuth';
import { ArrowLeft, User, Mail, Building, Globe, Save, Loader2 } from 'lucide-react';
import { auth } from '@/lib/firebase';
import { updateProfile } from 'firebase/auth';

export default function ProfilePage() {
  const router = useRouter();
  const { user, profile, updateUserProfile } = useAuth();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [formData, setFormData] = useState({
    displayName: '',
    email: '',
    companyName: '',
    companyWebsite: '',
  });

  useEffect(() => {
    if (!user) {
      router.push('/');
      return;
    }

    if (profile) {
      setFormData({
        displayName: profile.displayName || '',
        email: profile.email || '',
        companyName: profile.companyName || '',
        companyWebsite: profile.companyWebsite || '',
      });
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
      maxWidth: '800px',
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
      maxWidth: '800px',
      margin: '0 auto',
      padding: '40px 20px',
    },
    section: {
      marginBottom: '40px',
    },
    sectionTitle: {
      fontSize: '18px',
      fontWeight: '600',
      marginBottom: '24px',
      color: 'rgba(255, 255, 255, 0.9)',
    },
    form: {
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '20px',
    },
    fieldGroup: {
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '8px',
    },
    label: {
      fontSize: '14px',
      fontWeight: '500',
      color: 'rgba(255, 255, 255, 0.7)',
    },
    inputWrapper: {
      position: 'relative' as const,
    },
    inputIcon: {
      position: 'absolute' as const,
      left: '12px',
      top: '50%',
      transform: 'translateY(-50%)',
      color: 'rgba(255, 255, 255, 0.4)',
    },
    input: {
      width: '100%',
      padding: '10px 12px 10px 40px',
      backgroundColor: '#1a1a1a',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '8px',
      color: 'white',
      fontSize: '14px',
      outline: 'none',
      transition: 'all 0.2s',
    },
    inputDisabled: {
      opacity: 0.6,
      cursor: 'not-allowed',
    },
    fieldRow: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '20px',
    },
    button: {
      padding: '10px 20px',
      backgroundColor: '#ab68ff',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      fontSize: '14px',
      fontWeight: '500',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '8px',
      transition: 'background-color 0.2s',
      width: 'fit-content',
    },
    buttonDisabled: {
      opacity: 0.5,
      cursor: 'not-allowed',
    },
    successMessage: {
      padding: '12px',
      backgroundColor: 'rgba(34, 197, 94, 0.1)',
      border: '1px solid rgba(34, 197, 94, 0.3)',
      borderRadius: '8px',
      color: '#22c55e',
      fontSize: '14px',
    },
    errorMessage: {
      padding: '12px',
      backgroundColor: 'rgba(239, 68, 68, 0.1)',
      border: '1px solid rgba(239, 68, 68, 0.3)',
      borderRadius: '8px',
      color: '#ef4444',
      fontSize: '14px',
    },
    subscriptionCard: {
      backgroundColor: '#1a1a1a',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '12px',
      padding: '24px',
    },
    subscriptionHeader: {
      display: 'flex',
      justifyContent: 'space-between',
      alignItems: 'center',
      marginBottom: '20px',
    },
    subscriptionTier: {
      fontSize: '20px',
      fontWeight: '600',
      color: '#ab68ff',
    },
    subscriptionDetail: {
      display: 'flex',
      justifyContent: 'space-between',
      padding: '12px 0',
      borderBottom: '1px solid rgba(255, 255, 255, 0.05)',
    },
    subscriptionLabel: {
      color: 'rgba(255, 255, 255, 0.6)',
      fontSize: '14px',
    },
    subscriptionValue: {
      color: 'rgba(255, 255, 255, 0.9)',
      fontSize: '14px',
      fontWeight: '500',
    },
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    try {
      // Update Firebase display name if changed
      if (auth.currentUser && formData.displayName !== profile?.displayName) {
        await updateProfile(auth.currentUser, {
          displayName: formData.displayName,
        });
      }

      // Update backend profile
      await updateUserProfile({
        displayName: formData.displayName,
        companyName: formData.companyName,
        companyWebsite: formData.companyWebsite,
      });

      setSuccess(true);
      setTimeout(() => setSuccess(false), 3000);
    } catch (err: any) {
      console.error('Profile update error:', err);
      setError('Failed to update profile. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (!user) {
    return null;
  }

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
          <h1 style={styles.title}>Profile Settings</h1>
        </div>
      </div>

      <div style={styles.content}>
        {/* Account Information */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Account Information</h2>
          
          {success && (
            <div style={{ ...styles.successMessage, marginBottom: '20px' }}>
              Profile updated successfully!
            </div>
          )}
          
          {error && (
            <div style={{ ...styles.errorMessage, marginBottom: '20px' }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={styles.form}>
            <div style={styles.fieldRow}>
              <div style={styles.fieldGroup}>
                <label htmlFor="displayName" style={styles.label}>
                  Display Name
                </label>
                <div style={styles.inputWrapper}>
                  <User size={16} style={styles.inputIcon} />
                  <input
                    id="displayName"
                    name="displayName"
                    type="text"
                    value={formData.displayName}
                    onChange={handleChange}
                    style={styles.input}
                    placeholder="John Doe"
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = '#ab68ff';
                      e.currentTarget.style.boxShadow = '0 0 0 2px rgba(171, 104, 255, 0.2)';
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  />
                </div>
              </div>

              <div style={styles.fieldGroup}>
                <label htmlFor="email" style={styles.label}>
                  Email Address
                </label>
                <div style={styles.inputWrapper}>
                  <Mail size={16} style={styles.inputIcon} />
                  <input
                    id="email"
                    name="email"
                    type="email"
                    value={formData.email}
                    disabled
                    style={{ ...styles.input, ...styles.inputDisabled }}
                    placeholder="you@example.com"
                  />
                </div>
              </div>
            </div>

            <div style={styles.fieldRow}>
              <div style={styles.fieldGroup}>
                <label htmlFor="companyName" style={styles.label}>
                  Company Name
                </label>
                <div style={styles.inputWrapper}>
                  <Building size={16} style={styles.inputIcon} />
                  <input
                    id="companyName"
                    name="companyName"
                    type="text"
                    value={formData.companyName}
                    onChange={handleChange}
                    style={styles.input}
                    placeholder="Acme Inc."
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = '#ab68ff';
                      e.currentTarget.style.boxShadow = '0 0 0 2px rgba(171, 104, 255, 0.2)';
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  />
                </div>
              </div>

              <div style={styles.fieldGroup}>
                <label htmlFor="companyWebsite" style={styles.label}>
                  Company Website
                </label>
                <div style={styles.inputWrapper}>
                  <Globe size={16} style={styles.inputIcon} />
                  <input
                    id="companyWebsite"
                    name="companyWebsite"
                    type="url"
                    value={formData.companyWebsite}
                    onChange={handleChange}
                    style={styles.input}
                    placeholder="https://example.com"
                    onFocus={(e) => {
                      e.currentTarget.style.borderColor = '#ab68ff';
                      e.currentTarget.style.boxShadow = '0 0 0 2px rgba(171, 104, 255, 0.2)';
                    }}
                    onBlur={(e) => {
                      e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)';
                      e.currentTarget.style.boxShadow = 'none';
                    }}
                  />
                </div>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              style={{
                ...styles.button,
                ...(loading ? styles.buttonDisabled : {})
              }}
              onMouseEnter={(e) => !loading && (e.currentTarget.style.backgroundColor = '#9050e0')}
              onMouseLeave={(e) => !loading && (e.currentTarget.style.backgroundColor = '#ab68ff')}
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  Saving...
                </>
              ) : (
                <>
                  <Save size={16} />
                  Save Changes
                </>
              )}
            </button>
          </form>
        </div>

        {/* Subscription Details */}
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Subscription Details</h2>
          
          <div style={styles.subscriptionCard}>
            <div style={styles.subscriptionHeader}>
              <div style={styles.subscriptionTier}>
                {profile?.subscriptionTier ? 
                  profile.subscriptionTier.charAt(0).toUpperCase() + profile.subscriptionTier.slice(1) 
                  : 'Free'} Plan
              </div>
              <button
                onClick={() => router.push('/billing')}
                style={{
                  ...styles.button,
                  backgroundColor: 'transparent',
                  border: '1px solid #ab68ff',
                }}
                onMouseEnter={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(171, 104, 255, 0.1)';
                }}
                onMouseLeave={(e) => {
                  e.currentTarget.style.backgroundColor = 'transparent';
                }}
              >
                Manage Billing
              </button>
            </div>

            <div>
              <div style={styles.subscriptionDetail}>
                <span style={styles.subscriptionLabel}>Monthly Analyses Used</span>
                <span style={styles.subscriptionValue}>
                  {profile?.monthlyAnalysesUsed || 0} / {profile?.monthlyAnalysesLimit || 10}
                </span>
              </div>
              <div style={styles.subscriptionDetail}>
                <span style={styles.subscriptionLabel}>Account Created</span>
                <span style={styles.subscriptionValue}>
                  {profile?.createdAt ? new Date(profile.createdAt).toLocaleDateString() : 'N/A'}
                </span>
              </div>
              <div style={{ ...styles.subscriptionDetail, borderBottom: 'none' }}>
                <span style={styles.subscriptionLabel}>User ID</span>
                <span style={{ ...styles.subscriptionValue, fontFamily: 'monospace', fontSize: '12px' }}>
                  {user.uid}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}