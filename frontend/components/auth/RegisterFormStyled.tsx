"use client";

import React, { useState } from "react";
import { Mail, Lock, User, Building, Globe, Loader2 } from "lucide-react";
import { auth } from "@/lib/firebase";
import { createUserWithEmailAndPassword, updateProfile, signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import { useAuth } from "@/hooks/useAuth";

interface RegisterFormProps {
  onSuccess: () => void;
}

export default function RegisterFormStyled({ onSuccess }: RegisterFormProps) {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    password: "",
    confirmPassword: "",
    companyName: "",
    companyWebsite: "",
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const styles = {
    form: {
      display: 'flex',
      flexDirection: 'column' as const,
      gap: '16px',
    },
    errorBox: {
      backgroundColor: 'rgba(220, 38, 38, 0.1)',
      color: '#ef4444',
      border: '1px solid rgba(220, 38, 38, 0.3)',
      borderRadius: '6px',
      padding: '12px',
      fontSize: '14px',
    },
    fieldGroup: {
      marginBottom: '4px',
    },
    label: {
      display: 'block',
      fontSize: '14px',
      fontWeight: '500',
      color: 'rgba(255, 255, 255, 0.8)',
      marginBottom: '6px',
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
      pointerEvents: 'none' as const,
    },
    input: {
      width: '100%',
      padding: '10px 12px 10px 40px',
      backgroundColor: '#0a0a0a !important',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '6px',
      color: 'white',
      fontSize: '14px',
      outline: 'none',
      transition: 'all 0.2s',
    },
    button: {
      width: '100%',
      padding: '10px',
      backgroundColor: '#ab68ff',
      color: 'white',
      border: 'none',
      borderRadius: '6px',
      fontSize: '14px',
      fontWeight: '500',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '8px',
      transition: 'background-color 0.2s',
      marginTop: '8px',
    },
    buttonDisabled: {
      opacity: 0.5,
      cursor: 'not-allowed',
    },
    divider: {
      display: 'flex',
      alignItems: 'center',
      gap: '12px',
      margin: '8px 0',
    },
    dividerLine: {
      flex: 1,
      height: '1px',
      backgroundColor: 'rgba(255, 255, 255, 0.1)',
    },
    dividerText: {
      fontSize: '12px',
      color: 'rgba(255, 255, 255, 0.5)',
    },
    googleButton: {
      width: '100%',
      padding: '10px',
      backgroundColor: '#0a0a0a',
      color: 'rgba(255, 255, 255, 0.9)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
      borderRadius: '6px',
      fontSize: '14px',
      fontWeight: '500',
      cursor: 'pointer',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      gap: '8px',
      transition: 'background-color 0.2s',
    },
    disclaimer: {
      fontSize: '11px',
      color: 'rgba(255, 255, 255, 0.4)',
      textAlign: 'center' as const,
      marginTop: '8px',
    },
    fieldRow: {
      display: 'grid',
      gridTemplateColumns: '1fr 1fr',
      gap: '12px',
    }
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    if (formData.password !== formData.confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    if (formData.password.length < 6) {
      setError("Password must be at least 6 characters");
      return;
    }

    setLoading(true);

    try {
      const userCredential = await createUserWithEmailAndPassword(
        auth,
        formData.email,
        formData.password
      );

      if (formData.name) {
        await updateProfile(userCredential.user, {
          displayName: formData.name,
        });
      }

      const idToken = await userCredential.user.getIdToken();

      await login(idToken, {
        displayName: formData.name,
        companyName: formData.companyName,
        companyWebsite: formData.companyWebsite,
      });

      onSuccess();
    } catch (err: any) {
      console.error("Registration error:", err);
      if (err.code === "auth/email-already-in-use") {
        setError("An account with this email already exists");
      } else if (err.code === "auth/invalid-email") {
        setError("Invalid email address");
      } else if (err.code === "auth/weak-password") {
        setError("Password is too weak");
      } else {
        setError("Failed to create account. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignUp = async () => {
    setError("");
    setLoading(true);

    try {
      const provider = new GoogleAuthProvider();
      const userCredential = await signInWithPopup(auth, provider);
      const idToken = await userCredential.user.getIdToken();
      await login(idToken);
      onSuccess();
    } catch (err: any) {
      console.error("Google sign-up error:", err);
      setError("Failed to sign up with Google");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} style={styles.form}>
      {error && (
        <div style={styles.errorBox}>
          {error}
        </div>
      )}

      <div style={styles.fieldGroup}>
        <label htmlFor="name" style={styles.label}>
          Full Name *
        </label>
        <div style={styles.inputWrapper}>
          <User size={16} style={styles.inputIcon} />
          <input
            id="name"
            name="name"
            type="text"
            value={formData.name}
            onChange={handleChange}
            required
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
          Email *
        </label>
        <div style={styles.inputWrapper}>
          <Mail size={16} style={styles.inputIcon} />
          <input
            id="email"
            name="email"
            type="email"
            value={formData.email}
            onChange={handleChange}
            required
            style={styles.input}
            placeholder="you@example.com"
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

      <div style={styles.fieldRow}>
        <div style={styles.fieldGroup}>
          <label htmlFor="companyName" style={styles.label}>
            Company
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
            Website
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
              placeholder="example.com"
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

      <div style={styles.fieldRow}>
        <div style={styles.fieldGroup}>
          <label htmlFor="password" style={styles.label}>
            Password *
          </label>
          <div style={styles.inputWrapper}>
            <Lock size={16} style={styles.inputIcon} />
            <input
              id="password"
              name="password"
              type="password"
              value={formData.password}
              onChange={handleChange}
              required
              style={styles.input}
              placeholder="••••••••"
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
          <label htmlFor="confirmPassword" style={styles.label}>
            Confirm Password *
          </label>
          <div style={styles.inputWrapper}>
            <Lock size={16} style={styles.inputIcon} />
            <input
              id="confirmPassword"
              name="confirmPassword"
              type="password"
              value={formData.confirmPassword}
              onChange={handleChange}
              required
              style={styles.input}
              placeholder="••••••••"
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
            Creating account...
          </>
        ) : (
          "Create Account"
        )}
      </button>

      <div style={styles.divider}>
        <div style={styles.dividerLine} />
        <span style={styles.dividerText}>Or continue with</span>
        <div style={styles.dividerLine} />
      </div>

      <button
        type="button"
        onClick={handleGoogleSignUp}
        disabled={loading}
        style={{
          ...styles.googleButton,
          ...(loading ? styles.buttonDisabled : {})
        }}
        onMouseEnter={(e) => !loading && (e.currentTarget.style.backgroundColor = '#1a1a1a')}
        onMouseLeave={(e) => !loading && (e.currentTarget.style.backgroundColor = '#0a0a0a')}
      >
        <svg width="16" height="16" viewBox="0 0 24 24">
          <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
          <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
          <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
          <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
        </svg>
        Sign up with Google
      </button>

      <p style={styles.disclaimer}>
        By creating an account, you agree to our Terms of Service and Privacy Policy
      </p>
    </form>
  );
}