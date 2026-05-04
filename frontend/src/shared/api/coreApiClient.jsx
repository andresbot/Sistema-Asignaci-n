import { extractApiError } from "../utils/extractApiError";

const apiBase = import.meta.env.VITE_API_URL ?? "http://127.0.0.1:8000";
export const coreApiBase = `${apiBase.replace(/\/$/, "")}/api/core`;

export async function coreApiRequest(path, options = {}) {
  const { method = "GET", token, body } = options;

  const response = await fetch(`${coreApiBase}${path}`, {
    method,
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: body ? JSON.stringify(body) : undefined,
  });

  if (response.status === 204) {
    return null;
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    // If backend returned a field->messages validation payload,
    // throw it as a JSON string so callers can map messages to fields.
    if (payload && typeof payload === "object" && Object.keys(payload).length > 0 && !payload.detail) {
      throw new Error(JSON.stringify(payload));
    }

    throw new Error(extractApiError(payload));
  }

  return payload;
}

export async function coreApiMultipartRequest(path, options = {}) {
  const { method = "POST", token, formData } = options;

  const response = await fetch(`${coreApiBase}${path}`, {
    method,
    headers: {
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: formData,
  });

  if (response.status === 204) {
    return null;
  }

  const payload = await response.json().catch(() => ({}));
  if (!response.ok) {
    throw new Error(extractApiError(payload));
  }

  return payload;
}
