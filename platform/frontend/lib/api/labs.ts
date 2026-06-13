import { apiClient } from "./client";

export interface DeploymentSummary {
  id: number;
  status: string;
  started_at: string | null;
}

export interface LabTemplate {
  id: number;
  slug: string;
  name: string;
  description: string;
  category: "world" | "firerange" | "thirdparty";
  container_names: string[];
  images: Record<string, string>;
  build_contexts: Record<string, string>;
  start_order: string[];
  network_name: string;
  subnet: string;
  app_ip: string;
  exposed_ports: Record<string, number>;
  access_info: Array<{ key: string; value: string }>;
  volume_names: string[];
  requires_privileged: boolean;
  is_active: boolean;
  current_deployment: DeploymentSummary | null;
}

export async function getLabs(category?: string): Promise<LabTemplate[]> {
  const params = category ? { category } : {};
  const { data } = await apiClient.get<LabTemplate[]>("/labs/", { params });
  return data;
}

export async function getLab(id: number): Promise<LabTemplate> {
  const { data } = await apiClient.get<LabTemplate>(`/labs/${id}`);
  return data;
}
