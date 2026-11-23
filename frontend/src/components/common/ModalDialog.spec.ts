import { describe, it, expect, beforeAll } from "vitest";
import { mount } from "@vue/test-utils";
import ModalDialog from "./ModalDialog.vue";

describe("ModalDialog", () => {
  beforeAll(() => {
    // Ensure HTMLDialogElement methods exist in happy-dom environment
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

  it("renders title and content inside slot", () => {
    const wrapper = mount(ModalDialog, {
      props: {
        show: true,
        title: "Test Dialog Header",
      },
      slots: {
        default: '<div class="dialog-content">Sample Form Body</div>',
      },
    });

    expect(wrapper.find("#modal-title").text()).toBe("Test Dialog Header");
    expect(wrapper.find(".dialog-content").text()).toBe("Sample Form Body");
  });

  it("emits close event when close button is clicked", async () => {
    const wrapper = mount(ModalDialog, {
      props: {
        show: true,
        title: "Closable Dialog",
      },
    });

    const closeBtn = wrapper.find(".modal-close-btn");
    expect(closeBtn.exists()).toBe(true);
    await closeBtn.trigger("click");
    expect(wrapper.emitted("close")).toBeTruthy();
    expect(wrapper.emitted("close")?.length).toBe(1);
  });

  it("renders footer slot content when provided", () => {
    const wrapper = mount(ModalDialog, {
      props: {
        show: true,
        title: "Dialog With Footer",
      },
      slots: {
        footer: '<button class="footer-btn">Submit Action</button>',
      },
    });

    expect(wrapper.find(".modal-footer").exists()).toBe(true);
    expect(wrapper.find(".footer-btn").text()).toBe("Submit Action");
  });
});
