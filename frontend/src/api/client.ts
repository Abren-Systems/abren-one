/**
 * Typed API Client for Abren One.
 *
 * Implements conventions defined in `docs/engineering/frontend-conventions.md`:
 * - Session authentication (same-origin cookies)
 * - Auto-injects X-CSRFToken on mutating requests (POST, PUT, PATCH, DELETE)
 * - Auto-injects X-Organization-ID when an active tenant is selected
 */

function getCookie(name: string): string | null {
  const match = document.cookie.match(new RegExp(`(^|;\\s*)(${name})=([^;]*)`));
  return match ? decodeURIComponent(match[3]) : null;
}

let activeOrganizationId: string | null = null;

export function setActiveOrganizationId(orgId: string | null): void {
  activeOrganizationId = orgId;
}

export function getActiveOrganizationId(): string | null {
  return activeOrganizationId;
}

export class ApiError extends Error {
  constructor(
    public status: number,
    public data: any,
    message?: string
  ) {
    super(message || (typeof data === "object" && data?.detail) || `API Error ${status}`);
    this.name = "ApiError";
  }
}

export async function ensureCsrfToken(): Promise<string> {
  let token = getCookie("csrftoken");
  if (!token) {
    try {
      const res = await fetch("/api/v1/auth/csrf/", { credentials: "same-origin" });
      if (res.ok) {
        const data = await res.json();
        token = data.csrfToken;
      }
    } catch {
      // ignore network errors, proceed with existing or blank
    }
  }
  return token || "";
}

async function request<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  const headers = new Headers(options.headers || {});

  // Content-Type default
  if (!headers.has("Content-Type") && options.body && typeof options.body === "string") {
    headers.set("Content-Type", "application/json");
  }

  // Tenant header
  if (activeOrganizationId && !headers.has("X-Organization-ID")) {
    headers.set("X-Organization-ID", activeOrganizationId);
  }

  // CSRF token on mutating requests
  const method = (options.method || "GET").toUpperCase();
  if (["POST", "PUT", "PATCH", "DELETE"].includes(method)) {
    const csrfToken = await ensureCsrfToken();
    if (csrfToken && !headers.has("X-CSRFToken")) {
      headers.set("X-CSRFToken", csrfToken);
    }
  }

  const response = await fetch(endpoint, {
    ...options,
    headers,
    credentials: "same-origin",
  });

  if (response.status === 204) {
    return {} as T;
  }

  const data = await response.json().catch(() => null);

  if (!response.ok) {
    throw new ApiError(response.status, data);
  }

  return data as T;
}

export const api = {
  get<T>(endpoint: string, headers?: HeadersInit): Promise<T> {
    return request<T>(endpoint, { method: "GET", headers });
  },

  post<T>(endpoint: string, body?: any, headers?: HeadersInit): Promise<T> {
    return request<T>(endpoint, {
      method: "POST",
      body: body !== undefined ? JSON.stringify(body) : undefined,
      headers,
    });
  },

  patch<T>(endpoint: string, body?: any, headers?: HeadersInit): Promise<T> {
    return request<T>(endpoint, {
      method: "PATCH",
      body: body !== undefined ? JSON.stringify(body) : undefined,
      headers,
    });
  },

  delete<T>(endpoint: string, headers?: HeadersInit): Promise<T> {
    return request<T>(endpoint, { method: "DELETE", headers });
  },
};
