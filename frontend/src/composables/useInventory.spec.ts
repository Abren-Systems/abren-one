import { describe, it, expect, beforeEach, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useInventory } from "./useInventory";
import { inventoryApi } from "@/api/modules/inventory";
import { useTenantStore } from "@/stores/tenant";

describe("useInventory composable", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    const tenant = useTenantStore();
    tenant.selectOrganization("org-inventory-100");
    vi.restoreAllMocks();
  });

  it("loads categories, items, warehouses, and balances successfully", async () => {
    vi.spyOn(inventoryApi, "getCategories").mockResolvedValue([
      { id: "cat-1", name: "Medical", code: "MED", description: "", parent_id: null, parent_name: null },
    ]);
    vi.spyOn(inventoryApi, "getItems").mockResolvedValue([
      {
        id: "item-1",
        item_code: "MED-01",
        name: "First Aid Kit",
        category_id: "cat-1",
        category_name: "Medical",
        unit_of_measure: "each",
        item_type: "consumable",
        track_batches: true,
        track_expiry: true,
        reorder_threshold: "10",
        default_unit_cost: "25",
        is_active: true,
      },
    ]);
    vi.spyOn(inventoryApi, "getWarehouses").mockResolvedValue([
      {
        id: "wh-1",
        name: "Central Hub",
        code: "WH-01",
        warehouse_type: "central_warehouse",
        branch_id: null,
        custodian_id: null,
        is_active: true,
        location_count: 2,
      },
    ]);
    vi.spyOn(inventoryApi, "getBalances").mockResolvedValue([]);
    vi.spyOn(inventoryApi, "getLedgerEntries").mockResolvedValue([]);
    vi.spyOn(inventoryApi, "getAlerts").mockResolvedValue({
      reorder_alerts: [],
      expiring_batches: [],
    });

    const inv = useInventory();
    await inv.loadData();

    expect(inv.categories.value.length).toBe(1);
    expect(inv.categories.value[0].name).toBe("Medical");
    expect(inv.items.value.length).toBe(1);
    expect(inv.items.value[0].item_code).toBe("MED-01");
    expect(inv.warehouses.value.length).toBe(1);
    expect(inv.isLoading.value).toBe(false);
    expect(inv.errorMessage.value).toBeNull();
  });

  it("handles API failure by recording error message", async () => {
    vi.spyOn(inventoryApi, "getCategories").mockRejectedValue(
      new Error("Network connection failure")
    );
    vi.spyOn(inventoryApi, "getItems").mockResolvedValue([]);
    vi.spyOn(inventoryApi, "getWarehouses").mockResolvedValue([]);
    vi.spyOn(inventoryApi, "getBalances").mockResolvedValue([]);
    vi.spyOn(inventoryApi, "getLedgerEntries").mockResolvedValue([]);
    vi.spyOn(inventoryApi, "getAlerts").mockResolvedValue({
      reorder_alerts: [],
      expiring_batches: [],
    });

    const inv = useInventory();
    await inv.loadData();

    expect(inv.isLoading.value).toBe(false);
    expect(inv.errorMessage.value).toBe("Network connection failure");
  });

  it("creates item and triggers refresh", async () => {
    vi.spyOn(inventoryApi, "createItem").mockResolvedValue({ item_id: "new-item-99" });
    const loadSpy = vi.spyOn(inventoryApi, "getCategories").mockResolvedValue([]);
    vi.spyOn(inventoryApi, "getItems").mockResolvedValue([]);
    vi.spyOn(inventoryApi, "getWarehouses").mockResolvedValue([]);
    vi.spyOn(inventoryApi, "getBalances").mockResolvedValue([]);
    vi.spyOn(inventoryApi, "getLedgerEntries").mockResolvedValue([]);
    vi.spyOn(inventoryApi, "getAlerts").mockResolvedValue({
      reorder_alerts: [],
      expiring_batches: [],
    });

    const inv = useInventory();
    const res = await inv.createItem({
      category_id: "cat-1",
      item_code: "NEW-01",
      name: "Surgical Gloves",
      unit_of_measure: "box",
      item_type: "consumable",
      track_batches: true,
      track_expiry: true,
      reorder_threshold: "5",
      default_unit_cost: "12",
    });

    expect(res.item_id).toBe("new-item-99");
    expect(inv.successMessage.value).toBe("Item created successfully.");
    expect(loadSpy).toHaveBeenCalled();
  });
});
