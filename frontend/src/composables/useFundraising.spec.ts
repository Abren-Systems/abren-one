import { describe, it, expect, beforeEach, vi } from "vitest";
import { createPinia, setActivePinia } from "pinia";
import { useFundraising } from "./useFundraising";
import { fundraisingApi } from "@/api/modules/fundraising";
import { useTenantStore } from "@/stores/tenant";

describe("useFundraising composable", () => {
  beforeEach(() => {
    setActivePinia(createPinia());
    const tenant = useTenantStore();
    tenant.selectOrganization("org-fundraising-test");
    vi.restoreAllMocks();
  });

  it("loads donors, grants, and donations successfully", async () => {
    vi.spyOn(fundraisingApi, "getDonors").mockResolvedValue([
      {
        id: "donor-1",
        organization_id: "org-fundraising-test",
        name: "Hope Aid International",
        donor_type: "foundation",
        status: "active",
        is_active: true,
        email: "grants@hopeaid.org",
        phone: "+1-555-0199",
      },
    ]);
    vi.spyOn(fundraisingApi, "getGrants").mockResolvedValue([
      {
        id: "grant-1",
        organization_id: "org-fundraising-test",
        donor_id: "donor-1",
        donor_name: "Hope Aid International",
        title: "Disaster Response Grant",
        reference_code: "DRG-2026",
        total_amount: "250000.00",
        currency: "USD",
        status: "proposed",
        is_active: true,
        start_date: "2026-01-01",
        end_date: "2026-12-31",
        program_id: null,
      },
    ]);
    vi.spyOn(fundraisingApi, "getDonations").mockResolvedValue([
      {
        id: "don-1",
        organization_id: "org-fundraising-test",
        donor_id: "donor-1",
        donor_name: "Hope Aid International",
        grant_id: "grant-1",
        program_id: null,
        amount: "50000.00",
        currency: "USD",
        status: "confirmed",
        payment_method: "bank_transfer",
        reference: "WIRE-01",
        received_at: "2026-01-15T00:00:00Z",
      },
    ]);

    const fund = useFundraising();
    await fund.loadData();

    expect(fund.donors.value.length).toBe(1);
    expect(fund.donors.value[0].name).toBe("Hope Aid International");
    expect(fund.grants.value.length).toBe(1);
    expect(fund.grants.value[0].reference_code).toBe("DRG-2026");
    expect(fund.donations.value.length).toBe(1);
    expect(fund.isLoading.value).toBe(false);
    expect(fund.errorMessage.value).toBeNull();
  });

  it("creates donor and refreshes state", async () => {
    const createSpy = vi.spyOn(fundraisingApi, "createDonor").mockResolvedValue({ donor_id: "donor-2" });
    vi.spyOn(fundraisingApi, "getDonors").mockResolvedValue([]);
    vi.spyOn(fundraisingApi, "getGrants").mockResolvedValue([]);
    vi.spyOn(fundraisingApi, "getDonations").mockResolvedValue([]);

    const fund = useFundraising();
    await fund.createDonor({
      name: "Global Health Trust",
      donor_type: "foundation",
      email: "contact@ght.org",
    });

    expect(createSpy).toHaveBeenCalledWith({
      name: "Global Health Trust",
      donor_type: "foundation",
      email: "contact@ght.org",
    });
    expect(fund.successMessage.value).toBe('Donor "Global Health Trust" added successfully.');
  });

  it("creates grant and refreshes state", async () => {
    const createSpy = vi.spyOn(fundraisingApi, "createGrant").mockResolvedValue({ grant_id: "grant-2" });
    vi.spyOn(fundraisingApi, "getDonors").mockResolvedValue([]);
    vi.spyOn(fundraisingApi, "getGrants").mockResolvedValue([]);
    vi.spyOn(fundraisingApi, "getDonations").mockResolvedValue([]);

    const fund = useFundraising();
    await fund.createGrant({
      donor_id: "donor-1",
      title: "Nutrition Support Window",
      reference_code: "NSW-2026",
      total_amount: 100000,
      start_date: "2026-02-01",
      end_date: "2026-08-31",
      currency: "USD",
    });

    expect(createSpy).toHaveBeenCalled();
    expect(fund.successMessage.value).toBe('Grant "Nutrition Support Window" registered successfully.');
  });

  it("awards and activates grant", async () => {
    const awardSpy = vi.spyOn(fundraisingApi, "awardGrant").mockResolvedValue({ grant_id: "grant-1", status: "awarded" });
    const activateSpy = vi.spyOn(fundraisingApi, "activateGrant").mockResolvedValue({ grant_id: "grant-1", status: "active" });
    vi.spyOn(fundraisingApi, "getDonors").mockResolvedValue([]);
    vi.spyOn(fundraisingApi, "getGrants").mockResolvedValue([]);
    vi.spyOn(fundraisingApi, "getDonations").mockResolvedValue([]);

    const fund = useFundraising();
    await fund.awardGrant("grant-1");
    expect(awardSpy).toHaveBeenCalledWith("grant-1", undefined);
    expect(fund.successMessage.value).toBe("Grant awarded successfully.");

    await fund.activateGrant("grant-1");
    expect(activateSpy).toHaveBeenCalledWith("grant-1", undefined);
    expect(fund.successMessage.value).toBe("Grant activated for program implementation.");
  });

  it("records incoming donation", async () => {
    const recordSpy = vi.spyOn(fundraisingApi, "recordDonation").mockResolvedValue({ donation_id: "don-new" });
    vi.spyOn(fundraisingApi, "getDonors").mockResolvedValue([]);
    vi.spyOn(fundraisingApi, "getGrants").mockResolvedValue([]);
    vi.spyOn(fundraisingApi, "getDonations").mockResolvedValue([]);

    const fund = useFundraising();
    await fund.recordDonation({
      donor_id: "donor-1",
      amount: 15000,
      currency: "USD",
      payment_method: "bank_transfer",
    });

    expect(recordSpy).toHaveBeenCalled();
    expect(fund.successMessage.value).toBe("Donation contribution recorded successfully.");
  });
});
