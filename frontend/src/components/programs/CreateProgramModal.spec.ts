import { describe, it, expect, beforeAll, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import CreateProgramModal from "./modals/CreateProgramModal.vue";

beforeAll(() => {
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute("open");
  };
});

describe("CreateProgramModal.vue", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("renders form fields when open", () => {
    const wrapper = mount(CreateProgramModal, {
      props: { open: true },
    });

    expect(wrapper.find("input#prog-name").exists()).toBe(true);
    expect(wrapper.find("textarea#prog-desc").exists()).toBe(true);
    expect(wrapper.find("input#prog-start").exists()).toBe(true);
    expect(wrapper.find("input#prog-end").exists()).toBe(true);
  });

  it("emits create with correct payload on submit", async () => {
    const wrapper = mount(CreateProgramModal, {
      props: { open: true },
    });

    await wrapper.find("input#prog-name").setValue("Health Response");
    await wrapper.find("textarea#prog-desc").setValue("Multi-year health program");
    await wrapper.find("input#prog-start").setValue("2026-01-01");
    await wrapper.find("input#prog-end").setValue("2026-12-31");
    await wrapper.find("form").trigger("submit");

    expect(wrapper.emitted("create")).toBeTruthy();
    const payload = wrapper.emitted("create")![0][0] as any;
    expect(payload.name).toBe("Health Response");
    expect(payload.description).toBe("Multi-year health program");
    expect(payload.start_date).toBe("2026-01-01");
    expect(payload.end_date).toBe("2026-12-31");
  });

  it("emits close when Cancel button clicked", async () => {
    const wrapper = mount(CreateProgramModal, {
      props: { open: true },
    });

    await wrapper.find("button.btn-secondary").trigger("click");
    expect(wrapper.emitted("close")).toBeTruthy();
  });
});
