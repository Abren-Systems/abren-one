import { describe, it, expect, beforeEach, vi } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import LoginView from "./LoginView.vue";
import { useAuthStore } from "@/stores/auth";
import { useToastStore } from "@/stores/toast";

const mockPush = vi.fn();
vi.mock("vue-router", () => ({
  useRouter: () => ({
    push: mockPush,
  }),
}));

describe("LoginView.vue", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    vi.restoreAllMocks();
    mockPush.mockReset();
  });

  it("renders login form with username and password inputs", () => {
    const wrapper = mount(LoginView);
    expect(wrapper.find("input#username").exists()).toBe(true);
    expect(wrapper.find("input#password").exists()).toBe(true);
    expect(wrapper.find("button.login-btn").exists()).toBe(true);
  });

  it("shows inline validation errors when fields are empty", async () => {
    const wrapper = mount(LoginView);

    await wrapper.find("form").trigger("submit");

    expect(wrapper.find("#username-error").text()).toContain("Username is required.");
    expect(wrapper.find("#password-error").text()).toContain("Password is required.");
    expect(mockPush).not.toHaveBeenCalled();
  });

  it("submits login with trimmed credentials and navigates to dashboard", async () => {
    const authStore = useAuthStore();
    const toastStore = useToastStore();
    const loginSpy = vi.spyOn(authStore, "login").mockResolvedValue();
    const toastSpy = vi.spyOn(toastStore, "success");

    const wrapper = mount(LoginView);

    await wrapper.find("input#username").setValue("  testuser  ");
    await wrapper.find("input#password").setValue("secret123");
    await wrapper.find("form").trigger("submit");

    expect(loginSpy).toHaveBeenCalledWith({
      username: "testuser",
      password: "secret123",
    });
    expect(toastSpy).toHaveBeenCalled();
    expect(mockPush).toHaveBeenCalledWith({ name: "dashboard" });
  });

  it("displays server error message on login failure", async () => {
    const authStore = useAuthStore();
    vi.spyOn(authStore, "login").mockRejectedValue({
      data: { detail: "Invalid username or password" },
    });

    const wrapper = mount(LoginView);

    await wrapper.find("input#username").setValue("testuser");
    await wrapper.find("input#password").setValue("wrongpwd");
    await wrapper.find("form").trigger("submit");

    // Wait for promise rejection handling
    await wrapper.vm.$nextTick();

    expect(wrapper.find(".error-banner").text()).toContain("Invalid username or password");
    expect(mockPush).not.toHaveBeenCalled();
  });
});
