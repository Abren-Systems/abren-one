import { describe, it, expect } from "vitest";
import { mount } from "@vue/test-utils";
import TransactionDetailModal from "./TransactionDetailModal.vue";
import type { TransactionDetail } from "@/types/inventory";

describe("TransactionDetailModal", () => {
  const mockTransaction: TransactionDetail = {
    id: "tx-123",
    transaction_number: "TXN-202611-0001",
    transaction_type: "receipt_opening",
    status: "posted",
    transaction_date: "2026-11-20",
    source_warehouse_id: null,
    source_warehouse_name: null,
    destination_warehouse_id: "wh-1",
    destination_warehouse_name: "Central Warehouse",
    reference_document: "INIT-COUNT",
    executed_by: null,
    donor_name: "",
    notes: "Opening balance",
    entries: [
      {
        id: "entry-1",
        item_id: "item-1",
        item_name: "Tarpaulin 4x5m",
        item_code: "SHELTER-TARP-01",
        unit_of_measure: "sheets",
        warehouse_id: "wh-1",
        warehouse_name: "Central Warehouse",
        warehouse_code: "C-WH",
        location_id: null,
        location_name: null,
        batch_id: null,
        batch_number: null,
        quantity: "150.00",
        unit_cost: "24.50",
        program_id: null,
        activity_id: null,
      },
    ],
  };

  it("does not render when show is false", () => {
    const wrapper = mount(TransactionDetailModal, {
      props: {
        show: false,
        transaction: mockTransaction,
      },
    });
    expect(wrapper.find(".modal-backdrop").exists()).toBe(false);
  });

  it("renders transaction details and ledger entries when show is true", () => {
    const wrapper = mount(TransactionDetailModal, {
      props: {
        show: true,
        transaction: mockTransaction,
      },
    });
    expect(wrapper.find(".modal-backdrop").exists()).toBe(true);
    expect(wrapper.text()).toContain("Transaction TXN-202611-0001");
    expect(wrapper.text()).toContain("Central Warehouse");
    expect(wrapper.text()).toContain("Tarpaulin 4x5m");
    expect(wrapper.text()).toContain("+150.00 sheets");
  });

  it("emits close event when close button is clicked", async () => {
    const wrapper = mount(TransactionDetailModal, {
      props: {
        show: true,
        transaction: mockTransaction,
      },
    });
    const closeBtn = wrapper.find("button.btn-secondary");
    await closeBtn.trigger("click");
    expect(wrapper.emitted("close")).toHaveLength(1);
  });
});
