// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { apiClient } from "./client";

export type TeamRole = "owner" | "manager" | "member" | "viewer";

export const TEAM_ROLES: TeamRole[] = ["owner", "manager", "member", "viewer"];
export const ASSIGNABLE_ROLES: TeamRole[] = ["manager", "member", "viewer"];

export interface Team {
  id: number;
  name: string;
  slug: string;
  description: string | null;
  is_personal: boolean;
  created_by_id: number;
  created_at: string;
  updated_at: string;
}

export interface TeamWithRole extends Team {
  my_role: TeamRole;
  member_count: number;
}

export interface TeamMember {
  id: number;
  team_id: number;
  user_id: number;
  username: string;
  email: string;
  role: TeamRole;
  joined_at: string;
}

export interface TeamInvitation {
  id: number;
  team_id: number;
  email: string;
  role: TeamRole;
  token: string;
  expires_at: string;
  accepted_at: string | null;
  created_at: string;
}

export interface InvitationDetail {
  team_name: string;
  team_slug: string;
  role: TeamRole;
  invited_by_username: string;
  expires_at: string;
}

export async function getTeams(): Promise<TeamWithRole[]> {
  const { data } = await apiClient.get<TeamWithRole[]>("/teams/");
  return data;
}

export async function getTeam(id: number): Promise<TeamWithRole> {
  const { data } = await apiClient.get<TeamWithRole>(`/teams/${id}`);
  return data;
}

export async function createTeam(payload: {
  name: string;
  description?: string;
}): Promise<TeamWithRole> {
  const { data } = await apiClient.post<TeamWithRole>("/teams/", payload);
  return data;
}

export async function updateTeam(
  id: number,
  payload: { name?: string; description?: string }
): Promise<Team> {
  const { data } = await apiClient.patch<Team>(`/teams/${id}`, payload);
  return data;
}

export async function deleteTeam(id: number): Promise<void> {
  await apiClient.delete(`/teams/${id}`);
}

export async function getTeamMembers(teamId: number): Promise<TeamMember[]> {
  const { data } = await apiClient.get<TeamMember[]>(`/teams/${teamId}/members`);
  return data;
}

export async function searchUsers(q: string): Promise<{ id: number; username: string }[]> {
  const { data } = await apiClient.get<{ id: number; username: string }[]>("/profiles/search", {
    params: { q },
  });
  return data;
}

export async function inviteMember(
  teamId: number,
  payload: { username: string; role: TeamRole }
): Promise<TeamInvitation> {
  const { data } = await apiClient.post<TeamInvitation>(`/teams/${teamId}/invite`, payload);
  return data;
}

export async function declineInvitation(token: string): Promise<void> {
  await apiClient.post(`/invitations/${token}/decline`);
}

export async function removeMember(teamId: number, userId: number): Promise<void> {
  await apiClient.delete(`/teams/${teamId}/members/${userId}`);
}

export async function changeMemberRole(
  teamId: number,
  userId: number,
  role: TeamRole
): Promise<TeamMember> {
  const { data } = await apiClient.patch<TeamMember>(`/teams/${teamId}/members/${userId}`, { role });
  return data;
}

export async function transferOwnership(teamId: number, newOwnerId: number): Promise<void> {
  await apiClient.post(`/teams/${teamId}/transfer`, { new_owner_id: newOwnerId });
}

export async function getInvitationDetail(token: string): Promise<InvitationDetail> {
  const { data } = await apiClient.get<InvitationDetail>(`/invitations/${token}`);
  return data;
}

export async function acceptInvitation(token: string): Promise<TeamMember> {
  const { data } = await apiClient.post<TeamMember>(`/invitations/${token}/accept`);
  return data;
}
