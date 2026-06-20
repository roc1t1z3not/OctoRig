// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { apiClient } from "./client";

export interface Deployment {
  id: number;
  lab_template_id: number;
  started_by_id: number;
  team_id: number | null;
  challenge_id: number | null;
  instance_for_user_id: number | null;
  auto_destroy_at: string | null;
  dynamic_flag: string | null;
  status: "starting" | "running" | "stopping" | "stopped" | "error";
  visibility: "private" | "team" | "public";
  container_names: string[];
  container_ids: Record<string, string>;
  subnet: string | null;
  app_ip: string | null;
  network_name: string | null;
  access_info: Array<{ key: string; value: string }>;
  error_message: string | null;
  started_at: string | null;
  stopped_at: string | null;
  created_at: string;
  lab_name: string;
  lab_slug: string;
  lab_category: string;
  started_by_username: string;
  team_name: string | null;
}

export async function getDeployments(params?: {
  status?: string;
  team_id?: number;
}): Promise<Deployment[]> {
  const { data } = await apiClient.get<Deployment[]>("/deployments/", { params });
  return data;
}

export async function getDeployment(id: number): Promise<Deployment> {
  const { data } = await apiClient.get<Deployment>(`/deployments/${id}`);
  return data;
}

export async function startDeployment(
  labTemplateId: number,
  options?: { team_id?: number; visibility?: "private" | "team" | "public" }
): Promise<Deployment> {
  const { data } = await apiClient.post<Deployment>("/deployments/", {
    lab_template_id: labTemplateId,
    team_id: options?.team_id ?? null,
    visibility: options?.visibility ?? "private",
  });
  return data;
}

export async function stopDeployment(id: number): Promise<Deployment> {
  const { data } = await apiClient.delete<Deployment>(`/deployments/${id}`);
  return data;
}

export async function restartDeployment(id: number): Promise<Deployment> {
  const { data } = await apiClient.post<Deployment>(`/deployments/${id}/start`);
  return data;
}

export async function removeDeployment(id: number): Promise<void> {
  await apiClient.delete(`/deployments/${id}/purge`);
}

export async function resetDeployment(id: number): Promise<Deployment> {
  const { data } = await apiClient.post<Deployment>(`/deployments/${id}/reset`);
  return data;
}

export async function setDeploymentVisibility(
  id: number,
  visibility: "private" | "team" | "public"
): Promise<Deployment> {
  const { data } = await apiClient.patch<Deployment>(
    `/deployments/${id}/visibility`,
    null,
    { params: { visibility } }
  );
  return data;
}

export async function deployInstance(
  challengeId: number,
  ttlHours = 2
): Promise<Deployment> {
  const { data } = await apiClient.post<Deployment>("/deployments/", {
    challenge_id: challengeId,
    ttl_hours: ttlHours,
  });
  return data;
}

export async function getMyInstance(
  challengeId: number
): Promise<Deployment | null> {
  const { data } = await apiClient.get<Deployment | null>(
    "/deployments/instance",
    { params: { challenge_id: challengeId } }
  );
  return data;
}
