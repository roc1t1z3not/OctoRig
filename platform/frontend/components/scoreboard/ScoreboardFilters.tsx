import { Crosshair } from "lucide-react";
import type { ScoreboardEntry } from "@/lib/api/challenges";

export const SCOREBOARD_LIMITS = [25, 50, 100] as const;

export function ScoreboardFilters({
  events,
  eventSlug,
  limit,
  myEntry,
  onEventChange,
  onLimitChange,
  onScrollToMe,
}: {
  events: { slug: string; title: string; status: string }[];
  eventSlug: string;
  limit: number;
  myEntry: ScoreboardEntry | null | undefined;
  onEventChange: (slug: string) => void;
  onLimitChange: (limit: number) => void;
  onScrollToMe: () => void;
}) {
  return (
    <div className="sb-filters">
      <select
        className="sb-select"
        value={eventSlug}
        onChange={(e) => onEventChange(e.target.value)}
      >
        <option value="">Global</option>
        {events
          .filter((ev) => ev.status !== "draft")
          .map((ev) => (
            <option key={ev.slug} value={ev.slug}>{ev.title}</option>
          ))}
      </select>

      <select
        className="sb-select"
        value={limit}
        onChange={(e) => onLimitChange(Number(e.target.value))}
      >
        {SCOREBOARD_LIMITS.map((l) => (
          <option key={l} value={l}>Top {l}</option>
        ))}
      </select>

      {myEntry && (
        <button className="g-btn g-btn-ghost sb-highlight-btn" onClick={onScrollToMe}>
          <Crosshair size={12} />
          My Rank #{myEntry.rank}
        </button>
      )}
    </div>
  );
}
