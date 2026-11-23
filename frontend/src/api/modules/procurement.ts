import { api } from "../client";
import type {
  GoodsReceiptNote,
  PurchaseOrder,
  PurchaseRequisition,
  Vendor,
} from "@/types/procurement";

export const procurementApi = {
  // Vendors
  async getVendors(): Promise<Vendor[]> {
    return api.get<Vendor[]>("/api/v1/procurement/vendors/");
  },

  async createVendor(data: unknown): Promise<{ vendor_id: string }> {
    return api.post("/api/v1/procurement/vendors/", data);
  },

  async deactivateVendor(vendorId: string): Promise<void> {
    return api.post(`/api/v1/procurement/vendors/${vendorId}/deactivate/`, {});
  },

  // Requisitions
  async getRequisitions(): Promise<PurchaseRequisition[]> {
    return api.get<PurchaseRequisition[]>("/api/v1/procurement/requisitions/");
  },

  async getRequisition(id: string): Promise<PurchaseRequisition> {
    return api.get<PurchaseRequisition>(`/api/v1/procurement/requisitions/${id}/`);
  },

  async createRequisition(data: unknown): Promise<{ requisition_id: string }> {
    return api.post("/api/v1/procurement/requisitions/", data);
  },

  async submitRequisition(id: string): Promise<void> {
    return api.post(`/api/v1/procurement/requisitions/${id}/submit/`, {});
  },

  async approveRequisition(id: string): Promise<void> {
    return api.post(`/api/v1/procurement/requisitions/${id}/approve/`, {});
  },

  async rejectRequisition(id: string, reason: string): Promise<void> {
    return api.post(`/api/v1/procurement/requisitions/${id}/reject/`, { reason });
  },

  // Purchase Orders
  async getOrders(): Promise<PurchaseOrder[]> {
    return api.get<PurchaseOrder[]>("/api/v1/procurement/orders/");
  },

  async getOrder(id: string): Promise<PurchaseOrder> {
    return api.get<PurchaseOrder>(`/api/v1/procurement/orders/${id}/`);
  },

  async createOrder(data: unknown): Promise<{ order_id: string }> {
    return api.post("/api/v1/procurement/orders/", data);
  },

  async issueOrder(id: string): Promise<void> {
    return api.post(`/api/v1/procurement/orders/${id}/issue/`, {});
  },

  async cancelOrder(id: string, reason: string): Promise<void> {
    return api.post(`/api/v1/procurement/orders/${id}/cancel/`, { reason });
  },

  // Goods Receipts
  async getGoodsReceipts(): Promise<GoodsReceiptNote[]> {
    return api.get<GoodsReceiptNote[]>("/api/v1/procurement/receipts/");
  },

  async getGoodsReceipt(id: string): Promise<GoodsReceiptNote> {
    return api.get<GoodsReceiptNote>(`/api/v1/procurement/receipts/${id}/`);
  },

  async createGoodsReceipt(data: unknown): Promise<{ goods_receipt_id: string }> {
    return api.post("/api/v1/procurement/receipts/", data);
  },

  async inspectGoodsReceipt(id: string, data: unknown): Promise<void> {
    return api.post(`/api/v1/procurement/receipts/${id}/inspect/`, data);
  },
};
