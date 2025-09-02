"use client";

import React, { useState } from "react";
import { X } from "lucide-react";
import LoginFormStyled from "./LoginFormStyled";
import RegisterFormStyled from "./RegisterFormStyled";

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  initialMode?: "login" | "register";
}

export default function AuthModalStyled({ isOpen, onClose, initialMode = "login" }: AuthModalProps) {
  const [mode, setMode] = useState<"login" | "register">(initialMode);

  if (!isOpen) return null;

  const modalStyles = {
    backdrop: {
      position: 'fixed' as const,
      inset: 0,
      zIndex: 50,
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'center',
      backgroundColor: 'rgba(0, 0, 0, 0.8)',
      backdropFilter: 'blur(8px)',
    },
    modal: {
      position: 'relative' as const,
      width: '100%',
      maxWidth: '28rem',
      backgroundColor: '#1a1a1a',
      borderRadius: '12px',
      padding: '32px',
      boxShadow: '0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 10px 10px -5px rgba(0, 0, 0, 0.5)',
      border: '1px solid rgba(255, 255, 255, 0.1)',
    },
    closeButton: {
      position: 'absolute' as const,
      right: '16px',
      top: '16px',
      color: 'rgba(255, 255, 255, 0.5)',
      cursor: 'pointer',
      background: 'none',
      border: 'none',
      padding: '4px',
    },
    title: {
      fontSize: '24px',
      fontWeight: 'bold',
      color: 'white',
      marginBottom: '8px',
    },
    subtitle: {
      fontSize: '14px',
      color: 'rgba(255, 255, 255, 0.6)',
      marginBottom: '24px',
    },
    toggleText: {
      fontSize: '14px',
      color: 'rgba(255, 255, 255, 0.6)',
      textAlign: 'center' as const,
      marginTop: '24px',
    },
    toggleButton: {
      color: '#ab68ff',
      fontWeight: '500',
      marginLeft: '4px',
      cursor: 'pointer',
      background: 'none',
      border: 'none',
    }
  };

  return (
    <div style={modalStyles.backdrop}>
      <div style={modalStyles.modal}>
        <button
          onClick={onClose}
          style={modalStyles.closeButton}
          onMouseEnter={(e) => e.currentTarget.style.color = 'white'}
          onMouseLeave={(e) => e.currentTarget.style.color = 'rgba(255, 255, 255, 0.5)'}
        >
          <X size={20} />
        </button>

        <div>
          <h2 style={modalStyles.title}>
            {mode === "login" ? "Welcome Back" : "Create Account"}
          </h2>
          <p style={modalStyles.subtitle}>
            {mode === "login"
              ? "Sign in to access your growth insights"
              : "Start your journey to 10x revenue growth"}
          </p>
        </div>

        {mode === "login" ? (
          <LoginFormStyled onSuccess={onClose} />
        ) : (
          <RegisterFormStyled onSuccess={onClose} />
        )}

        <div style={modalStyles.toggleText}>
          {mode === "login" ? "Don't have an account?" : "Already have an account?"}
          <button
            onClick={() => setMode(mode === "login" ? "register" : "login")}
            style={modalStyles.toggleButton}
            onMouseEnter={(e) => e.currentTarget.style.color = '#9050e0'}
            onMouseLeave={(e) => e.currentTarget.style.color = '#ab68ff'}
          >
            {mode === "login" ? "Sign up" : "Sign in"}
          </button>
        </div>
      </div>
    </div>
  );
}