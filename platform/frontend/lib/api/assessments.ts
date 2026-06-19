// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { apiClient } from "./client";

export type InviteStatus = "pending" | "accepted" | "active" | "completed" | "expired" | "revoked";

export interface Assessment {
  id: number;
  name: string;
  slug: string;
  company_name: string | null;
  company_logo_url: string | null;
  description: string | null;
  candidate_instructions: string | null;
  duration_hours: number;
  lab_slugs: string[];
  lab_display_names: Record<string, string>;
  is_active: boolean;
  created_by_id: number;
  created_at: string;
  invite_count: number;
  active_invite_count: number;
}

export interface AssessmentInvite {
  id: number;
  assessment_id: number;
  email: string;
  candidate_name: string | null;
  token: string;
  user_id: number | null;
  accepted_at: string | null;
  started_at: string | null;
  expires_at: string | null;
  completed_at: string | null;
  deployment_ids: number[];
  is_revoked: boolean;
  status: InviteStatus;
}

export interface FlagSolve {
  challenge_slug: string;
  challenge_title: string;
  points: number;
  solved_at: string;
}

export interface AssessmentInviteWithProgress extends AssessmentInvite {
  flags_solved: FlagSolve[];
  score: number;
  report_submitted: boolean;
}

export interface CandidateLabInfo {
  display_name: string;
  slug: string;
  deployment_id: number | null;
  status: string | null;
  access_info: Array<{ key: string; value: string }>;
}

export interface CandidateAssessmentStatus {
  assessment_name: string;
  company_name: string | null;
  company_logo_url: string | null;
  candidate_instructions: string | null;
  started_at: string | null;
  expires_at: string | null;
  completed_at: string | null;
  time_remaining_seconds: number | null;
  labs: CandidateLabInfo[];
  report_submitted: boolean;
  report_content: string | null;
}

export interface InviteLandingResponse {
  assessment_name: string;
  company_name: string | null;
  company_logo_url: string | null;
  candidate_instructions: string | null;
  lab_count: number;
  duration_hours: number;
  candidate_name: string | null;
  status: InviteStatus;
}

// ---------------------------------------------------------------------------
// Admin — Assessment CRUD
// ---------------------------------------------------------------------------

export interface CreateAssessmentPayload {
  name: string;
  slug?: string;
  company_name?: string;
  company_logo_url?: string;
  description?: string;
  candidate_instructions?: string;
  duration_hours?: number;
  lab_slugs: string[];
  lab_display_names?: Record<string, string>;
}

export async function listAssessments(): Promise<Assessment[]> {
  const { data } = await apiClient.get<Assessment[]>("/admin/assessments/");
  return data;
}

export async function getAssessment(id: number): Promise<Assessment> {
  const { data } = await apiClient.get<Assessment>(`/admin/assessments/${id}`);
  return data;
}

export async function createAssessment(payload: CreateAssessmentPayload): Promise<Assessment> {
  const { data } = await apiClient.post<Assessment>("/admin/assessments/", payload);
  return data;
}

export async function updateAssessment(
  id: number,
  payload: Partial<CreateAssessmentPayload> & { is_active?: boolean }
): Promise<Assessment> {
  const { data } = await apiClient.patch<Assessment>(`/admin/assessments/${id}`, payload);
  return data;
}

export async function deleteAssessment(id: number): Promise<void> {
  await apiClient.delete(`/admin/assessments/${id}`);
}

// ---------------------------------------------------------------------------
// Admin — Invite management
// ---------------------------------------------------------------------------

export interface CreateInvitePayload {
  email: string;
  candidate_name?: string;
}

export async function listInvites(assessmentId: number): Promise<AssessmentInvite[]> {
  const { data } = await apiClient.get<AssessmentInvite[]>(
    `/admin/assessments/${assessmentId}/invites`
  );
  return data;
}

export async function createInvite(
  assessmentId: number,
  payload: CreateInvitePayload
): Promise<AssessmentInvite> {
  const { data } = await apiClient.post<AssessmentInvite>(
    `/admin/assessments/${assessmentId}/invites`,
    payload
  );
  return data;
}

export async function revokeInvite(assessmentId: number, inviteId: number): Promise<void> {
  await apiClient.delete(`/admin/assessments/${assessmentId}/invites/${inviteId}`);
}

export async function listCandidateProgress(
  assessmentId: number
): Promise<AssessmentInviteWithProgress[]> {
  const { data } = await apiClient.get<AssessmentInviteWithProgress[]>(
    `/admin/assessments/${assessmentId}/progress`
  );
  return data;
}

export async function getCandidateProgress(
  assessmentId: number,
  inviteId: number
): Promise<AssessmentInviteWithProgress> {
  const { data } = await apiClient.get<AssessmentInviteWithProgress>(
    `/admin/assessments/${assessmentId}/invites/${inviteId}/progress`
  );
  return data;
}

// ---------------------------------------------------------------------------
// Candidate
// ---------------------------------------------------------------------------

export async function getInviteLanding(token: string): Promise<InviteLandingResponse> {
  const { data } = await apiClient.get<InviteLandingResponse>(
    `/assessments/invite/${token}`
  );
  return data;
}

export interface AcceptInvitePayload {
  username: string;
  password: string;
}

export async function acceptInvite(
  token: string,
  payload: AcceptInvitePayload
): Promise<{ access_token: string; expires_in: number }> {
  const { data } = await apiClient.post<{ access_token: string; expires_in: number }>(
    `/assessments/invite/${token}/accept`,
    payload
  );
  return data;
}

export async function startAssessment(): Promise<CandidateAssessmentStatus> {
  const { data } = await apiClient.post<CandidateAssessmentStatus>("/assessments/me/start");
  return data;
}

export async function getAssessmentStatus(): Promise<CandidateAssessmentStatus> {
  const { data } = await apiClient.get<CandidateAssessmentStatus>("/assessments/me");
  return data;
}

export async function submitReport(content: string): Promise<void> {
  await apiClient.post("/assessments/me/report", { content });
}

export async function completeAssessment(): Promise<CandidateAssessmentStatus> {
  const { data } = await apiClient.post<CandidateAssessmentStatus>("/assessments/me/complete");
  return data;
}
