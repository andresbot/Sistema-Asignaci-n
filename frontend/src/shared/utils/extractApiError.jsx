export function extractApiError(payload) {
  if (typeof payload === "string") {
    return payload;
  }

  if (payload?.detail) {
    return payload.detail;
  }

  if (payload?.non_field_errors?.length) {
    return payload.non_field_errors[0];
  }

  const firstField = Object.keys(payload || {})[0];
  if (!firstField) {
    return "Ocurrio un error inesperado.";
  }

  const value = payload[firstField];
  return Array.isArray(value) ? value[0] : String(value);
}
