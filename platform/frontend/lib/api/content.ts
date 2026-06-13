import { apiClient } from "./client";

export type ContentType = "challenge" | "lab";
export type ContentStatus =
  | "draft" | "pending_review" | "in_review" | "approved" | "published" | "rejected";
export type ReviewVerdict = "approved" | "rejected" | "needs_changes";

export interface ContentSubmission {
  id: number;
  author_id: number;
  content_type: ContentType;
  title: string;
  body: Record<string, unknown>;
  status: ContentStatus;
  reviewer_id: number | null;
  created_at: string;
  updated_at: string;
}

export async function getMySubmissions(status?: ContentStatus): Promise<ContentSubmission[]> {
  const { data } = await apiClient.get<ContentSubmission[]>("/content/mine", {
    params: status ? { status } : undefined,
  });
  return data;
}

export async function createSubmission(payload: {
  content_type: ContentType;
  title: string;
  body: Record<string, unknown>;
}): Promise<ContentSubmission> {
  const { data } = await apiClient.post<ContentSubmission>("/content/", payload);
  return data;
}

export async function updateSubmission(
  id: number,
  payload: { title?: string; body?: Record<string, unknown> }
): Promise<ContentSubmission> {
  const { data } = await apiClient.patch<ContentSubmission>(`/content/${id}`, payload);
  return data;
}

export async function submitForReview(id: number): Promise<ContentSubmission> {
  const { data } = await apiClient.post<ContentSubmission>(`/content/${id}/submit`);
  return data;
}

export async function getPendingQueue(): Promise<ContentSubmission[]> {
  const { data } = await apiClient.get<ContentSubmission[]>("/content/queue/pending");
  return data;
}

export async function getApprovedQueue(): Promise<ContentSubmission[]> {
  const { data } = await apiClient.get<ContentSubmission[]>("/content/queue/approved");
  return data;
}

export async function claimSubmission(id: number): Promise<ContentSubmission> {
  const { data } = await apiClient.post<ContentSubmission>(`/content/${id}/claim`);
  return data;
}

export async function reviewSubmission(
  id: number,
  verdict: ReviewVerdict,
  comment?: string
): Promise<{ review_id: number; verdict: ReviewVerdict; submission_status: ContentStatus }> {
  const { data } = await apiClient.post(`/content/${id}/review`, { verdict, comment });
  return data;
}

export async function publishSubmission(id: number): Promise<ContentSubmission> {
  const { data } = await apiClient.post<ContentSubmission>(`/content/${id}/publish`);
  return data;
}
