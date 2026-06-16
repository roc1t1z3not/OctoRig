// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { apiClient } from "./client";

export interface Badge {
  id: number;
  slug: string;
  name: string;
  description: string;
  icon: string;
  category: string | null;
  points_value: number;
  earned: boolean;
  earned_at: string | null;
}

export async function getBadges(): Promise<Badge[]> {
  const { data } = await apiClient.get<Badge[]>("/badges/");
  return data;
}

export async function getMyBadges(): Promise<Badge[]> {
  const { data } = await apiClient.get<Badge[]>("/badges/me");
  return data;
}

export async function getUserBadges(userId: number): Promise<Badge[]> {
  const { data } = await apiClient.get<Badge[]>(`/badges/users/${userId}`);
  return data;
}

export async function evaluateAchievements(): Promise<string[]> {
  const { data } = await apiClient.post<string[]>("/badges/evaluate");
  return data;
}
