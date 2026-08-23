export interface User {
  id: string;
  email: string;
  full_name: string;
  role: "patient" | "doctor" | "admin";
  is_active: boolean;
}

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface RegisterPayload {
  email: string;
  password: string;
  full_name: string;
}

export interface LoginPayload {
  email: string;
  password: string;
}
