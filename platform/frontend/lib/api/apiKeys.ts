import { apiClient } from "./client";

export interface ApiKey {
  id: number;
  name: string;
  key_prefix: string;
  expires_at: string | null;
  last_used_at: string | null;
  is_active: boolean;
  created_at: string;
}

export interface ApiKeyCreated extends ApiKey {
  raw_key: string;
}

export async function getApiKeys(): Promise<ApiKey[]> {
  const { data } = await apiClient.get<ApiKey[]>("/api-keys/");
  return data;
}

export async function createApiKey(payload: {
  name: string;
  expires_at?: string | null;
}): Promise<ApiKeyCreated> {
  const { data } = await apiClient.post<ApiKeyCreated>("/api-keys/", payload);
  return data;
}

export async function revokeApiKey(id: number): Promise<void> {
  await apiClient.delete(`/api-keys/${id}`);
}
