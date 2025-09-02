import { useState, useEffect, useContext, createContext } from 'react';
import { User as FirebaseUser } from 'firebase/auth';
import { auth } from '@/lib/firebase';
import { onAuthStateChanged, signOut } from 'firebase/auth';

interface UserProfile {
  id: string;
  email: string;
  displayName: string | null;
  photoUrl: string | null;
  companyName: string | null;
  companyWebsite: string | null;
  subscriptionTier: 'free' | 'starter' | 'pro' | 'enterprise';
  subscriptionStatus: 'active' | 'cancelled' | 'past_due' | 'trialing' | 'inactive';
  monthlyAnalysesLimit: number;
  monthlyAnalysesUsed: number;
  canUseAiChat: boolean;
  canExportData: boolean;
  canUseApi: boolean;
  createdAt?: string;
}

interface AuthContextType {
  user: FirebaseUser | null;
  profile: UserProfile | null;
  loading: boolean;
  error: string | null;
  login: (idToken: string, additionalData?: any) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
  updateUserProfile: (data: Partial<UserProfile>) => Promise<void>;
}

const AuthContext = createContext<AuthContextType>({
  user: null,
  profile: null,
  loading: true,
  error: null,
  login: async () => {},
  logout: async () => {},
  refreshProfile: async () => {},
  updateUserProfile: async () => {},
});

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<FirebaseUser | null>(null);
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Listen to Firebase auth state changes
  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      setUser(firebaseUser);
      
      if (firebaseUser) {
        // Get user profile from backend
        await fetchUserProfile(firebaseUser);
      } else {
        setProfile(null);
      }
      
      setLoading(false);
    });

    return () => unsubscribe();
  }, []);

  const fetchUserProfile = async (firebaseUser: FirebaseUser) => {
    try {
      const idToken = await firebaseUser.getIdToken();
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/me`, {
        headers: {
          Authorization: `Bearer ${idToken}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        setProfile({
          id: data.id,
          email: data.email,
          displayName: data.display_name,
          photoUrl: data.photo_url,
          companyName: data.company_name,
          companyWebsite: data.company_website,
          subscriptionTier: data.subscription_tier,
          subscriptionStatus: data.subscription_status,
          monthlyAnalysesLimit: data.monthly_analyses_limit,
          monthlyAnalysesUsed: data.monthly_analyses_used,
          canUseAiChat: data.can_use_ai_chat,
          canExportData: data.can_export_data,
          canUseApi: data.can_use_api,
          createdAt: data.created_at,
        });
      } else {
        setError('Failed to fetch user profile');
      }
    } catch (err) {
      console.error('Error fetching user profile:', err);
      setError('Failed to fetch user profile');
    }
  };

  const login = async (idToken: string, additionalData?: any) => {
    try {
      setError(null);
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          id_token: idToken,
          ...additionalData,
        }),
      });

      if (response.ok) {
        const data = await response.json();
        setProfile({
          id: data.id,
          email: data.email,
          displayName: data.display_name,
          photoUrl: data.photo_url,
          companyName: data.company_name,
          companyWebsite: data.company_website,
          subscriptionTier: data.subscription_tier,
          subscriptionStatus: data.subscription_status,
          monthlyAnalysesLimit: data.monthly_analyses_limit,
          monthlyAnalysesUsed: data.monthly_analyses_used,
          canUseAiChat: data.can_use_ai_chat,
          canExportData: data.can_export_data,
          canUseApi: data.can_use_api,
          createdAt: data.created_at,
        });
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Login failed');
      }
    } catch (err: any) {
      console.error('Login error:', err);
      setError(err.message || 'Login failed');
      throw err;
    }
  };

  const logout = async () => {
    try {
      setError(null);
      
      // Sign out from Firebase
      await signOut(auth);
      
      // Clear local state
      setUser(null);
      setProfile(null);
      
      // Optional: Call backend logout endpoint
      if (user) {
        const idToken = await user.getIdToken();
        await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/logout`, {
          method: 'POST',
          headers: {
            Authorization: `Bearer ${idToken}`,
          },
        });
      }
    } catch (err: any) {
      console.error('Logout error:', err);
      setError(err.message || 'Logout failed');
      throw err;
    }
  };

  const refreshProfile = async () => {
    if (user) {
      await fetchUserProfile(user);
    }
  };

  const updateUserProfile = async (data: Partial<UserProfile>) => {
    if (!user) {
      throw new Error('User not authenticated');
    }

    try {
      setError(null);
      const idToken = await user.getIdToken();
      
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/auth/profile`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${idToken}`,
        },
        body: JSON.stringify({
          display_name: data.displayName,
          company_name: data.companyName,
          company_website: data.companyWebsite,
        }),
      });

      if (response.ok) {
        const updatedData = await response.json();
        setProfile({
          id: updatedData.id,
          email: updatedData.email,
          displayName: updatedData.display_name,
          photoUrl: updatedData.photo_url,
          companyName: updatedData.company_name,
          companyWebsite: updatedData.company_website,
          subscriptionTier: updatedData.subscription_tier,
          subscriptionStatus: updatedData.subscription_status,
          monthlyAnalysesLimit: updatedData.monthly_analyses_limit,
          monthlyAnalysesUsed: updatedData.monthly_analyses_used,
          canUseAiChat: updatedData.can_use_ai_chat,
          canExportData: updatedData.can_export_data,
          canUseApi: updatedData.can_use_api,
          createdAt: updatedData.created_at,
        });
      } else {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update profile');
      }
    } catch (err: any) {
      console.error('Update profile error:', err);
      setError(err.message || 'Failed to update profile');
      throw err;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        profile,
        loading,
        error,
        login,
        logout,
        refreshProfile,
        updateUserProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}