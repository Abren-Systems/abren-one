import { describe, it, expect, beforeAll } from "vitest";
import { mount } from "@vue/test-utils";
import CreateJournalEntryModal from "./modals/CreateJournalEntryModal.vue";
import type { Account } from "@/types/finance";

const mockAccounts: Account[] = [
  {
    id: "acc-1",
    code: "1010",
    name: "Cash and Bank",
    account_type: "asset",
    currency: "USD",
    is_active: true,
  },
  {
    id: "acc-2",
    code: "5010",
    name: "Relief Supplies Expense",
    account_type: "expense",
    currency: "USD",
    is_active: true,
  },
];

describe("CreateJournalEntryModal", () => {
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

  it("renders modal form with initial 2 lines", () => {
    const wrapper = mount(CreateJournalEntryModal, {
      props: {
        open: true,
        accounts: mockAccounts,
      },
    });

    expect(wrapper.text()).toContain("Record Balanced Journal Entry");
    expect(wrapper.find("#je-memo").exists()).toBe(true);
    expect(wrapper.findAll(".line-row").length).toBe(2);
  });

  it("adds and removes lines", async () => {
    const wrapper = mount(CreateJournalEntryModal, {
      props: {
        open: true,
        accounts: mockAccounts,
      },
    });

    const addBtn = wrapper.find(".legs-header button");
    await addBtn.trigger("click");
    expect(wrapper.findAll(".line-row").length).toBe(3);

    const removeBtns = wrapper.findAll("button.btn-icon");
    await removeBtns[2].trigger("click");
    expect(wrapper.findAll(".line-row").length).toBe(2);
  });

  it("submits balanced journal entry", async () => {
    const wrapper = mount(CreateJournalEntryModal, {
      props: {
        open: true,
        accounts: mockAccounts,
      },
    });

    await wrapper.find("#je-memo").setValue("Field Aid Purchase");

    const lineRows = wrapper.findAll(".line-row");
    // Line 1: select acc-2, debit 250, credit 0
    await lineRows[0].find("select").setValue("acc-2");
    const line1Inputs = lineRows[0].findAll(".amount-col input");
    await line1Inputs[0].setValue(250);

    // Line 2: select acc-1, debit 0, credit 250
    await lineRows[1].find("select").setValue("acc-1");
    const line2Inputs = lineRows[1].findAll(".amount-col input");
    await line2Inputs[1].setValue(250);

    // Check balance banner
    expect(wrapper.text()).toContain("✓ Balanced");

    const form = wrapper.find("form");
    await form.trigger("submit.prevent");

    expect(wrapper.emitted("create")).toHaveLength(1);
    const payload = wrapper.emitted("create")![0][0] as any;
    expect(payload.memo).toBe("Field Aid Purchase");
    expect(payload.lines).toHaveLength(2);
    expect(payload.lines[0].debit).toBe(250);
    expect(payload.lines[1].credit).toBe(250);
  });

  it("emits close when cancel clicked", async () => {
    const wrapper = mount(CreateJournalEntryModal, {
      props: {
        open: true,
        accounts: mockAccounts,
      },
    });

    const cancelBtn = wrapper.find(".modal-actions button.btn-secondary");
    await cancelBtn.trigger("click");

    expect(wrapper.emitted("close")).toHaveLength(1);
  });
});
