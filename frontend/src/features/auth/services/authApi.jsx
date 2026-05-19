import { coreApiRequest } from "../../../shared/api/coreApiClient";

export function login({ email, password }) {
  return coreApiRequest("/auth/login/", {
    method: "POST",
    body: { email, password },
  });
}

export function logout({ token, refresh }) {
  return coreApiRequest("/auth/logout/", {
    method: "POST",
    token,
    body: { refresh },
  });
}

export function fetchCurrentUser(token) {
  return coreApiRequest("/auth/me/", { token });
}
