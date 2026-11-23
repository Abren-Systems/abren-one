import { api } from "../client";
import type { Donation, Donor, Grant } from "@/types/fundraising";

export const fundraisingApi = {
  async getDonors(): Promise<Donor[]> {
    return api.get<Donor[]>("/api/v1/fundraising/donors/");
  },

  async createDonor(data: unknown): Promise<{ donor_id: string }> {
    return api.post("/api/v1/fundraising/donors/", data);
  },

  async getGrants(): Promise<Grant[]> {
    return api.get<Grant[]>("/api/v1/fundraising/grants/");
  },

  async createGrant(data: unknown): Promise<{ grant_id: string }> {
    return api.post("/api/v1/fundraising/grants/", data);
  },

  async awardGrant(id: string, notes?: string): Promise<{ grant_id: string; status: string }> {
    return api.post(`/api/v1/fundraising/grants/${id}/award/`, { notes: notes || "" });
  },

  async activateGrant(id: string, notes?: string): Promise<{ grant_id: string; status: string }> {
    return api.post(`/api/v1/fundraising/grants/${id}/activate/`, { notes: notes || "" });
  },

  async closeGrant(id: string, reason?: string): Promise<{ grant_id: string; status: string }> {
    return api.post(`/api/v1/fundraising/grants/${id}/close/`, { reason: reason || "" });
  },

  async getDonations(): Promise<Donation[]> {
    return api.get<Donation[]>("/api/v1/fundraising/donations/");
  },

  async recordDonation(data: unknown): Promise<{ donation_id: string }> {
    return api.post("/api/v1/fundraising/donations/", data);
  },
};
