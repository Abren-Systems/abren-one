import { api } from "../client";
import type {
  Branch,
  Department,
  Member,
} from "@/types/organization";

export interface CreateBranchPayload {
  name: string;
  code: string;
}

export interface CreateDepartmentPayload {
  name: string;
  code: string;
}

export const organizationsApi = {
  async getBranches(): Promise<Branch[]> {
    return api.get<Branch[]>("/api/v1/organizations/branches/");
  },

  async createBranch(
    data: CreateBranchPayload
  ): Promise<{ branch_id: string }> {
    return api.post<{ branch_id: string }>("/api/v1/organizations/branches/", data);
  },

  async getDepartments(): Promise<Department[]> {
    return api.get<Department[]>("/api/v1/organizations/departments/");
  },

  async createDepartment(
    data: CreateDepartmentPayload
  ): Promise<{ department_id: string }> {
    return api.post<{ department_id: string }>(
      "/api/v1/organizations/departments/",
      data
    );
  },

  async getMembers(): Promise<Member[]> {
    return api.get<Member[]>("/api/v1/organizations/members/");
  },
};
