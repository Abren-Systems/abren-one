import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import CreateVendorModal from "./CreateVendorModal.vue";

describe("CreateVendorModal", () => {
  it("does not render when show is false", () => {
    const wrapper = mount(CreateVendorModal, {
      props: {
        show: false,
        isLoading: false,
      },
    });
    expect(wrapper.find(".modal-backdrop").exists()).toBe(false);
  });

  it("renders form fields and emits submit with payload", async () => {
    const wrapper = mount(CreateVendorModal, {
      props: {
        show: true,
        isLoading: false,
      },
    });
    expect(wrapper.find(".modal-backdrop").exists()).toBe(true);
    expect(wrapper.text()).toContain("Add New Supplier / Vendor");

    // Fill in vendor name
    const inputs = wrapper.findAll("input");
    const nameInput = inputs[0]; // vendorName
    await nameInput.setValue("Acme Relief Supplies");

    // Click submit
    const submitBtn = wrapper.find("button.btn-primary");
    await submitBtn.trigger("click");

    expect(wrapper.emitted("submit")).toHaveLength(1);
    const emittedPayload = wrapper.emitted("submit")![0][0] as any;
    expect(emittedPayload.name).toBe("Acme Relief Supplies");
    expect(emittedPayload.vendor_type).toBe("goods");
    expect(emittedPayload.default_payment_terms).toBe("Net 30");
  });

  it("emits close event when close button is clicked", async () => {
    const wrapper = mount(CreateVendorModal, {
      props: {
        show: true,
        isLoading: false,
      },
    });
    const closeBtn = wrapper.find("button.modal-close");
    await closeBtn.trigger("click");
    expect(wrapper.emitted("close")).toHaveLength(1);
  });
});
