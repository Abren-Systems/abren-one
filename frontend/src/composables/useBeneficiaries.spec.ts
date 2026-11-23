import { describe, it, expect, beforeEach, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useBeneficiaries } from "./useBeneficiaries";
import { beneficiariesApi } from "@/api/modules/beneficiaries";
import { useTenantStore } from "@/stores/tenant";

describe("useBeneficiaries composable", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    const tenant = useTenantStore();
    tenant.selectOrganization("org-beneficiary-test");
    vi.restoreAllMocks();
  });

  it("loads beneficiaries and deliveries successfully", async () => {
    vi.spyOn(beneficiariesApi, "getBeneficiaries").mockResolvedValue([
      {
        id: "ben-1",
        organization_id: "org-beneficiary-test",
        beneficiary_type: "individual",
        identification_number: "ID-12345",
        display_name: "Fatima Ali",
        first_name: "Fatima",
        last_name: "Ali",
        household_name: "",
        status: "active",
        vulnerability_level: "high",
        contact_phone: "+251 91 123 4567",
        contact_address: "Zone 1",
        is_active: true,
      },
    ]);
    vi.spyOn(beneficiariesApi, "getDeliveries").mockResolvedValue([
      {
        id: "del-1",
        organization_id: "org-beneficiary-test",
        beneficiary_id: "ben-1",
        beneficiary_name: "Fatima Ali",
        service_type: "food_assistance",
        status: "delivered",
        delivery_date: "2026-02-01",
        quantity: "2.00",
        unit: "rations",
        program_id: null,
        activity_id: null,
        notes: "Monthly ration kit",
      },
    ]);

    const bens = useBeneficiaries();
    await bens.loadData();

    expect(bens.beneficiaries.value.length).toBe(1);
    expect(bens.beneficiaries.value[0].display_name).toBe("Fatima Ali");
    expect(bens.deliveries.value.length).toBe(1);
    expect(bens.isLoading.value).toBe(false);
    expect(bens.errorMessage.value).toBeNull();
  });

  it("registers beneficiary and refreshes state", async () => {
    const regSpy = vi.spyOn(beneficiariesApi, "registerBeneficiary").mockResolvedValue({ beneficiary_id: "ben-2" });
    vi.spyOn(beneficiariesApi, "getBeneficiaries").mockResolvedValue([]);
    vi.spyOn(beneficiariesApi, "getDeliveries").mockResolvedValue([]);

    const bens = useBeneficiaries();
    await bens.registerBeneficiary({
      beneficiary_type: "individual",
      first_name: "Ahmed",
      last_name: "Hassan",
      vulnerability_level: "critical",
    });

    expect(regSpy).toHaveBeenCalledWith({
      beneficiary_type: "individual",
      first_name: "Ahmed",
      last_name: "Hassan",
      vulnerability_level: "critical",
    });
    expect(bens.successMessage.value).toBe('Registered "Ahmed Hassan" successfully.');
  });

  it("records service delivery and refreshes state", async () => {
    const delSpy = vi.spyOn(beneficiariesApi, "recordDelivery").mockResolvedValue({ delivery_id: "del-2" });
    vi.spyOn(beneficiariesApi, "getBeneficiaries").mockResolvedValue([]);
    vi.spyOn(beneficiariesApi, "getDeliveries").mockResolvedValue([]);

    const bens = useBeneficiaries();
    await bens.recordDelivery({
      beneficiary_id: "ben-1",
      service_type: "medical_support",
      delivery_date: "2026-02-02",
      quantity: 1,
      unit: "kit",
    });

    expect(delSpy).toHaveBeenCalled();
    expect(bens.successMessage.value).toBe("Service delivery event recorded successfully.");
  });
});
