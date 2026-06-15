import { apiClient } from "./client";

export interface Rank {
  id: number;
  name: string;
  min_points: number;
  icon: string | null;
  color: string | null;
  is_active: boolean;
}

export interface UserRank {
  points: number;
  rank: Rank | null;
  next_rank: Rank | null;
  progress_pct: number;
}

export async function getRanks(): Promise<Rank[]> {
  const { data } = await apiClient.get<Rank[]>("/ranks/");
  return data;
}

export async function getMyRank(): Promise<UserRank> {
  const { data } = await apiClient.get<UserRank>("/ranks/me");
  return data;
}

export async function getUserRank(userId: number): Promise<UserRank> {
  const { data } = await apiClient.get<UserRank>(`/ranks/users/${userId}`);
  return data;
}

// Admin CRUD

export interface AdminRankCreate {
  name: string;
  min_points: number;
  icon?: string;
  color?: string;
}

export interface AdminRankUpdate {
  name?: string;
  min_points?: number;
  icon?: string;
  color?: string;
  is_active?: boolean;
}

export async function getAdminRanks(): Promise<Rank[]> {
  const { data } = await apiClient.get<Rank[]>("/admin/ranks/");
  return data;
}

export async function createAdminRank(payload: AdminRankCreate): Promise<Rank> {
  const { data } = await apiClient.post<Rank>("/admin/ranks/", payload);
  return data;
}

export async function updateAdminRank(id: number, payload: AdminRankUpdate): Promise<Rank> {
  const { data } = await apiClient.patch<Rank>(`/admin/ranks/${id}`, payload);
  return data;
}

export async function deleteAdminRank(id: number): Promise<void> {
  await apiClient.delete(`/admin/ranks/${id}`);
}
