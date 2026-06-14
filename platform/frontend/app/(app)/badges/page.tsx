"use client";
import "./badges.css";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Award, CheckCircle2, RefreshCw } from "lucide-react";
import { getBadges, evaluateAchievements, type Badge } from "@/lib/api/badges";
import { useNotificationsStore } from "@/stores/notifications.store";

const ICON_MAP: Record<string, string> = {
  flag:      "🚩",
  hash:      "#",
  zap:       "⚡",
  droplets:  "🩸",
  database:  "🗄️",
  code:      "</>",
  lock:      "🔒",
  star:      "⭐",
  crown:     "👑",
  shield:    "🛡️",
  target:    "🎯",
  trophy:    "🏆",
  skull:     "💀",
  eye:       "👁️",
  globe:     "🌐",
  flame:     "🔥",
};

function BadgeCard({ badge }: { badge: Badge }) {
  return (
    <div className={`badge-card g-card ${badge.earned ? "badge-earned" : "badge-locked"}`}>
      <div className="badge-icon">{ICON_MAP[badge.icon] ?? "🏅"}</div>
      <div className="badge-info">
        <div className="badge-name">
          {badge.name}
          {badge.earned && <CheckCircle2 size={12} className="badge-check" />}
        </div>
        <p className="badge-desc">{badge.description}</p>
        {badge.points_value > 0 && (
          <span className="badge-pts">+{badge.points_value} pts</span>
        )}
        {badge.earned_at && (
          <span className="badge-date">
            Earned {new Date(badge.earned_at).toLocaleDateString()}
          </span>
        )}
      </div>
    </div>
  );
}

export default function BadgesPage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();

  const { data: badges = [], isLoading } = useQuery({
    queryKey: ["badges"],
    queryFn: getBadges,
  });

  const evalMutation = useMutation({
    mutationFn: evaluateAchievements,
    onSuccess: (newBadges) => {
      qc.invalidateQueries({ queryKey: ["badges"] });
      if (newBadges.length > 0) {
        push("success", `Unlocked: ${newBadges.join(", ")}`);
      } else {
        push("info", "No new badges earned yet.");
      }
    },
    onError: () => push("error", "Failed to evaluate achievements"),
  });

  const earned = badges.filter((b) => b.earned).length;
  const total = badges.length;

  const byCategory = badges.reduce<Record<string, Badge[]>>((acc, b) => {
    const cat = b.category ?? "other";
    (acc[cat] ??= []).push(b);
    return acc;
  }, {});

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title font-mono">
            <Award size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
            Badges
          </h1>
          {!isLoading && (
            <p className="page-sub">{earned}/{total} earned</p>
          )}
        </div>
        <button
          className="g-btn g-btn-ghost"
          onClick={() => evalMutation.mutate()}
          disabled={evalMutation.isPending}
        >
          <RefreshCw size={13} />
          {evalMutation.isPending ? "Checking…" : "Check Achievements"}
        </button>
      </div>

      {isLoading ? (
        <div className="text-muted text-sm">Loading badges…</div>
      ) : (
        <div className="categories">
          {Object.entries(byCategory).map(([cat, catBadges]) => (
            <section key={cat}>
              <h2 className="cat-title">{cat}</h2>
              <div className="badge-grid">
                {catBadges.map((b) => (
                  <BadgeCard key={b.id} badge={b} />
                ))}
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
