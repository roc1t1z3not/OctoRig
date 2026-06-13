import { apiClient } from "./client";

export interface SystemHealth {
  docker: "ok" | "error";
  database: "ok" | "error";
  running_labs: number;
  total_containers: number;
}

export interface ContainerInfo {
  name: string;
  status: string;
  image: string;
  created: string;
}

export async function getHealth(): Promise<SystemHealth> {
  const { data } = await apiClient.get<SystemHealth>("/system/health");
  return data;
}

export async function getContainers(): Promise<ContainerInfo[]> {
  const { data } = await apiClient.get<ContainerInfo[]>("/system/containers");
  return data;
}

export interface PluginInfo {
  name: string;
  version: string;
  plugin_type: string;
  entry_point: string;
}

export async function getPlugins(): Promise<PluginInfo[]> {
  const { data } = await apiClient.get<PluginInfo[]>("/system/plugins");
  return data;
}
