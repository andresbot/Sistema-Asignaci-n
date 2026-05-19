export const AUTH_STORAGE_KEYS = {
  access: "sa_access_token",
  refresh: "sa_refresh_token",
};

export function getStoredAccessToken() {
  return localStorage.getItem(AUTH_STORAGE_KEYS.access);
}

export function getStoredRefreshToken() {
  return localStorage.getItem(AUTH_STORAGE_KEYS.refresh);
}

export function saveAuthTokens(accessToken, refreshToken) {
  localStorage.setItem(AUTH_STORAGE_KEYS.access, accessToken);
  localStorage.setItem(AUTH_STORAGE_KEYS.refresh, refreshToken);
}

export function clearAuthTokens() {
  localStorage.removeItem(AUTH_STORAGE_KEYS.access);
  localStorage.removeItem(AUTH_STORAGE_KEYS.refresh);
}
