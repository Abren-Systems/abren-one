export interface UserOrganization {
  organization_id: string;
  name: string;
  slug: string;
  role: "owner" | "admin" | "staff" | "member";
  status: "active" | "suspended" | "pending";
  is_active: boolean;
}

export interface OrganizationDetail {
  id: string;
  name: string;
  slug: string;
  status: string;
  is_active: boolean;
}

export interface Branch {
  id: string;
  organization_id: string;
  name: string;
  code: string;
  is_headquarters: boolean;
  is_active: boolean;
}

export interface Department {
  id: string;
  organization_id: string;
  branch_id: string | null;
  name: string;
  code: string;
  is_active: boolean;
}

export interface Member {
  membership_id: string;
  user_id: string;
  username: string;
  email: string;
  role: string;
  status: string;
  is_active: boolean;
}
