import { useEffect, useState } from "react";

import { fetchCurrentUser, login, logout } from "../services/authApi";
import {
  clearAuthTokens,
  getStoredAccessToken,
  getStoredRefreshToken,
  saveAuthTokens,
} from "../services/authStorage";

export function useAuthSession() {
  const [authToken, setAuthToken] = useState(getStoredAccessToken());
  const [refreshToken, setRefreshToken] = useState(getStoredRefreshToken());
  const [currentUser, setCurrentUser] = useState(null);
  const [authLoading, setAuthLoading] = useState(Boolean(authToken));
  const [loginState, setLoginState] = useState({
    email: "admin@sistema.local",
    password: "",
    loading: false,
    error: "",
  });

  const clearSession = () => {
    clearAuthTokens();
    setAuthToken(null);
    setRefreshToken(null);
    setCurrentUser(null);
  };

  useEffect(() => {
    if (!authToken) {
      setCurrentUser(null);
      setAuthLoading(false);
      return;
    }

    let mounted = true;

    const loadProfile = async () => {
      setAuthLoading(true);
      try {
        const profile = await fetchCurrentUser(authToken);
        if (mounted) {
          setCurrentUser(profile);
        }
      } catch (_error) {
        if (mounted) {
          clearSession();
        }
      } finally {
        if (mounted) {
          setAuthLoading(false);
        }
      }
    };

    loadProfile();

    return () => {
      mounted = false;
    };
  }, [authToken]);

  const handleLogin = async (event) => {
    event.preventDefault();
    setLoginState((previous) => ({ ...previous, loading: true, error: "" }));

    try {
      const response = await login({
        email: loginState.email,
        password: loginState.password,
      });
      saveAuthTokens(response.access, response.refresh);
      setAuthToken(response.access);
      setRefreshToken(response.refresh);
      setLoginState((previous) => ({ ...previous, password: "", loading: false }));
    } catch (error) {
      setLoginState((previous) => ({
        ...previous,
        loading: false,
        error: error.message || "No se pudo iniciar sesion.",
      }));
    }
  };

  const handleLogout = async () => {
    try {
      if (authToken && refreshToken) {
        await logout({ token: authToken, refresh: refreshToken });
      }
    } catch (_error) {
      // Si falla logout remoto, se limpia sesion local de todas formas.
    } finally {
      clearSession();
    }
  };

  return {
    authToken,
    currentUser,
    authLoading,
    loginState,
    setLoginState,
    handleLogin,
    handleLogout,
  };
}
