import { coreApiRequest } from "../../../shared/api/coreApiClient";

export function fetchRoles(token) {
  return coreApiRequest("/roles/", { token });
}

export function fetchUsers(token) {
  return coreApiRequest("/users/", { token });
}

export function createUser(token, payload) {
  return coreApiRequest("/users/", {
    method: "POST",
    token,
    body: payload,
  });
}

export function updateUser(token, userProfileId, payload) {
  return coreApiRequest(`/users/${userProfileId}/`, {
    method: "PATCH",
    token,
    body: payload,
  });
}

export function deactivateUser(token, userProfileId) {
  return coreApiRequest(`/users/${userProfileId}/`, {
    method: "DELETE",
    token,
  });
}
