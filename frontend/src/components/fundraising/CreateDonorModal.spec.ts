import { describe, it, expect, beforeAll } from "vitest";
import { mount } from "@vue/test-utils";
import CreateDonorModal from "./modals/CreateDonorModal.vue";

describe("CreateDonorModal", () => {
  beforeAll(() => {
    if (!HTMLDialogElement.prototype.showModal) {
      HTMLDialogElement.prototype.showModal = function () {
        this.open = true;
      };
    }
    if (!HTMLDialogElement.prototype.close) {
      HTMLDialogElement.prototype.close = function () {
        this.open = false;
      };
    }
  });

  it("renders modal form when open", () => {
    const wrapper = mount(CreateDonorModal, {
      props: {
        open: true,
      },
    });

    expect(wrapper.text()).toContain("Add Supporter / Donor");
    expect(wrapper.find("#donor-name").exists()).toBe(true);
    expect(wrapper.find("#donor-type").exists()).toBe(true);
  });

  it("emits create on submit with payload", async () => {
    const wrapper = mount(CreateDonorModal, {
      props: {
        open: true,
      },
    });

    await wrapper.find("#donor-name").setValue("Nordic Relief Trust");
    await wrapper.find("#donor-type").setValue("foundation");
    await wrapper.find("#donor-email").setValue("nordic@relief.org");

    const form = wrapper.find("form");
    await form.trigger("submit.prevent");

    expect(wrapper.emitted("create")).toHaveLength(1);
    expect(wrapper.emitted("create")![0][0]).toEqual({
      name: "Nordic Relief Trust",
      donor_type: "foundation",
      email: "nordic@relief.org",
      phone: undefined,
    });
  });

  it("emits close when cancel clicked", async () => {
    const wrapper = mount(CreateDonorModal, {
      props: {
        open: true,
      },
    });

    const cancelBtn = wrapper.find(".modal-actions button.btn-secondary");
    await cancelBtn.trigger("click");

    expect(wrapper.emitted("close")).toHaveLength(1);
  });
});
