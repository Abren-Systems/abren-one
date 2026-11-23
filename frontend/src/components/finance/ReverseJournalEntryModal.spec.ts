import { describe, it, expect, beforeAll } from "vitest";
import { mount } from "@vue/test-utils";
import ReverseJournalEntryModal from "./modals/ReverseJournalEntryModal.vue";
import type { JournalEntry } from "@/types/finance";

const mockEntry: JournalEntry = {
  id: "je-100",
  entry_number: "JE-2026-0099",
  entry_date: "2026-02-01",
  memo: "Erroneous Expense Entry",
  status: "posted",
  currency: "USD",
  total_amount: "300.00",
  reversal_of_id: null,
};

describe("ReverseJournalEntryModal", () => {
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

  it("renders reversal warning and entry details", () => {
    const wrapper = mount(ReverseJournalEntryModal, {
      props: {
        open: true,
        entry: mockEntry,
      },
    });

    expect(wrapper.text()).toContain("Reverse Journal Entry");
    expect(wrapper.text()).toContain("JE-2026-0099");
    expect(wrapper.text()).toContain("Erroneous Expense Entry");
    expect(wrapper.text()).toContain("Accounting Principle");
  });

  it("emits confirm with entry ID and reason on submit", async () => {
    const wrapper = mount(ReverseJournalEntryModal, {
      props: {
        open: true,
        entry: mockEntry,
      },
    });

    const textarea = wrapper.find("textarea#rev-reason");
    await textarea.setValue("Duplicate entry entered by field office");

    const form = wrapper.find("form");
    await form.trigger("submit.prevent");

    expect(wrapper.emitted("confirm")).toHaveLength(1);
    expect(wrapper.emitted("confirm")![0]).toEqual([
      "je-100",
      "Duplicate entry entered by field office",
    ]);
  });

  it("emits close when cancel clicked", async () => {
    const wrapper = mount(ReverseJournalEntryModal, {
      props: {
        open: true,
        entry: mockEntry,
      },
    });

    const cancelBtn = wrapper.find("button.btn-secondary");
    await cancelBtn.trigger("click");

    expect(wrapper.emitted("close")).toHaveLength(1);
  });
});
