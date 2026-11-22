export interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_staff: boolean;
  is_superuser: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface CsrfResponse {
  csrfToken: string;
}
