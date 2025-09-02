"use client";

import React, { useState } from "react";
import { Mail, Lock, Loader2 } from "lucide-react";
import { auth } from "@/lib/firebase";
import { signInWithEmailAndPassword, signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import { useAuth } from "@/hooks/useAuth";

interface LoginFormProps {
  onSuccess: () => void;
}

export default function LoginFormStyled({ onSuccess }: LoginFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
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
    inputFocus: {
      borderColor: '#ab68ff',
      boxShadow: '0 0 0 2px rgba(171, 104, 255, 0.2)',
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
    },
    buttonHover: {
      backgroundColor: '#9050e0',
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
    googleButtonHover: {
      backgroundColor: '#1a1a1a',
    },
    forgotPassword: {
      fontSize: '13px',
      color: '#ab68ff',
      textAlign: 'right' as const,
      cursor: 'pointer',
      background: 'none',
      border: 'none',
      marginTop: '-8px',
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const idToken = await userCredential.user.getIdToken();
      await login(idToken);
      onSuccess();
    } catch (err: any) {
      console.error("Login error:", err);
      if (err.code === "auth/user-not-found") {
        setError("No account found with this email");
      } else if (err.code === "auth/wrong-password") {
        setError("Incorrect password");
      } else if (err.code === "auth/invalid-email") {
        setError("Invalid email address");
      } else {
        setError("Failed to sign in. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setError("");
    setLoading(true);

    try {
      const provider = new GoogleAuthProvider();
      const userCredential = await signInWithPopup(auth, provider);
      const idToken = await userCredential.user.getIdToken();
      await login(idToken);
      onSuccess();
    } catch (err: any) {
      console.error("Google sign-in error:", err);
      setError("Failed to sign in with Google");
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
        <label htmlFor="email" style={styles.label}>
          Email
        </label>
        <div style={styles.inputWrapper}>
          <Mail size={16} style={styles.inputIcon} />
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
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

      <div style={styles.fieldGroup}>
        <label htmlFor="password" style={styles.label}>
          Password
        </label>
        <div style={styles.inputWrapper}>
          <Lock size={16} style={styles.inputIcon} />
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
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

      <button
        type="button"
        style={styles.forgotPassword}
        onMouseEnter={(e) => e.currentTarget.style.color = '#9050e0'}
        onMouseLeave={(e) => e.currentTarget.style.color = '#ab68ff'}
      >
        Forgot password?
      </button>

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
            Signing in...
          </>
        ) : (
          "Sign In"
        )}
      </button>

      <div style={styles.divider}>
        <div style={styles.dividerLine} />
        <span style={styles.dividerText}>Or continue with</span>
        <div style={styles.dividerLine} />
      </div>

      <button
        type="button"
        onClick={handleGoogleSignIn}
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
        Sign in with Google
      </button>
    </form>
  );
}