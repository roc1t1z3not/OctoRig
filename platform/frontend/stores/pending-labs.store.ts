// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { create } from "zustand";

export interface PendingLab {
  deploymentId: number;
  labName: string;
  toastId: string;
}

interface PendingLabsState {
  pending: PendingLab[];
  add: (lab: PendingLab) => void;
  remove: (deploymentId: number) => void;
}

export const usePendingLabsStore = create<PendingLabsState>((set) => ({
  pending: [],
  add: (lab) => set((s) => ({ pending: [...s.pending, lab] })),
  remove: (deploymentId) =>
    set((s) => ({ pending: s.pending.filter((l) => l.deploymentId !== deploymentId) })),
}));
