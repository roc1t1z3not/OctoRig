import { create } from "zustand";

export interface LiveDeployment {
  id: number;
  lab_template_id: number | null;
  lab_name: string | null;
  status: string;
  error_message?: string | null;
}

export interface LiveHealth {
  running_labs: number;
  total_containers: number;
  docker: string;
}

interface LiveState {
  connected: boolean;
  health: LiveHealth | null;
  deployments: Record<number, LiveDeployment>;
  setConnected: (v: boolean) => void;
  setHealth: (h: LiveHealth) => void;
  upsertDeployment: (d: LiveDeployment) => void;
}

export const useLiveStore = create<LiveState>((set) => ({
  connected: false,
  health: null,
  deployments: {},
  setConnected: (connected) => set({ connected }),
  setHealth: (health) => set({ health }),
  upsertDeployment: (d) =>
    set((s) => ({ deployments: { ...s.deployments, [d.id]: d } })),
}));
