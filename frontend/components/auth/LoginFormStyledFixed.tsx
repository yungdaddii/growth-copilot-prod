"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { auth } from "@/lib/firebase";
import { signInWithEmailAndPassword, signInWithPopup, GoogleAuthProvider } from "firebase/auth";
import Link from "next/link";
import Image from "next/image";

interface LoginFormStyledProps {
  onSuccess: () => void;
}

export default function LoginFormStyled({ onSuccess }: LoginFormStyledProps) {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const router = useRouter();

  const styles = {
    form: {
      display: "flex",
      flexDirection: "column" as const,
      gap: "24px",
      width: "100%",
      maxWidth: "400px",
      margin: "0 auto",
    },
    title: {
      fontSize: "32px",
      fontWeight: "bold",
      marginBottom: "8px",
      color: "#111827",
      textAlign: "center" as const,
    },
    subtitle: {
      fontSize: "16px",
      color: "#6B7280",
      marginBottom: "32px",
      textAlign: "center" as const,
    },
    inputGroup: {
      display: "flex",
      flexDirection: "column" as const,
      gap: "8px",
    },
    label: {
      fontSize: "14px",
      fontWeight: "500",
      color: "#374151",
    },
    input: {
      padding: "12px 16px",
      fontSize: "16px",
      border: "1px solid #D1D5DB",
      borderRadius: "8px",
      backgroundColor: "#FFFFFF",
      transition: "all 0.2s",
      outline: "none",
    },
    button: {
      padding: "12px 24px",
      fontSize: "16px",
      fontWeight: "600",
      color: "#FFFFFF",
      backgroundColor: "#7C3AED",
      border: "none",
      borderRadius: "8px",
      cursor: "pointer",
      transition: "all 0.2s",
      marginTop: "8px",
    },
    googleButton: {
      padding: "12px 24px",
      fontSize: "16px",
      fontWeight: "600",
      color: "#374151",
      backgroundColor: "#FFFFFF",
      border: "1px solid #D1D5DB",
      borderRadius: "8px",
      cursor: "pointer",
      transition: "all 0.2s",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
      gap: "12px",
    },
    divider: {
      display: "flex",
      alignItems: "center",
      gap: "16px",
      margin: "8px 0",
    },
    dividerLine: {
      flex: 1,
      height: "1px",
      backgroundColor: "#E5E7EB",
    },
    dividerText: {
      fontSize: "14px",
      color: "#6B7280",
      fontWeight: "500",
    },
    footer: {
      textAlign: "center" as const,
      fontSize: "14px",
      color: "#6B7280",
      marginTop: "24px",
    },
    link: {
      color: "#7C3AED",
      textDecoration: "none",
      fontWeight: "600",
      marginLeft: "4px",
    },
    errorBox: {
      padding: "12px",
      backgroundColor: "#FEE2E2",
      border: "1px solid #FECACA",
      borderRadius: "8px",
      color: "#991B1B",
      fontSize: "14px",
      marginBottom: "16px",
    },
    forgotPassword: {
      textAlign: "right" as const,
      marginTop: "-16px",
    },
    forgotLink: {
      fontSize: "14px",
      color: "#7C3AED",
      textDecoration: "none",
    },
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) {
      setError("Please fill in all fields");
      return;
    }

    setError("");
    setLoading(true);

    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      const idToken = await userCredential.user.getIdToken();
      
      console.log("Firebase sign-in successful, calling backend...");
      await login(idToken);
      console.log("Backend login successful");
      onSuccess();
    } catch (err: any) {
      console.error("Sign-in error details:", {
        code: err.code,
        message: err.message,
        fullError: err
      });
      
      if (err.code === "auth/user-not-found") {
        setError("No account found with this email");
      } else if (err.code === "auth/wrong-password") {
        setError("Incorrect password");
      } else if (err.code === "auth/invalid-email") {
        setError("Invalid email address");
      } else if (err.code === "auth/too-many-requests") {
        setError("Too many failed attempts. Please try again later");
      } else if (err.message && err.message.includes("backend")) {
        setError(`Backend error: ${err.message}`);
      } else {
        setError(err.message || "Failed to sign in. Please try again");
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGoogleSignIn = async () => {
    setError("");
    setLoading(true);

    try {
      console.log("Starting Google sign-in...");
      const provider = new GoogleAuthProvider();
      const userCredential = await signInWithPopup(auth, provider);
      console.log("Firebase Google sign-in successful");
      
      const idToken = await userCredential.user.getIdToken();
      console.log("Got Firebase ID token, calling backend...");
      
      try {
        await login(idToken);
        console.log("Backend login successful");
        onSuccess();
      } catch (backendError: any) {
        console.error("Backend login failed:", backendError);
        // More detailed error for backend issues
        if (backendError.message) {
          setError(`Backend authentication failed: ${backendError.message}`);
        } else {
          setError("Failed to authenticate with backend server. Please try again.");
        }
        // Sign out from Firebase since backend auth failed
        await auth.signOut();
      }
    } catch (err: any) {
      console.error("Google sign-in error details:", {
        code: err.code,
        message: err.message,
        fullError: err
      });
      
      if (err.code === "auth/popup-closed-by-user") {
        setError("Sign-in cancelled");
      } else if (err.code === "auth/popup-blocked") {
        setError("Popup was blocked. Please allow popups for this site");
      } else {
        setError(`Google sign-in failed: ${err.message || "Unknown error"}`);
      }
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

      <div style={styles.inputGroup}>
        <label htmlFor="email" style={styles.label}>
          Email
        </label>
        <input
          id="email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={styles.input}
          placeholder="Enter your email"
          disabled={loading}
        />
      </div>

      <div style={styles.inputGroup}>
        <label htmlFor="password" style={styles.label}>
          Password
        </label>
        <input
          id="password"
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={styles.input}
          placeholder="Enter your password"
          disabled={loading}
        />
      </div>

      <div style={styles.forgotPassword}>
        <Link href="/forgot-password" style={styles.forgotLink}>
          Forgot password?
        </Link>
      </div>

      <button
        type="submit"
        style={{
          ...styles.button,
          opacity: loading ? 0.7 : 1,
          cursor: loading ? "not-allowed" : "pointer",
        }}
        disabled={loading}
      >
        {loading ? "Signing in..." : "Sign In"}
      </button>

      <div style={styles.divider}>
        <div style={styles.dividerLine}></div>
        <span style={styles.dividerText}>Or continue with</span>
        <div style={styles.dividerLine}></div>
      </div>

      <button
        type="button"
        onClick={handleGoogleSignIn}
        style={{
          ...styles.googleButton,
          opacity: loading ? 0.7 : 1,
          cursor: loading ? "not-allowed" : "pointer",
        }}
        disabled={loading}
      >
        <Image
          src="https://www.gstatic.com/firebasejs/ui/2.0.0/images/auth/google.svg"
          alt="Google"
          width={20}
          height={20}
        />
        Sign in with Google
      </button>

      <div style={styles.footer}>
        Don't have an account?
        <Link href="/signup" style={styles.link}>
          Sign up
        </Link>
      </div>
    </form>
  );
}