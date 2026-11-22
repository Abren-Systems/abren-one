# Procurement Module

## Overview

The Procurement module manages supplier relationships, spend requests, commercial purchasing commitments, and physical delivery verification for organizations operating within Abren One.

It is designed as an operational capability within a coherent NGO operating system: connecting organizational needs, program activities, purchasing decisions, financial commitments, delivery verification, and supplier obligations.

## Principles

1. **Separation of Authorization Lifecycle & Fulfillment**: Requisition authorization status (`DRAFT`, `SUBMITTED`, `APPROVED`, `REJECTED`, `CANCELLED`) tracks spend approvals. Fulfillment position (`NOT_ORDERED`, `PARTIALLY_ORDERED`, `FULLY_ORDERED`, `PARTIALLY_FULFILLED`, `FULLY_FULFILLED`) is derived from allocation and receipt data, never stored as a static enum.
2. **Line-Level Traceability & Attribution**: Requisition items carry line-level program, activity, and department attribution. `OrderLineAllocation` explicitly maps requisition line items to purchase order line items with quantity tracking.
3. **Item-Level Inspection & Reconciliation**: Goods receipts track physical counts and require explicit item-level inspection reconciliation: `quantity_accepted + quantity_rejected == quantity_received`.
4. **Controlled Financial Integration Contract**: Procurement exposes frozen DTOs through `public.py` for Finance commitment tracking, 3-way matching, and AP recognition without coupling to General Ledger tables.
5. **Rigorous Tenant Isolation & Segregation of Duties**: Requesters cannot approve their own requisitions. Soft references across modules are validated within the active tenant organization.

## Entities

- **Vendor (`Vendor`)**: Supplier master record with classification (`GOODS`, `SERVICES`, `CONSULTING`), verification status, default currency, and payment terms.
- **Purchase Requisition (`PurchaseRequisition`)**: Authorization document tracking organizational need and approval lifecycle.
- **Requisition Item (`RequisitionItem`)**: Line-level requirement with operational attribution (`program_id`, `activity_id`, `department_id`).
- **Purchase Order (`PurchaseOrder`)**: Commercial commitment to a supplier with snapshotted payment terms.
- **Purchase Order Item (`PurchaseOrderItem`)**: Line-level contracted quantity and price.
- **Order Line Allocation (`OrderLineAllocation`)**: Explicit join entity linking requisition items to purchase order items.
- **Goods Receipt Note (`GoodsReceiptNote`)**: Evidence of physical delivery or service completion.
- **Goods Receipt Item (`GoodsReceiptItem`)**: Line-level receipt with item inspection state and accepted/rejected quantities.

## Public Interface (`public.py`)

- **Commitment Visibility DTOs**: `ProcurementCommitmentItem`, `ProcurementCommitmentSummary`, `AcceptedReceiptItem`
- **Public Queries**:
  - `get_outstanding_commitments(organization_id, program_id=None, limit=100, offset=0)`
  - `get_commitment_detail(organization_id, po_id)`
  - `get_accepted_receipts_for_order(organization_id, po_id)`
  - `get_unmatched_accepted_receipts(organization_id, limit=100, offset=0)`
