import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import JournalEntriesTab from "./tabs/JournalEntriesTab.vue";
import type { JournalEntry } from "@/types/finance";

const mockEntries: JournalEntry[] = [
  {
    id: "je-1",
    entry_number: "JE-2026-0001",
    entry_date: "2026-01-15",
    memo: "Opening Bank Deposit",
    currency: "USD",
    status: "draft",
    total_amount: "5000.00",
    reversal_of_id: null,
  },
  {
    id: "je-2",
    entry_number: "JE-2026-0002",
    entry_date: "2026-01-16",
    memo: "Relief Goods Purchase",
    currency: "USD",
    status: "posted",
    total_amount: "1200.00",
    reversal_of_id: null,
  },
];

describe("JournalEntriesTab", () => {
  it("renders journal entries and their lines", () => {
    const wrapper = mount(JournalEntriesTab, {
      props: {
        journalEntries: mockEntries,
      },
    });

    expect(wrapper.text()).toContain("JE-2026-0001");
    expect(wrapper.text()).toContain("Opening Bank Deposit");
    expect(wrapper.text()).toContain("JE-2026-0002");
    expect(wrapper.text()).toContain("Relief Goods Purchase");
    expect(wrapper.findAll("tbody tr").length).toBe(2);
  });

  it("filters journal entries by search query", async () => {
    const wrapper = mount(JournalEntriesTab, {
      props: {
        journalEntries: mockEntries,
      },
    });

    const searchInput = wrapper.find('input[type="search"]');
    await searchInput.setValue("Relief");

    expect(wrapper.findAll("tbody tr").length).toBe(1);
    expect(wrapper.text()).toContain("Relief Goods Purchase");
    expect(wrapper.text()).not.toContain("Opening Bank Deposit");
  });

  it("filters journal entries by status", async () => {
    const wrapper = mount(JournalEntriesTab, {
      props: {
        journalEntries: mockEntries,
      },
    });

    const select = wrapper.find("select.filter-select");
    await select.setValue("draft");

    expect(wrapper.findAll("tbody tr").length).toBe(1);
    expect(wrapper.text()).toContain("JE-2026-0001");
    expect(wrapper.text()).not.toContain("JE-2026-0002");
  });

  it("emits postEntry when Post to Ledger button is clicked", async () => {
    const wrapper = mount(JournalEntriesTab, {
      props: {
        journalEntries: mockEntries,
      },
    });

    const postBtn = wrapper.find("button.btn-post");
    expect(postBtn.exists()).toBe(true);
    await postBtn.trigger("click");

    expect(wrapper.emitted("postEntry")).toHaveLength(1);
    expect(wrapper.emitted("postEntry")![0]).toEqual(["je-1"]);
  });

  it("emits reverseEntry when Reverse Entry button is clicked", async () => {
    const wrapper = mount(JournalEntriesTab, {
      props: {
        journalEntries: mockEntries,
      },
    });

    const reverseBtn = wrapper.find("button.btn-reverse");
    expect(reverseBtn.exists()).toBe(true);
    await reverseBtn.trigger("click");

    expect(wrapper.emitted("reverseEntry")).toHaveLength(1);
    expect(wrapper.emitted("reverseEntry")![0][0]).toEqual(mockEntries[1]);
  });

  it("emits openCreateEntry when Record Journal Entry button is clicked", async () => {
    const wrapper = mount(JournalEntriesTab, {
      props: {
        journalEntries: mockEntries,
      },
    });

    const createBtn = wrapper.find("button.btn-primary");
    await createBtn.trigger("click");

    expect(wrapper.emitted("openCreateEntry")).toHaveLength(1);
  });
});
