import { describe, it, expect, beforeEach, vi } from "vitest";
import {
  api,
  ApiError,
  getActiveOrganizationId,
  setActiveOrganizationId,
} from "./client";

describe("API Client", () => {
  beforeEach(() => {
    setActiveOrganizationId(null);
    vi.restoreAllMocks();
  });

  it("manages active organization ID in memory and injects header", async () => {
    expect(getActiveOrganizationId()).toBeNull();
    setActiveOrganizationId("org-1234");
    expect(getActiveOrganizationId()).toBe("org-1234");

    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ status: "ok" }), {
        status: 200,
        headers: { "Content-Type": "application/json" },
      })
    );

    const res = await api.get<{ status: string }>("/api/v1/test/");
    expect(res).toEqual({ status: "ok" });
    expect(fetchSpy).toHaveBeenCalledTimes(1);

    const callArgs = fetchSpy.mock.calls[0];
    const options = callArgs[1] as RequestInit;
    const headers = options.headers as Headers;
    expect(headers.get("X-Organization-ID")).toBe("org-1234");
  });

  it("injects CSRF token from cookie on POST requests", async () => {
    Object.defineProperty(document, "cookie", {
      writable: true,
      value: "csrftoken=mock-csrf-token-abc;",
    });

    const fetchSpy = vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(JSON.stringify({ created: true }), {
        status: 201,
        headers: { "Content-Type": "application/json" },
      })
    );

    const res = await api.post("/api/v1/test/", { name: "Sample" });
    expect(res).toEqual({ created: true });

    const callArgs = fetchSpy.mock.calls[0];
    const options = callArgs[1] as RequestInit;
    const headers = options.headers as Headers;
    expect(headers.get("X-CSRFToken")).toBe("mock-csrf-token-abc");
    expect(headers.get("Content-Type")).toBe("application/json");
  });

  it("throws typed ApiError on 4xx/5xx responses", async () => {
    vi.spyOn(globalThis, "fetch").mockImplementation(() =>
      Promise.resolve(
        new Response(
          JSON.stringify({ detail: "Insufficient stock available" }),
          {
            status: 400,
            headers: { "Content-Type": "application/json" },
          }
        )
      )
    );

    await expect(api.get("/api/v1/test/")).rejects.toThrow(ApiError);

    try {
      await api.get("/api/v1/test/");
    } catch (err) {
      expect(err).toBeInstanceOf(ApiError);
      const apiErr = err as ApiError;
      expect(apiErr.status).toBe(400);
      expect(apiErr.message).toBe("Insufficient stock available");
    }
  });

  it("handles 204 No Content gracefully", async () => {
    vi.spyOn(globalThis, "fetch").mockResolvedValue(
      new Response(null, { status: 204 })
    );

    const res = await api.delete("/api/v1/test/item-1/");
    expect(res).toEqual({});
  });
});
