import type { ChallengeDifficulty } from "@/lib/api/challenges";

export const DIFF_COLOR: Record<ChallengeDifficulty, string> = {
  easy:   "var(--g-success)",
  medium: "var(--g-warning)",
  hard:   "var(--g-orange)",
  insane: "var(--g-danger)",
};
