export interface Program {
  id: string;
  organization_id: string;
  name: string;
  description: string;
  status: string;
  is_active: boolean;
  start_date?: string | null;
  end_date?: string | null;
}

export interface Project {
  id: string;
  organization_id: string;
  program_id: string;
  name: string;
  description: string;
  budget_currency: string;
  status: string;
}

export interface Activity {
  id: string;
  organization_id: string;
  project_id: string;
  name: string;
  status: string;
  due_date?: string | null;
}

export interface CreateProgramPayload {
  name: string;
  description?: string;
  start_date?: string | null;
  end_date?: string | null;
}

export interface CreateProjectPayload {
  program_id: string;
  name: string;
  description?: string;
  budget_currency?: string;
}

export interface CreateActivityPayload {
  project_id: string;
  name: string;
  due_date?: string | null;
}
