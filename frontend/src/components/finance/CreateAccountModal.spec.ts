import { describe, it, expect, beforeAll } from "vitest";
import { mount } from "@vue/test-utils";
import CreateAccountModal from "./modals/CreateAccountModal.vue";

describe("CreateAccountModal", () => {
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
    const wrapper = mount(CreateAccountModal, {
      props: {
        open: true,
      },
    });

    expect(wrapper.text()).toContain("Add Chart of Accounts Record");
    expect(wrapper.find("#acc-code").exists()).toBe(true);
    expect(wrapper.find("#acc-name").exists()).toBe(true);
    expect(wrapper.find("#acc-type").exists()).toBe(true);
  });

  it("emits create with form data on submit", async () => {
    const wrapper = mount(CreateAccountModal, {
      props: {
        open: true,
      },
    });

    await wrapper.find("#acc-code").setValue("1400");
    await wrapper.find("#acc-name").setValue("Prepaid Expenses");
    await wrapper.find("#acc-type").setValue("asset");
    await wrapper.find("#acc-curr").setValue("USD");

    const form = wrapper.find("form");
    await form.trigger("submit.prevent");

    expect(wrapper.emitted("create")).toHaveLength(1);
    expect(wrapper.emitted("create")![0][0]).toEqual({
      code: "1400",
      name: "Prepaid Expenses",
      account_type: "asset",
      currency: "USD",
      description: "",
    });
  });

  it("emits close when cancel button is clicked", async () => {
    const wrapper = mount(CreateAccountModal, {
      props: {
        open: true,
      },
    });

    const cancelBtn = wrapper.find("button.btn-secondary");
    await cancelBtn.trigger("click");

    expect(wrapper.emitted("close")).toHaveLength(1);
  });
});
