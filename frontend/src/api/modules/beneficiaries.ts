import { api } from "../client";
import type {
  Beneficiary,
  RecordDeliveryPayload,
  RegisterBeneficiaryPayload,
  ServiceDelivery,
} from "@/types/beneficiary";

export const beneficiariesApi = {
  async getBeneficiaries(): Promise<Beneficiary[]> {
    return api.get<Beneficiary[]>("/api/v1/beneficiaries/");
  },

  async registerBeneficiary(
    data: RegisterBeneficiaryPayload
  ): Promise<{ beneficiary_id: string }> {
    return api.post<{ beneficiary_id: string }>("/api/v1/beneficiaries/", data);
  },

  async getDeliveries(): Promise<ServiceDelivery[]> {
    return api.get<ServiceDelivery[]>("/api/v1/beneficiaries/deliveries/");
  },

  async recordDelivery(
    data: RecordDeliveryPayload
  ): Promise<{ delivery_id: string }> {
    return api.post<{ delivery_id: string }>("/api/v1/beneficiaries/deliveries/", data);
  },
};
