"use client";

import { useState } from 'react';
import { User, Settings, LogOut, CreditCard, ChevronDown } from 'lucide-react';
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/navigation';

export function UserProfileMenu() {
  const [isOpen, setIsOpen] = useState(false);
  const { user, profile, logout } = useAuth();
  const router = useRouter();

  const styles = {
    container: {
      position: 'relative' as const,
      borderTop: '1px solid rgba(255, 255, 255, 0.1)',
      padding: '12px',
    },
    button: {
      width: '100%',
      padding: '8px 12px',
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      backgroundColor: 'transparent',
      border: 'none',
      cursor: 'pointer',
      borderRadius: '8px',
      transition: 'background-color 0.2s',
    },
    buttonHover: {
      backgroundColor: 'rgba(255, 255, 255, 0.05)',
    },
    avatar: {
      width: '32px',
      height: '32px',
      borderRadius: '50%',
      backgroundColor: '#ab68ff',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      fontSize: '14px',
      color: 'white',
      fontWeight: '600',
      flexShrink: 0,
    },
    userInfo: {
      flex: 1,
      textAlign: 'left' as const,
      minWidth: 0,
    },
    userName: {
      color: 'white',
      fontSize: '14px',
      fontWeight: '500',
      overflow: 'hidden',
      textOverflow: 'ellipsis',
      whiteSpace: 'nowrap' as const,
    },
    userTier: {
      color: 'rgba(255, 255, 255, 0.5)',
      fontSize: '12px',
    },
    chevron: {
      color: 'rgba(255, 255, 255, 0.5)',
      transition: 'transform 0.2s',
      transform: isOpen ? 'rotate(180deg)' : 'rotate(0deg)',
    },
    dropdown: {
      position: 'absolute' as const,
      bottom: '100%',
      left: '12px',
      right: '12px',
      marginBottom: '8px',
      backgroundColor: '#1a1a1a',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '8px',
      padding: '8px',
      boxShadow: '0 -4px 12px rgba(0, 0, 0, 0.3)',
      display: isOpen ? 'block' : 'none',
    },
    menuItem: {
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      padding: '10px 12px',
      color: 'rgba(255, 255, 255, 0.8)',
      fontSize: '14px',
      borderRadius: '6px',
      cursor: 'pointer',
      transition: 'all 0.2s',
      backgroundColor: 'transparent',
      border: 'none',
      width: '100%',
      textAlign: 'left' as const,
    },
    menuItemHover: {
      backgroundColor: 'rgba(255, 255, 255, 0.05)',
      color: 'white',
    },
    menuItemIcon: {
      width: '16px',
      height: '16px',
      color: 'rgba(255, 255, 255, 0.5)',
    },
    divider: {
      height: '1px',
      backgroundColor: 'rgba(255, 255, 255, 0.1)',
      margin: '8px 0',
    },
    signInButton: {
      width: '100%',
      padding: '10px 12px',
      backgroundColor: '#ab68ff',
      color: 'white',
      border: 'none',
      borderRadius: '8px',
      cursor: 'pointer',
      fontSize: '14px',
      fontWeight: '500',
      transition: 'background-color 0.2s',
    },
    signInButtonHover: {
      backgroundColor: '#9050e0',
    }
  };

  const handleLogout = async () => {
    await logout();
    setIsOpen(false);
    window.location.reload();
  };

  const handleProfileClick = () => {
    router.push('/profile');
    setIsOpen(false);
  };

  const handleBillingClick = () => {
    router.push('/billing');
    setIsOpen(false);
  };

  const getInitial = () => {
    if (profile?.displayName) {
      return profile.displayName[0].toUpperCase();
    }
    if (profile?.email) {
      return profile.email[0].toUpperCase();
    }
    return 'U';
  };

  const getTierDisplay = () => {
    if (!profile?.subscriptionTier) return 'Free';
    return profile.subscriptionTier.charAt(0).toUpperCase() + profile.subscriptionTier.slice(1);
  };

  if (!user) {
    return (
      <div style={styles.container}>
        <button
          style={styles.signInButton}
          onMouseEnter={(e) => {
            e.currentTarget.style.backgroundColor = '#9050e0';
          }}
          onMouseLeave={(e) => {
            e.currentTarget.style.backgroundColor = '#ab68ff';
          }}
          onClick={() => {
            // Trigger auth modal from parent
            const event = new CustomEvent('openAuthModal');
            window.dispatchEvent(event);
          }}
        >
          Sign In / Sign Up
        </button>
      </div>
    );
  }

  return (
    <div style={styles.container}>
      {isOpen && (
        <div style={styles.dropdown}>
          <button
            style={styles.menuItem}
            onMouseEnter={(e) => {
              Object.assign(e.currentTarget.style, styles.menuItemHover);
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.color = 'rgba(255, 255, 255, 0.8)';
            }}
            onClick={handleProfileClick}
          >
            <Settings style={styles.menuItemIcon} />
            <span>Profile Settings</span>
          </button>

          <button
            style={styles.menuItem}
            onMouseEnter={(e) => {
              Object.assign(e.currentTarget.style, styles.menuItemHover);
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.color = 'rgba(255, 255, 255, 0.8)';
            }}
            onClick={handleBillingClick}
          >
            <CreditCard style={styles.menuItemIcon} />
            <span>Billing & Plan</span>
          </button>

          <div style={styles.divider} />

          <button
            style={styles.menuItem}
            onMouseEnter={(e) => {
              Object.assign(e.currentTarget.style, styles.menuItemHover);
            }}
            onMouseLeave={(e) => {
              e.currentTarget.style.backgroundColor = 'transparent';
              e.currentTarget.style.color = 'rgba(255, 255, 255, 0.8)';
            }}
            onClick={handleLogout}
          >
            <LogOut style={styles.menuItemIcon} />
            <span>Sign Out</span>
          </button>
        </div>
      )}

      <button
        style={styles.button}
        onMouseEnter={(e) => {
          Object.assign(e.currentTarget.style, styles.buttonHover);
        }}
        onMouseLeave={(e) => {
          e.currentTarget.style.backgroundColor = 'transparent';
        }}
        onClick={() => setIsOpen(!isOpen)}
      >
        <div style={styles.avatar}>
          {getInitial()}
        </div>
        <div style={styles.userInfo}>
          <div style={styles.userName}>
            {profile?.displayName || profile?.email || 'User'}
          </div>
          <div style={styles.userTier}>
            {getTierDisplay()} • {profile?.monthlyAnalysesUsed || 0}/{profile?.monthlyAnalysesLimit || 10}
          </div>
        </div>
        <ChevronDown size={16} style={styles.chevron} />
      </button>
    </div>
  );
}