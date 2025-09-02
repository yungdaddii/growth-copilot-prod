"use client";

import React, { useState } from "react";
import { Mail, Lock, Loader2 } from "lucide-react";
import { auth } from "@/lib/firebase";
import { signInWithEmailAndPassword, signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import { useAuth } from "@/hooks/useAuth";

interface LoginFormProps {
  onSuccess: () => void;
}

export default function LoginForm({ onSuccess }: LoginFormProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    try {
      // Sign in with Firebase
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const idToken = await userCredential.user.getIdToken();
      
      // Send token to backend
      await login(idToken);
      
      // Show success message
      setSuccess("Welcome back! Redirecting...");
      
      // Wait a moment for user to see the success message
      setTimeout(() => {
        onSuccess();
      }, 1000);
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
      
      // Send token to backend
      await login(idToken);
      
      // Show success message
      setSuccess("Welcome back! Redirecting...");
      
      // Wait a moment for user to see the success message
      setTimeout(() => {
        onSuccess();
      }, 1000);
    } catch (err: any) {
      console.error("Google sign-in error:", err);
      setError("Failed to sign in with Google");
    } finally {
      setLoading(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      {error && (
        <div className="rounded-md p-3 text-sm" style={{ backgroundColor: 'rgba(220, 38, 38, 0.1)', color: '#ef4444', border: '1px solid rgba(220, 38, 38, 0.3)' }}>
          {error}
        </div>
      )}
      
      {success && (
        <div className="rounded-md p-3 text-sm" style={{ backgroundColor: 'rgba(34, 197, 94, 0.1)', color: '#22c55e', border: '1px solid rgba(34, 197, 94, 0.3)' }}>
          {success}
        </div>
      )}

      <div>
        <label htmlFor="email" className="block text-sm font-medium" style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
          Email
        </label>
        <div className="relative mt-1">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <Mail className="h-4 w-4 text-gray-400" />
          </div>
          <input
            id="email"
            type="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            className="block w-full rounded-md py-2 pl-10 pr-3 text-sm focus:outline-none focus:ring-1"
            style={{ backgroundColor: '#0a0a0a', border: '1px solid rgba(255, 255, 255, 0.1)', color: 'white' }}
            onFocus={(e) => { e.currentTarget.style.borderColor = '#ab68ff'; e.currentTarget.style.boxShadow = '0 0 0 1px #ab68ff'; }}
            onBlur={(e) => { e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)'; e.currentTarget.style.boxShadow = 'none'; }}
            placeholder="you@example.com"
          />
        </div>
      </div>

      <div>
        <label htmlFor="password" className="block text-sm font-medium" style={{ color: 'rgba(255, 255, 255, 0.8)' }}>
          Password
        </label>
        <div className="relative mt-1">
          <div className="pointer-events-none absolute inset-y-0 left-0 flex items-center pl-3">
            <Lock className="h-4 w-4 text-gray-400" />
          </div>
          <input
            id="password"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            className="block w-full rounded-md py-2 pl-10 pr-3 text-sm focus:outline-none focus:ring-1"
            style={{ backgroundColor: '#0a0a0a', border: '1px solid rgba(255, 255, 255, 0.1)', color: 'white' }}
            onFocus={(e) => { e.currentTarget.style.borderColor = '#ab68ff'; e.currentTarget.style.boxShadow = '0 0 0 1px #ab68ff'; }}
            onBlur={(e) => { e.currentTarget.style.borderColor = 'rgba(255, 255, 255, 0.1)'; e.currentTarget.style.boxShadow = 'none'; }}
            placeholder="••••••••"
          />
        </div>
      </div>

      <div className="flex items-center justify-between">
        <button
          type="button"
          className="text-sm text-blue-600 hover:text-blue-500 dark:text-blue-400"
        >
          Forgot password?
        </button>
      </div>

      <button
        type="submit"
        disabled={loading}
        className="flex w-full items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus:outline-none disabled:opacity-50"
        style={{ backgroundColor: '#ab68ff', color: 'white' }}
        onMouseEnter={(e) => !loading && (e.currentTarget.style.backgroundColor = '#9050e0')}
        onMouseLeave={(e) => !loading && (e.currentTarget.style.backgroundColor = '#ab68ff')}
      >
        {loading ? (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            Signing in...
          </>
        ) : (
          "Sign in"
        )}
      </button>

      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t" style={{ borderColor: 'rgba(255, 255, 255, 0.1)' }} />
        </div>
        <div className="relative flex justify-center text-sm">
          <span className="px-2" style={{ backgroundColor: '#1a1a1a', color: 'rgba(255, 255, 255, 0.6)' }}>
            Or continue with
          </span>
        </div>
      </div>

      <button
        type="button"
        onClick={handleGoogleSignIn}
        disabled={loading}
        className="flex w-full items-center justify-center rounded-md px-4 py-2 text-sm font-medium transition-colors focus:outline-none disabled:opacity-50"
        style={{ backgroundColor: '#0a0a0a', border: '1px solid rgba(255, 255, 255, 0.1)', color: 'rgba(255, 255, 255, 0.8)' }}
        onMouseEnter={(e) => !loading && (e.currentTarget.style.backgroundColor = '#1f1f1f')}
        onMouseLeave={(e) => !loading && (e.currentTarget.style.backgroundColor = '#0a0a0a')}
      >
        <svg className="mr-2 h-4 w-4" viewBox="0 0 24 24">
          <path
            fill="#4285F4"
            d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"
          />
          <path
            fill="#34A853"
            d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"
          />
          <path
            fill="#FBBC05"
            d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"
          />
          <path
            fill="#EA4335"
            d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"
          />
        </svg>
        Sign in with Google
      </button>
    </form>
  );
}