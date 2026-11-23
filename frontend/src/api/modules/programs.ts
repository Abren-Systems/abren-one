import { api } from "../client";
import type {
  Activity,
  CreateActivityPayload,
  CreateProgramPayload,
  CreateProjectPayload,
  Program,
  Project,
} from "@/types/program";

export const programsApi = {
  async getPrograms(): Promise<Program[]> {
    return api.get<Program[]>("/api/v1/programs/");
  },

  async createProgram(
    data: CreateProgramPayload
  ): Promise<{ program_id: string }> {
    return api.post<{ program_id: string }>("/api/v1/programs/", data);
  },

  async getProjects(): Promise<Project[]> {
    return api.get<Project[]>("/api/v1/programs/projects/");
  },

  async createProject(
    data: CreateProjectPayload
  ): Promise<{ project_id: string }> {
    return api.post<{ project_id: string }>("/api/v1/programs/projects/", data);
  },

  async getActivities(): Promise<Activity[]> {
    return api.get<Activity[]>("/api/v1/programs/activities/");
  },

  async createActivity(
    data: CreateActivityPayload
  ): Promise<{ activity_id: string }> {
    return api.post<{ activity_id: string }>("/api/v1/programs/activities/", data);
  },
};
