"use client";
import "./badges.css";

import { useState } from "react";
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

const CATEGORIES = ["all", "milestone", "competition", "skill"] as const;
type CategoryFilter = typeof CATEGORIES[number];
type StatusFilter = "all" | "earned" | "locked";

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
        <div className="badge-meta">
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
    </div>
  );
}

export default function BadgesPage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const [catFilter, setCatFilter] = useState<CategoryFilter>("all");
  const [statusFilter, setStatusFilter] = useState<StatusFilter>("all");

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

  const filtered = badges.filter((b) => {
    if (catFilter !== "all" && b.category !== catFilter) return false;
    if (statusFilter === "earned" && !b.earned) return false;
    if (statusFilter === "locked" && b.earned) return false;
    return true;
  });

  const byCategory = filtered.reduce<Record<string, Badge[]>>((acc, b) => {
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

      <div className="filter-bar">
        <div className="filter-group">
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              className={`filter-pill ${catFilter === cat ? "active" : ""}`}
              onClick={() => setCatFilter(cat)}
            >
              {cat === "all" ? "All" : cat.charAt(0).toUpperCase() + cat.slice(1)}
            </button>
          ))}
        </div>
        <div className="filter-group">
          {(["all", "earned", "locked"] as StatusFilter[]).map((s) => (
            <button
              key={s}
              className={`filter-pill ${statusFilter === s ? "active" : ""}`}
              onClick={() => setStatusFilter(s)}
            >
              {s.charAt(0).toUpperCase() + s.slice(1)}
            </button>
          ))}
        </div>
      </div>

      {isLoading ? (
        <div className="text-muted text-sm">Loading badges…</div>
      ) : filtered.length === 0 ? (
        <div className="text-muted text-sm">No badges match this filter.</div>
      ) : catFilter !== "all" ? (
        <div className="badge-grid">
          {filtered.map((b) => <BadgeCard key={b.id} badge={b} />)}
        </div>
      ) : (
        <div className="categories">
          {Object.entries(byCategory).map(([cat, catBadges]) => (
            <section key={cat}>
              <h2 className="cat-title">{cat}</h2>
              <div className="badge-grid">
                {catBadges.map((b) => <BadgeCard key={b.id} badge={b} />)}
              </div>
            </section>
          ))}
        </div>
      )}
    </div>
  );
}
