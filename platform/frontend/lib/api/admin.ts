// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { apiClient } from "./client";

export interface SystemStats {
  user_count: number;
  team_count: number;
  active_deployments: number;
  total_deployments: number;
  api_key_count: number;
  pending_scheduled_actions: number;
}

export interface AdminUser {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  is_owner: boolean;
  platform_roles: string[];
  locked_until: string | null;
  created_at: string;
  last_login_at: string | null;
  team_count: number;
  deployment_count: number;
  api_key_count: number;
}

export interface PlatformRole {
  id: number;
  slug: string;
  display_name: string;
  description: string | null;
  permissions: string[];
  is_system: boolean;
  is_default: boolean;
  created_at: string;
}

export interface PlatformRoleCreate {
  slug: string;
  display_name: string;
  description?: string;
  permissions: string[];
  is_default?: boolean;
}

export interface PlatformRoleUpdate {
  display_name?: string;
  description?: string;
  permissions?: string[];
  is_default?: boolean;
}

export async function listRoles(): Promise<PlatformRole[]> {
  const { data } = await apiClient.get<PlatformRole[]>("/admin/roles/");
  return data;
}

export async function createRole(payload: PlatformRoleCreate): Promise<PlatformRole> {
  const { data } = await apiClient.post<PlatformRole>("/admin/roles/", payload);
  return data;
}

export async function updateRole(slug: string, payload: PlatformRoleUpdate): Promise<PlatformRole> {
  const { data } = await apiClient.patch<PlatformRole>(`/admin/roles/${slug}`, payload);
  return data;
}

export async function deleteRole(slug: string): Promise<void> {
  await apiClient.delete(`/admin/roles/${slug}`);
}

export interface AdminTeam {
  id: number;
  name: string;
  slug: string;
  is_personal: boolean;
  created_by_id: number;
  created_by_username: string;
  member_count: number;
  deployment_count: number;
  created_at: string;
}

export interface AdminAuditLog {
  id: number;
  user_id: number | null;
  username: string | null;
  team_id: number | null;
  team_name: string | null;
  deployment_id: number | null;
  action: string;
  detail: Record<string, unknown>;
  ip_address: string | null;
  created_at: string;
}

export interface AdminApiKey {
  id: number;
  user_id: number;
  username: string;
  name: string;
  key_prefix: string;
  expires_at: string | null;
  last_used_at: string | null;
  is_active: boolean;
  created_at: string;
}

export async function getStats(): Promise<SystemStats> {
  const { data } = await apiClient.get<SystemStats>("/admin/stats");
  return data;
}

export async function getAdminUsers(params?: {
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<AdminUser[]> {
  const { data } = await apiClient.get<AdminUser[]>("/admin/users/", { params });
  return data;
}

export async function createAdminUser(payload: {
  username: string;
  email: string;
  password: string;
  platform_roles?: string[];
}): Promise<AdminUser> {
  const { data } = await apiClient.post<AdminUser>("/admin/users/", payload);
  return data;
}

export async function updateAdminUser(
  id: number,
  payload: { is_active?: boolean; platform_roles?: string[]; unlock?: boolean }
): Promise<AdminUser> {
  const { data } = await apiClient.patch<AdminUser>(`/admin/users/${id}`, payload);
  return data;
}

export async function resetUserPassword(
  id: number,
  newPassword: string
): Promise<void> {
  await apiClient.post(`/admin/users/${id}/reset-password`, {
    new_password: newPassword,
  });
}

export async function getAdminTeams(params?: {
  search?: string;
  limit?: number;
}): Promise<AdminTeam[]> {
  const { data } = await apiClient.get<AdminTeam[]>("/admin/teams/", { params });
  return data;
}

export async function getAdminAuditLogs(params?: {
  action?: string;
  user_id?: number;
  team_id?: number;
  from_date?: string;
  to_date?: string;
  limit?: number;
  offset?: number;
}): Promise<AdminAuditLog[]> {
  const { from_date, to_date, ...rest } = params ?? {};
  const query = {
    ...rest,
    ...(from_date ? { from: from_date } : {}),
    ...(to_date ? { to: to_date } : {}),
  };
  const { data } = await apiClient.get<AdminAuditLog[]>("/admin/audit-logs/", { params: query });
  return data;
}

export async function getAdminApiKeys(params?: {
  user_id?: number;
  active_only?: boolean;
}): Promise<AdminApiKey[]> {
  const { data } = await apiClient.get<AdminApiKey[]>("/admin/api-keys/", { params });
  return data;
}

export interface AdminDeployment {
  id: number;
  lab_name: string;
  lab_category: string;
  started_by_username: string;
  team_name: string | null;
  visibility: "private" | "team" | "public";
  status: string;
  started_at: string | null;
  stopped_at: string | null;
  container_names: string[];
}

export async function getAdminDeployments(params?: {
  status?: string;
  user_id?: number;
  team_id?: number;
  search?: string;
  limit?: number;
  offset?: number;
}): Promise<AdminDeployment[]> {
  const { data } = await apiClient.get<AdminDeployment[]>("/admin/deployments/", { params });
  return data;
}

export async function resetUserPoints(userId: number): Promise<void> {
  await apiClient.post(`/admin/users/${userId}/reset-points`);
}

export async function resetDatabase(): Promise<void> {
  await apiClient.post("/admin/reset-db");
}

export async function stopAllDeployments(): Promise<void> {
  await apiClient.post("/admin/deployments/stop-all");
}
