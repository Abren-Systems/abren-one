import { describe, it, expect, beforeEach, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useProcurement } from "./useProcurement";
import { procurementApi } from "@/api/modules/procurement";
import { useTenantStore } from "@/stores/tenant";

describe("useProcurement composable", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    const tenant = useTenantStore();
    tenant.selectOrganization("org-procurement-200");
    vi.restoreAllMocks();
  });

  it("loads vendors, requisitions, orders, and receipts successfully", async () => {
    vi.spyOn(procurementApi, "getVendors").mockResolvedValue([
      {
        id: "v-1",
        name: "Pharma Supplies Ltd",
        vendor_type: "goods",
        tax_id: "TAX-123",
        country: "ET",
        contact_name: "Abebe",
        email: "abebe@pharma.com",
        default_currency: "USD",
        verification_status: "verified",
        is_active: true,
      },
    ]);
    vi.spyOn(procurementApi, "getRequisitions").mockResolvedValue([]);
    vi.spyOn(procurementApi, "getOrders").mockResolvedValue([]);
    vi.spyOn(procurementApi, "getGoodsReceipts").mockResolvedValue([]);

    const proc = useProcurement();
    await proc.loadData();

    expect(proc.vendors.value.length).toBe(1);
    expect(proc.vendors.value[0].name).toBe("Pharma Supplies Ltd");
    expect(proc.isLoading.value).toBe(false);
    expect(proc.errorMessage.value).toBeNull();
  });

  it("submits requisition approval and updates success message", async () => {
    const approveSpy = vi.spyOn(procurementApi, "approveRequisition").mockResolvedValue(undefined);
    vi.spyOn(procurementApi, "getVendors").mockResolvedValue([]);
    vi.spyOn(procurementApi, "getRequisitions").mockResolvedValue([]);
    vi.spyOn(procurementApi, "getOrders").mockResolvedValue([]);
    vi.spyOn(procurementApi, "getGoodsReceipts").mockResolvedValue([]);

    const proc = useProcurement();
    await proc.approveRequisition("req-1234");

    expect(approveSpy).toHaveBeenCalledWith("req-1234");
    expect(proc.successMessage.value).toBe("Requisition approved.");
  });

  it("issues purchase order and refreshes state", async () => {
    const issueSpy = vi.spyOn(procurementApi, "issueOrder").mockResolvedValue(undefined);
    vi.spyOn(procurementApi, "getVendors").mockResolvedValue([]);
    vi.spyOn(procurementApi, "getRequisitions").mockResolvedValue([]);
    vi.spyOn(procurementApi, "getOrders").mockResolvedValue([]);
    vi.spyOn(procurementApi, "getGoodsReceipts").mockResolvedValue([]);

    const proc = useProcurement();
    await proc.issueOrder("po-5678");

    expect(issueSpy).toHaveBeenCalledWith("po-5678");
    expect(proc.successMessage.value).toBe("Purchase Order issued to vendor.");
  });
});
