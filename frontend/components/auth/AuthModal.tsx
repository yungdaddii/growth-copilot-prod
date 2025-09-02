"use client";

import React, { useState } from "react";
import { X } from "lucide-react";
import LoginForm from "./LoginForm";
import RegisterForm from "./RegisterForm";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: "login" | "register";
}

export default function AuthModal({ isOpen, onClose, initialMode = "login" }: AuthModalProps) {
  const [mode, setMode] = useState<"login" | "register">(initialMode);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center" style={{ backgroundColor: 'rgba(0, 0, 0, 0.7)', backdropFilter: 'blur(4px)' }}>
      <div className="relative w-full max-w-md rounded-xl p-6 shadow-2xl" style={{ backgroundColor: '#1a1a1a', border: '1px solid rgba(255, 255, 255, 0.1)' }}>
        <button
          onClick={onClose}
          className="absolute right-4 top-4 transition-colors"
          style={{ color: 'rgba(255, 255, 255, 0.5)' }}
          onMouseEnter={(e) => e.currentTarget.style.color = 'rgba(255, 255, 255, 0.8)'}
          onMouseLeave={(e) => e.currentTarget.style.color = 'rgba(255, 255, 255, 0.5)'}
        >
          <X className="h-5 w-5" />
        </button>

        <div className="mb-6">
          <h2 className="text-2xl font-bold" style={{ color: 'white' }}>
            {mode === "login" ? "Welcome Back" : "Create Account"}
          </h2>
          <p className="mt-2 text-sm" style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
            {mode === "login"
              ? "Sign in to access your growth insights"
              : "Start your journey to 10x revenue growth"}
          </p>
        </div>

        {mode === "login" ? (
          <LoginForm onSuccess={onClose} />
        ) : (
          <RegisterForm onSuccess={onClose} />
        )}

        <div className="mt-6 text-center">
          <p className="text-sm" style={{ color: 'rgba(255, 255, 255, 0.6)' }}>
            {mode === "login" ? "Don't have an account?" : "Already have an account?"}
            <button
              onClick={() => setMode(mode === "login" ? "register" : "login")}
              className="ml-1 font-medium transition-colors"
              style={{ color: '#ab68ff' }}
              onMouseEnter={(e) => e.currentTarget.style.color = '#9050e0'}
              onMouseLeave={(e) => e.currentTarget.style.color = '#ab68ff'}
            >
              {mode === "login" ? "Sign up" : "Sign in"}
            </button>
          </p>
        </div>
      </div>
    </div>
  );
}