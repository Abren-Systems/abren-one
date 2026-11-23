import { describe, it, expect, beforeAll } from "vitest";
import { mount } from "@vue/test-utils";
import RegisterBeneficiaryModal from "./modals/RegisterBeneficiaryModal.vue";

describe("RegisterBeneficiaryModal", () => {
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
    const wrapper = mount(RegisterBeneficiaryModal, {
      props: {
        open: true,
      },
    });

    expect(wrapper.text()).toContain("Register Beneficiary Profile");
    expect(wrapper.find("#ben-type").exists()).toBe(true);
    expect(wrapper.find("#first-name").exists()).toBe(true);
    expect(wrapper.find("#last-name").exists()).toBe(true);
  });

  it("switches to household name input when household is selected", async () => {
    const wrapper = mount(RegisterBeneficiaryModal, {
      props: {
        open: true,
      },
    });

    const typeSelect = wrapper.find("#ben-type");
    await typeSelect.setValue("household");

    expect(wrapper.find("#hh-name").exists()).toBe(true);
    expect(wrapper.find("#first-name").exists()).toBe(false);
  });

  it("emits create on submit with payload", async () => {
    const wrapper = mount(RegisterBeneficiaryModal, {
      props: {
        open: true,
      },
    });

    await wrapper.find("#first-name").setValue("Zara");
    await wrapper.find("#last-name").setValue("Abdi");
    await wrapper.find("#ben-vuln").setValue("critical");
    await wrapper.find("#id-number").setValue("RAT-999");

    const form = wrapper.find("form");
    await form.trigger("submit.prevent");

    expect(wrapper.emitted("create")).toHaveLength(1);
    expect(wrapper.emitted("create")![0][0]).toEqual({
      beneficiary_type: "individual",
      first_name: "Zara",
      last_name: "Abdi",
      household_name: undefined,
      identification_number: "RAT-999",
      vulnerability_level: "critical",
      contact_phone: undefined,
      contact_address: undefined,
    });
  });

  it("emits close when cancel clicked", async () => {
    const wrapper = mount(RegisterBeneficiaryModal, {
      props: {
        open: true,
      },
    });

    const cancelBtn = wrapper.find(".modal-actions button.btn-secondary");
    await cancelBtn.trigger("click");

    expect(wrapper.emitted("close")).toHaveLength(1);
  });
});
