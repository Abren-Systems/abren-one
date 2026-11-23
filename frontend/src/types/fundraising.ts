export interface Donor {
  id: string;
  organization_id: string;
  name: string;
  donor_type: string;
  status: string;
  is_active: boolean;
  email: string;
  phone: string;
}

export interface Grant {
  id: string;
  organization_id: string;
  donor_id: string;
  donor_name: string;
  title: string;
  reference_code: string;
  total_amount: string;
  currency: string;
  status: string;
  is_active: boolean;
  start_date: string;
  end_date: string;
  program_id: string | null;
}

export interface Donation {
  id: string;
  organization_id: string;
  donor_id: string;
  donor_name: string;
  grant_id: string | null;
  program_id: string | null;
  amount: string;
  currency: string;
  status: string;
  payment_method: string;
  reference: string;
  received_at: string;
}

export interface CreateDonorPayload {
  name: string;
  donor_type?: string;
  email?: string;
  phone?: string;
}

export interface CreateGrantPayload {
  donor_id: string;
  title: string;
  reference_code: string;
  total_amount: string | number;
  start_date: string;
  end_date: string;
  currency?: string;
  program_id?: string | null;
}

export interface RecordDonationPayload {
  donor_id: string;
  amount: string | number;
  currency?: string;
  payment_method?: string;
  reference?: string;
  grant_id?: string | null;
  program_id?: string | null;
}
