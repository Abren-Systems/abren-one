export interface Beneficiary {
  id: string;
  organization_id: string;
  beneficiary_type: "individual" | "household" | "community";
  identification_number: string;
  display_name: string;
  first_name: string;
  last_name: string;
  household_name: string;
  status: string;
  vulnerability_level: string;
  contact_phone: string;
  contact_address: string;
  is_active: boolean;
}

export interface ServiceDelivery {
  id: string;
  organization_id: string;
  beneficiary_id: string;
  beneficiary_name: string;
  service_type: string;
  status: string;
  delivery_date: string;
  quantity: string;
  unit: string;
  program_id: string | null;
  activity_id: string | null;
  notes: string;
}
