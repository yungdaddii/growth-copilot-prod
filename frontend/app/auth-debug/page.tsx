"use client";

import { useState } from "react";
import { auth } from "@/lib/firebase";
import { 
  createUserWithEmailAndPassword, 
  signInWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  updateProfile
} from "firebase/auth";

export default function AuthDebugPage() {
  const [logs, setLogs] = useState<string[]>([]);
  const [email, setEmail] = useState("test@example.com");
  const [password, setPassword] = useState("Test123!");
  const [displayName, setDisplayName] = useState("Test User");

  const addLog = (message: string, type: "info" | "success" | "error" = "info") => {
    const timestamp = new Date().toLocaleTimeString();
    const prefix = type === "error" ? "❌" : type === "success" ? "✅" : "ℹ️";
    setLogs(prev => [...prev, `[${timestamp}] ${prefix} ${message}`]);
  };

  const clearLogs = () => setLogs([]);

  const testFirebaseConfig = () => {
    addLog("Testing Firebase configuration...");
    try {
      if (auth) {
        addLog(`Firebase app initialized: ${auth.app.name}`, "success");
        addLog(`Auth domain: ${auth.app.options.authDomain || "Not set"}`, "info");
        addLog(`Project ID: ${auth.app.options.projectId || "Not set"}`, "info");
      } else {
        addLog("Firebase auth not initialized", "error");
      }
    } catch (error: any) {
      addLog(`Firebase config error: ${error.message}`, "error");
    }
  };

  const testSignUp = async () => {
    addLog("Starting sign up test...");
    try {
      // Step 1: Create user
      addLog("Creating user with email and password...");
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      addLog(`User created: ${userCredential.user.uid}`, "success");

      // Step 2: Update profile
      if (displayName) {
        addLog("Updating user profile...");
        await updateProfile(userCredential.user, { displayName });
        addLog("Profile updated", "success");
      }

      // Step 3: Get ID token
      addLog("Getting ID token...");
      const idToken = await userCredential.user.getIdToken();
      addLog(`ID token obtained (length: ${idToken.length})`, "success");

      // Step 4: Call backend
      addLog("Calling backend /api/auth/login...");
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id_token: idToken,
          display_name: displayName,
          company_name: "Test Company",
          company_website: "https://test.com"
        }),
      });

      if (response.ok) {
        const data = await response.json();
        addLog(`Backend login successful: ${data.email}`, "success");
        addLog(`User ID: ${data.id}`, "info");
        addLog(`Subscription: ${data.subscription_tier}`, "info");
      } else {
        const errorData = await response.json();
        addLog(`Backend error: ${errorData.detail}`, "error");
      }
    } catch (error: any) {
      addLog(`Sign up failed: ${error.message}`, "error");
      if (error.code) {
        addLog(`Error code: ${error.code}`, "error");
      }
    }
  };

  const testSignIn = async () => {
    addLog("Starting sign in test...");
    try {
      // Step 1: Sign in
      addLog("Signing in with email and password...");
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      addLog(`User signed in: ${userCredential.user.uid}`, "success");

      // Step 2: Get ID token
      addLog("Getting ID token...");
      const idToken = await userCredential.user.getIdToken();
      addLog(`ID token obtained (length: ${idToken.length})`, "success");

      // Step 3: Call backend
      addLog("Calling backend /api/auth/login...");
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id_token: idToken
        }),
      });

      if (response.ok) {
        const data = await response.json();
        addLog(`Backend login successful: ${data.email}`, "success");
      } else {
        const errorData = await response.json();
        addLog(`Backend error: ${errorData.detail}`, "error");
      }
    } catch (error: any) {
      addLog(`Sign in failed: ${error.message}`, "error");
      if (error.code) {
        addLog(`Error code: ${error.code}`, "error");
      }
    }
  };

  const testGoogleSignIn = async () => {
    addLog("Starting Google sign in test...");
    try {
      const provider = new GoogleAuthProvider();
      addLog("Opening Google sign in popup...");
      const userCredential = await signInWithPopup(auth, provider);
      addLog(`Google sign in successful: ${userCredential.user.email}`, "success");

      // Get ID token
      const idToken = await userCredential.user.getIdToken();
      addLog(`ID token obtained (length: ${idToken.length})`, "success");

      // Call backend
      addLog("Calling backend /api/auth/login...");
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          id_token: idToken
        }),
      });

      if (response.ok) {
        const data = await response.json();
        addLog(`Backend login successful: ${data.email}`, "success");
      } else {
        const errorData = await response.json();
        addLog(`Backend error: ${errorData.detail}`, "error");
      }
    } catch (error: any) {
      addLog(`Google sign in failed: ${error.message}`, "error");
      if (error.code) {
        addLog(`Error code: ${error.code}`, "error");
      }
    }
  };

  const testBackendHealth = async () => {
    addLog("Testing backend health endpoints...");
    
    // Test Firebase health
    try {
      addLog("Checking /health/firebase...");
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health/firebase`);
      const data = await response.json();
      
      if (data.status === "operational") {
        addLog("Firebase is operational", "success");
      } else if (data.status === "degraded") {
        addLog("Firebase is degraded - credentials may be missing", "error");
        addLog(`Recommendation: ${data.recommendation}`, "info");
      } else {
        addLog(`Firebase status: ${data.status}`, "error");
        addLog(`Error: ${data.error || "Unknown"}`, "error");
      }
    } catch (error: any) {
      addLog(`Failed to check Firebase health: ${error.message}`, "error");
    }

    // Test config health
    try {
      addLog("Checking /health/config...");
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/health/config`);
      const data = await response.json();
      
      if (data.status === "healthy") {
        addLog("All configurations are healthy", "success");
      } else {
        addLog(`Configuration status: ${data.status}`, "error");
        if (data.missing_critical && data.missing_critical.length > 0) {
          addLog(`Missing: ${data.missing_critical.filter(Boolean).join(", ")}`, "error");
        }
      }
    } catch (error: any) {
      addLog(`Failed to check config health: ${error.message}`, "error");
    }
  };

  return (
    <div className="min-h-screen bg-black text-white p-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Auth Debug Tool</h1>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {/* Test Credentials */}
          <div className="bg-gray-900 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Test Credentials</h2>
            <div className="space-y-4">
              <div>
                <label className="block text-sm text-gray-400 mb-1">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 bg-black border border-gray-700 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Password</label>
                <input
                  type="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="w-full px-3 py-2 bg-black border border-gray-700 rounded"
                />
              </div>
              <div>
                <label className="block text-sm text-gray-400 mb-1">Display Name</label>
                <input
                  type="text"
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  className="w-full px-3 py-2 bg-black border border-gray-700 rounded"
                />
              </div>
            </div>
          </div>

          {/* Test Actions */}
          <div className="bg-gray-900 rounded-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Test Actions</h2>
            <div className="space-y-2">
              <button
                onClick={testFirebaseConfig}
                className="w-full px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded text-sm font-medium"
              >
                Test Firebase Config
              </button>
              <button
                onClick={testBackendHealth}
                className="w-full px-4 py-2 bg-green-600 hover:bg-green-700 rounded text-sm font-medium"
              >
                Test Backend Health
              </button>
              <button
                onClick={testSignUp}
                className="w-full px-4 py-2 bg-purple-600 hover:bg-purple-700 rounded text-sm font-medium"
              >
                Test Sign Up
              </button>
              <button
                onClick={testSignIn}
                className="w-full px-4 py-2 bg-indigo-600 hover:bg-indigo-700 rounded text-sm font-medium"
              >
                Test Sign In
              </button>
              <button
                onClick={testGoogleSignIn}
                className="w-full px-4 py-2 bg-red-600 hover:bg-red-700 rounded text-sm font-medium"
              >
                Test Google Sign In
              </button>
              <button
                onClick={clearLogs}
                className="w-full px-4 py-2 bg-gray-600 hover:bg-gray-700 rounded text-sm font-medium"
              >
                Clear Logs
              </button>
            </div>
          </div>
        </div>

        {/* Logs */}
        <div className="bg-gray-900 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Debug Logs</h2>
          <div className="bg-black rounded p-4 h-96 overflow-y-auto font-mono text-sm">
            {logs.length === 0 ? (
              <p className="text-gray-500">No logs yet. Click a test button to start.</p>
            ) : (
              logs.map((log, index) => (
                <div key={index} className="mb-1">
                  {log}
                </div>
              ))
            )}
          </div>
        </div>

        {/* Environment Info */}
        <div className="mt-6 bg-gray-900 rounded-lg p-6">
          <h2 className="text-xl font-semibold mb-4">Environment</h2>
          <div className="space-y-2 text-sm">
            <div>
              <span className="text-gray-400">API URL:</span>{" "}
              <span className="font-mono">{process.env.NEXT_PUBLIC_API_URL || "Not set"}</span>
            </div>
            <div>
              <span className="text-gray-400">Firebase Project:</span>{" "}
              <span className="font-mono">{process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || "Not set"}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}