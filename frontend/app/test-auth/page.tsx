"use client";

import { useState, useEffect } from 'react';
import { auth } from '@/lib/firebase';
import { 
  signInWithEmailAndPassword, 
  createUserWithEmailAndPassword,
  signInWithPopup,
  GoogleAuthProvider,
  onAuthStateChanged,
  signOut
} from 'firebase/auth';
import { useAuth } from '@/hooks/useAuth';

export default function TestAuthPage() {
  const [email, setEmail] = useState('test@example.com');
  const [password, setPassword] = useState('test123456');
  const [firebaseUser, setFirebaseUser] = useState<any>(null);
  const [idToken, setIdToken] = useState<string>('');
  const [testResults, setTestResults] = useState<any[]>([]);
  const [backendUrl, setBackendUrl] = useState('');
  const { user, profile, error: authError } = useAuth();

  useEffect(() => {
    // Get backend URL from environment
    setBackendUrl(process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000');

    // Listen to Firebase auth state
    const unsubscribe = onAuthStateChanged(auth, async (user) => {
      setFirebaseUser(user);
      if (user) {
        try {
          const token = await user.getIdToken();
          setIdToken(token);
          addTestResult('Firebase Auth State', 'success', { uid: user.uid, email: user.email });
        } catch (error) {
          addTestResult('Get ID Token', 'error', error);
        }
      } else {
        setIdToken('');
        addTestResult('Firebase Auth State', 'info', 'User signed out');
      }
    });

    return () => unsubscribe();
  }, []);

  const addTestResult = (test: string, status: 'success' | 'error' | 'info', data: any) => {
    setTestResults(prev => [...prev, { 
      test, 
      status, 
      data, 
      timestamp: new Date().toISOString() 
    }]);
  };

  const testFirebaseConfig = async () => {
    try {
      addTestResult('Firebase Config', 'success', {
        apiKey: process.env.NEXT_PUBLIC_FIREBASE_API_KEY ? '✓ Set' : '✗ Missing',
        authDomain: process.env.NEXT_PUBLIC_FIREBASE_AUTH_DOMAIN || 'Missing',
        projectId: process.env.NEXT_PUBLIC_FIREBASE_PROJECT_ID || 'Missing',
      });
    } catch (error) {
      addTestResult('Firebase Config', 'error', error);
    }
  };

  const testEmailSignUp = async () => {
    try {
      const userCredential = await createUserWithEmailAndPassword(auth, email, password);
      addTestResult('Email Sign Up', 'success', {
        uid: userCredential.user.uid,
        email: userCredential.user.email
      });
    } catch (error: any) {
      addTestResult('Email Sign Up', 'error', {
        code: error.code,
        message: error.message
      });
    }
  };

  const testEmailSignIn = async () => {
    try {
      const userCredential = await signInWithEmailAndPassword(auth, email, password);
      addTestResult('Email Sign In', 'success', {
        uid: userCredential.user.uid,
        email: userCredential.user.email
      });
    } catch (error: any) {
      addTestResult('Email Sign In', 'error', {
        code: error.code,
        message: error.message
      });
    }
  };

  const testGoogleSignIn = async () => {
    try {
      const provider = new GoogleAuthProvider();
      const userCredential = await signInWithPopup(auth, provider);
      addTestResult('Google Sign In', 'success', {
        uid: userCredential.user.uid,
        email: userCredential.user.email,
        displayName: userCredential.user.displayName
      });
    } catch (error: any) {
      addTestResult('Google Sign In', 'error', {
        code: error.code,
        message: error.message,
        customData: error.customData
      });
    }
  };

  const testSignOut = async () => {
    try {
      await signOut(auth);
      addTestResult('Sign Out', 'success', 'User signed out');
    } catch (error: any) {
      addTestResult('Sign Out', 'error', error);
    }
  };

  const testBackendAuth = async () => {
    if (!idToken) {
      addTestResult('Backend Auth', 'error', 'No ID token available. Sign in first.');
      return;
    }

    try {
      const response = await fetch(`${backendUrl}/api/auth/me`, {
        headers: {
          'Authorization': `Bearer ${idToken}`,
        },
      });

      const data = await response.json();
      
      if (response.ok) {
        addTestResult('Backend Auth', 'success', data);
      } else {
        addTestResult('Backend Auth', 'error', {
          status: response.status,
          data
        });
      }
    } catch (error) {
      addTestResult('Backend Auth', 'error', error);
    }
  };

  const testBackendLogin = async () => {
    if (!idToken) {
      addTestResult('Backend Login', 'error', 'No ID token available. Sign in first.');
      return;
    }

    try {
      const response = await fetch(`${backendUrl}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id_token: idToken,
          display_name: firebaseUser?.displayName || 'Test User',
          company_name: 'Test Company',
        }),
      });

      const data = await response.json();
      
      if (response.ok) {
        addTestResult('Backend Login', 'success', data);
      } else {
        addTestResult('Backend Login', 'error', {
          status: response.status,
          data
        });
      }
    } catch (error) {
      addTestResult('Backend Login', 'error', error);
    }
  };

  const testWebSocket = async () => {
    try {
      const wsUrl = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws/chat';
      const sessionId = localStorage.getItem('session_id') || crypto.randomUUID();
      
      let finalUrl = `${wsUrl}?session_id=${sessionId}`;
      if (idToken) {
        finalUrl += `&token=${idToken}`;
      }

      addTestResult('WebSocket URL', 'info', finalUrl.replace(/token=.*/, 'token=***'));

      const ws = new WebSocket(finalUrl);
      
      ws.onopen = () => {
        addTestResult('WebSocket', 'success', 'Connected');
        ws.send(JSON.stringify({
          type: 'chat',
          payload: { content: 'test message' }
        }));
      };

      ws.onmessage = (event) => {
        addTestResult('WebSocket Message', 'success', JSON.parse(event.data));
      };

      ws.onerror = (error) => {
        addTestResult('WebSocket', 'error', error);
      };

      ws.onclose = () => {
        addTestResult('WebSocket', 'info', 'Closed');
      };

      // Close after 5 seconds
      setTimeout(() => ws.close(), 5000);
    } catch (error) {
      addTestResult('WebSocket', 'error', error);
    }
  };

  const clearResults = () => {
    setTestResults([]);
  };

  const styles = {
    container: {
      maxWidth: '1200px',
      margin: '0 auto',
      padding: '20px',
      backgroundColor: '#0a0a0a',
      minHeight: '100vh',
      color: 'white',
    },
    header: {
      marginBottom: '30px',
      borderBottom: '1px solid rgba(255,255,255,0.1)',
      paddingBottom: '20px',
    },
    title: {
      fontSize: '24px',
      fontWeight: 'bold',
      marginBottom: '10px',
    },
    section: {
      backgroundColor: '#1a1a1a',
      borderRadius: '8px',
      padding: '20px',
      marginBottom: '20px',
      border: '1px solid rgba(255,255,255,0.1)',
    },
    sectionTitle: {
      fontSize: '18px',
      fontWeight: '600',
      marginBottom: '15px',
      color: '#ab68ff',
    },
    grid: {
      display: 'grid',
      gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
      gap: '10px',
      marginBottom: '20px',
    },
    button: {
      padding: '10px 20px',
      backgroundColor: '#ab68ff',
      color: 'white',
      border: 'none',
      borderRadius: '6px',
      cursor: 'pointer',
      fontSize: '14px',
      fontWeight: '500',
      transition: 'background-color 0.2s',
    },
    input: {
      width: '100%',
      padding: '8px 12px',
      backgroundColor: '#2a2a2a',
      border: '1px solid rgba(255,255,255,0.1)',
      borderRadius: '4px',
      color: 'white',
      marginBottom: '10px',
    },
    statusBadge: {
      display: 'inline-block',
      padding: '4px 8px',
      borderRadius: '4px',
      fontSize: '12px',
      fontWeight: '600',
      marginLeft: '10px',
    },
    success: {
      backgroundColor: 'rgba(34, 197, 94, 0.2)',
      color: '#22c55e',
    },
    error: {
      backgroundColor: 'rgba(239, 68, 68, 0.2)',
      color: '#ef4444',
    },
    info: {
      backgroundColor: 'rgba(59, 130, 246, 0.2)',
      color: '#3b82f6',
    },
    resultItem: {
      backgroundColor: '#2a2a2a',
      padding: '10px',
      borderRadius: '6px',
      marginBottom: '10px',
      fontSize: '12px',
      fontFamily: 'monospace',
    },
    pre: {
      backgroundColor: '#0a0a0a',
      padding: '8px',
      borderRadius: '4px',
      marginTop: '5px',
      overflow: 'auto',
      fontSize: '11px',
    },
  };

  return (
    <div style={styles.container}>
      <div style={styles.header}>
        <h1 style={styles.title}>Authentication Test Suite</h1>
        <p>Backend URL: {backendUrl}</p>
        <p>Current User: {firebaseUser?.email || 'Not signed in'}</p>
        {profile && <p>Profile: {profile.email} (Tier: {profile.subscriptionTier})</p>}
      </div>

      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>Test Credentials</h2>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          style={styles.input}
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          style={styles.input}
        />
      </div>

      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>Firebase Tests</h2>
        <div style={styles.grid}>
          <button style={styles.button} onClick={testFirebaseConfig}>
            Test Config
          </button>
          <button style={styles.button} onClick={testEmailSignUp}>
            Email Sign Up
          </button>
          <button style={styles.button} onClick={testEmailSignIn}>
            Email Sign In
          </button>
          <button style={styles.button} onClick={testGoogleSignIn}>
            Google Sign In
          </button>
          <button style={styles.button} onClick={testSignOut}>
            Sign Out
          </button>
        </div>
      </div>

      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>Backend Tests</h2>
        <div style={styles.grid}>
          <button style={styles.button} onClick={testBackendAuth}>
            Test /api/auth/me
          </button>
          <button style={styles.button} onClick={testBackendLogin}>
            Test /api/auth/login
          </button>
          <button style={styles.button} onClick={testWebSocket}>
            Test WebSocket
          </button>
        </div>
      </div>

      <div style={styles.section}>
        <h2 style={styles.sectionTitle}>
          Test Results
          <button 
            style={{...styles.button, marginLeft: '20px', backgroundColor: '#666'}} 
            onClick={clearResults}
          >
            Clear
          </button>
        </h2>
        {testResults.map((result, index) => (
          <div key={index} style={styles.resultItem}>
            <div>
              <strong>{result.test}</strong>
              <span style={{
                ...styles.statusBadge,
                ...(result.status === 'success' ? styles.success : 
                    result.status === 'error' ? styles.error : styles.info)
              }}>
                {result.status.toUpperCase()}
              </span>
              <span style={{ marginLeft: '10px', color: '#666' }}>
                {result.timestamp}
              </span>
            </div>
            <pre style={styles.pre}>
              {JSON.stringify(result.data, null, 2)}
            </pre>
          </div>
        ))}
      </div>

      {idToken && (
        <div style={styles.section}>
          <h2 style={styles.sectionTitle}>Current ID Token (for debugging)</h2>
          <pre style={styles.pre}>
            {idToken.substring(0, 50)}...
          </pre>
        </div>
      )}
    </div>
  );
}