import { describe, it, expect, beforeAll, beforeEach } from "vitest";
import { mount } from "@vue/test-utils";
import { createPinia, setActivePinia } from "pinia";
import CreateBranchModal from "./modals/CreateBranchModal.vue";

beforeAll(() => {
  HTMLDialogElement.prototype.showModal = function () {
    this.setAttribute("open", "");
  };
  HTMLDialogElement.prototype.close = function () {
    this.removeAttribute("open");
  };
});

describe("CreateBranchModal.vue", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
  });

  it("renders form fields when open", () => {
    const wrapper = mount(CreateBranchModal, {
      props: { open: true },
    });

    expect(wrapper.find("input#branch-name").exists()).toBe(true);
    expect(wrapper.find("input#branch-code").exists()).toBe(true);
  });

  it("emits create with correct payload on submit", async () => {
    const wrapper = mount(CreateBranchModal, {
      props: { open: true },
    });

    await wrapper.find("input#branch-name").setValue("Field Office South");
    await wrapper.find("input#branch-code").setValue("fo-s");
    await wrapper.find("form").trigger("submit");

    expect(wrapper.emitted("create")).toBeTruthy();
    const payload = wrapper.emitted("create")![0][0] as any;
    expect(payload.name).toBe("Field Office South");
    expect(payload.code).toBe("FO-S"); // toUpperCase applied
  });

  it("does not emit create when name is empty", async () => {
    const wrapper = mount(CreateBranchModal, {
      props: { open: true },
    });

    await wrapper.find("input#branch-code").setValue("HQ");
    await wrapper.find("form").trigger("submit");

    expect(wrapper.emitted("create")).toBeFalsy();
  });

  it("emits close when Cancel button clicked", async () => {
    const wrapper = mount(CreateBranchModal, {
      props: { open: true },
    });

    await wrapper.find("button.btn-secondary").trigger("click");
    expect(wrapper.emitted("close")).toBeTruthy();
  });
});
