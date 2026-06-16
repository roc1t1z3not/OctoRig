import { CheckCircle2 } from "lucide-react";
import type { Badge } from "@/lib/api/badges";
import { formatDate } from "@/lib/utils/date";
import { ICON_MAP } from "@/lib/utils/badge-icons";

export function BadgeCard({ badge }: { badge: Badge }) {
  return (
    <div className={`badge-card g-card ${badge.earned ? "badge-earned" : "badge-locked"}`}>
      <div className="badge-icon">{ICON_MAP[badge.icon] ?? "🏅"}</div>
      <div className="badge-info">
        <div className="badge-name">
          {badge.name}
          {badge.earned && <CheckCircle2 size={12} className="badge-check" />}
        </div>
        <p className="badge-desc">{badge.description}</p>
        <div className="badge-meta">
          {badge.points_value > 0 && (
            <span className="badge-pts">+{badge.points_value} pts</span>
          )}
          {badge.earned_at && (
            <span className="badge-date">Earned {formatDate(badge.earned_at)}</span>
          )}
        </div>
      </div>
    </div>
  );
}
