import { apiClient } from "./client";

export type ScheduledActionType = "deploy" | "destroy";
export type ScheduledActionStatus =
  | "pending"
  | "executing"
  | "completed"
  | "failed"
  | "cancelled";

export interface ScheduledAction {
  id: number;
  user_id: number;
  team_id: number | null;
  lab_template_id: number | null;
  deployment_id: number | null;
  action: ScheduledActionType;
  scheduled_at: string;
  executed_at: string | null;
  status: ScheduledActionStatus;
  error_message: string | null;
  created_at: string;
}

export async function getScheduledActions(
  status?: ScheduledActionStatus
): Promise<ScheduledAction[]> {
  const params = status ? { status } : {};
  const { data } = await apiClient.get<ScheduledAction[]>("/schedule/", { params });
  return data;
}

export async function createScheduledAction(payload: {
  action: ScheduledActionType;
  scheduled_at: string;
  deployment_id?: number;
  lab_template_id?: number;
  team_id?: number;
}): Promise<ScheduledAction> {
  const { data } = await apiClient.post<ScheduledAction>("/schedule/", payload);
  return data;
}

export async function cancelScheduledAction(id: number): Promise<void> {
  await apiClient.delete(`/schedule/${id}`);
}
