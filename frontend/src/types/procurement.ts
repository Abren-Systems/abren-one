export interface Vendor {
  id: string;
  name: string;
  vendor_type: "goods" | "services" | "consulting";
  tax_id: string;
  country: string;
  contact_name: string;
  email: string;
  phone?: string;
  address?: string;
  default_payment_terms?: string;
  default_currency: string;
  verification_status: "unverified" | "verified" | "suspended";
  is_active: boolean;
  notes?: string;
}

export interface RequisitionItem {
  id: string;
  description: string;
  quantity: string | number;
  unit: string;
  estimated_unit_price: string | number;
  line_total: string | number;
  program_id: string | null;
  activity_id: string | null;
  department_id: string | null;
  allocated_quantity?: string | number;
  outstanding_quantity?: string | number;
}

export interface PurchaseRequisition {
  id: string;
  requisition_number: string;
  title: string;
  authorization_status: "draft" | "submitted" | "approved" | "rejected" | "cancelled";
  currency: string;
  total_estimated_cost: string | number;
  requested_by: string;
  approved_by: string | null;
  approved_at: string | null;
  rejection_reason?: string;
  notes?: string;
  created_at: string;
  item_count?: number;
  items?: RequisitionItem[];
  fulfillment_position?: string;
}

export interface RequisitionFulfillmentItem {
  item_id: string;
  description: string;
  quantity_requested: string | number;
  unit: string;
  quantity_ordered: string | number;
  quantity_accepted: string | number;
  quantity_outstanding_order: string | number;
  quantity_outstanding_delivery: string | number;
}

export interface RequisitionFulfillment {
  requisition_id: string;
  requisition_number: string;
  authorization_status: string;
  fulfillment_position: "NOT_ORDERED" | "PARTIALLY_ORDERED" | "FULLY_ORDERED" | "PARTIALLY_FULFILLED" | "FULLY_FULFILLED";
  items: RequisitionFulfillmentItem[];
}

export interface PurchaseOrderItem {
  id: string;
  description: string;
  quantity: string | number;
  unit: string;
  unit_price: string | number;
  line_total: string | number;
  quantity_received?: string | number;
  quantity_accepted?: string | number;
  quantity_outstanding?: string | number;
}

export interface PurchaseOrder {
  id: string;
  order_number: string;
  vendor_id: string;
  vendor_name: string;
  requisition_id: string | null;
  requisition_number?: string;
  status: "draft" | "issued" | "closed" | "cancelled";
  currency: string;
  total_amount: string | number;
  payment_terms: string;
  issued_at: string | null;
  issued_by?: string | null;
  expected_delivery_date?: string | null;
  delivery_address?: string;
  terms_and_conditions?: string;
  cancellation_reason?: string;
  notes?: string;
  created_at: string;
  item_count?: number;
  items?: PurchaseOrderItem[];
}

export interface OrderDeliveryItem {
  po_item_id: string;
  description: string;
  quantity_ordered: string | number;
  unit: string;
  unit_price: string | number;
  quantity_received: string | number;
  quantity_accepted: string | number;
  quantity_rejected: string | number;
  quantity_outstanding: string | number;
}

export interface OrderDeliveryPosition {
  order_id: string;
  order_number: string;
  status: string;
  delivery_position: "NOT_DELIVERED" | "PARTIALLY_DELIVERED" | "FULLY_DELIVERED" | "OVER_DELIVERED";
  items: OrderDeliveryItem[];
}

export interface GoodsReceiptItem {
  id: string;
  po_item_id: string;
  description?: string;
  quantity_received: string | number;
  quantity_accepted: string | number;
  quantity_rejected: string | number;
  is_inspected: boolean;
  rejection_reason?: string;
}

export interface GoodsReceiptNote {
  id: string;
  receipt_number: string;
  purchase_order_id: string;
  order_number?: string;
  receipt_type: "goods" | "services";
  received_date: string;
  received_by: string;
  inspection_notes?: string;
  is_correction: boolean;
  corrects_id?: string | null;
  is_fully_inspected: boolean;
  has_rejections: boolean;
  item_count?: number;
  created_at?: string;
  items?: GoodsReceiptItem[];
}
