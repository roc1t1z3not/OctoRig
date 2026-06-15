"use client";
import "./scoreboard.css";

import { useRef, useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Trophy, Crosshair, Snowflake } from "lucide-react";
import { getGlobalScoreboard } from "@/lib/api/challenges";
import { getEventScoreboard, getEvents } from "@/lib/api/events";
import { getRanks } from "@/lib/api/ranks";
import { useUserStore } from "@/stores/user.store";
import type { ScoreboardEntry } from "@/lib/api/challenges";
import type { Rank } from "@/lib/api/ranks";

const LIMITS = [25, 50, 100] as const;
type Limit = typeof LIMITS[number];

function rankForPoints(ranks: Rank[], points: number): Rank | null {
  const eligible = ranks.filter((r) => r.is_active && r.min_points <= points);
  if (eligible.length === 0) return null;
  return eligible.reduce((a, b) => (b.min_points > a.min_points ? b : a));
}

function RankChip({ rank }: { rank: Rank | null }) {
  if (!rank) return null;
  return (
    <span
      className="sb-rank-chip"
      style={{ color: rank.color ?? "var(--g-text-muted)", borderColor: rank.color ?? "var(--g-border)" }}
    >
      {rank.name}
    </span>
  );
}

function RankNum({ n }: { n: number }) {
  if (n === 1) return <span className="sb-rank-num sb-rank-num--gold"><span className="sb-medal">🥇</span>1</span>;
  if (n === 2) return <span className="sb-rank-num sb-rank-num--silver"><span className="sb-medal">🥈</span>2</span>;
  if (n === 3) return <span className="sb-rank-num sb-rank-num--bronze"><span className="sb-medal">🥉</span>3</span>;
  return <span className="sb-rank-num">{n}</span>;
}

function ScoreRow({
  entry,
  ranks,
  isMe,
  rowRef,
}: {
  entry: ScoreboardEntry;
  ranks: Rank[];
  isMe: boolean;
  rowRef?: React.Ref<HTMLTableRowElement>;
}) {
  const rank = rankForPoints(ranks, entry.total);
  return (
    <tr className={isMe ? "sb-row--me" : ""} ref={rowRef}>
      <td><RankNum n={entry.rank} /></td>
      <td>
        {entry.username ? (
          <Link href={`/profile/${entry.username}`} className="sb-username">
            {entry.username}
          </Link>
        ) : (
          <span className="sb-username" style={{ color: "var(--g-text-muted)" }}>Unknown</span>
        )}
      </td>
      <td><RankChip rank={rank} /></td>
      <td className="sb-pts">{entry.total.toLocaleString()}</td>
      <td className="sb-meta">{entry.solve_count}</td>
      <td className="sb-meta">{entry.badge_count}</td>
    </tr>
  );
}

export default function ScoreboardPage() {
  const { user } = useUserStore();
  const [limit, setLimit] = useState<Limit>(50);
  const [eventSlug, setEventSlug] = useState<string>("");
  const myRowRef = useRef<HTMLTableRowElement>(null);

  const { data: events = [] } = useQuery({
    queryKey: ["events"],
    queryFn: () => getEvents(),
  });

  const { data: ranks = [] } = useQuery({
    queryKey: ["ranks"],
    queryFn: getRanks,
    staleTime: 60_000,
  });

  const isGlobal = eventSlug === "";

  const { data: entries = [], isLoading } = useQuery({
    queryKey: ["scoreboard", isGlobal ? "global" : eventSlug, limit],
    queryFn: () =>
      isGlobal
        ? getGlobalScoreboard(limit)
        : getEventScoreboard(eventSlug, limit),
  });

  function scrollToMe() {
    myRowRef.current?.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  const myEntry = user ? entries.find((e) => e.username === user.username) : null;
  const isFrozen = isGlobal && entries.length > 0 && entries[0].frozen === true;

  return (
    <div className="page">
      <div className="sb-header">
        <div>
          <h1 className="page-title font-mono">
            <Trophy size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
            Scoreboard
          </h1>
          {!isLoading && (
            <p className="page-sub" style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
              {entries.length} players ranked
              {isFrozen && (
                <span style={{
                  display: "inline-flex", alignItems: "center", gap: "0.25rem",
                  fontSize: "0.6875rem", color: "var(--g-accent)",
                  background: "color-mix(in srgb, var(--g-accent) 12%, transparent)",
                  border: "1px solid color-mix(in srgb, var(--g-accent) 30%, transparent)",
                  borderRadius: "4px", padding: "0.1rem 0.4rem",
                }}>
                  <Snowflake size={10} />
                  Scoreboard frozen
                </span>
              )}
            </p>
          )}
        </div>

        <div className="sb-filters">
          <select
            className="sb-select"
            value={eventSlug}
            onChange={(e) => setEventSlug(e.target.value)}
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
            onChange={(e) => setLimit(Number(e.target.value) as Limit)}
          >
            {LIMITS.map((l) => (
              <option key={l} value={l}>Top {l}</option>
            ))}
          </select>

          {myEntry && (
            <button className="g-btn g-btn-ghost sb-highlight-btn" onClick={scrollToMe}>
              <Crosshair size={12} />
              My Rank #{myEntry.rank}
            </button>
          )}
        </div>
      </div>

      {isLoading ? (
        <div className="text-muted text-sm">Loading…</div>
      ) : entries.length === 0 ? (
        <div className="sb-empty">No scores yet.</div>
      ) : (
        <div className="sb-table-wrap g-card" style={{ padding: 0, overflow: "hidden" }}>
          <table className="sb-table">
            <thead>
              <tr>
                <th style={{ textAlign: "right" }}>#</th>
                <th>Player</th>
                <th>Rank</th>
                <th>Points</th>
                <th>Solves</th>
                <th>Badges</th>
              </tr>
            </thead>
            <tbody>
              {entries.map((entry) => {
                const isMe = !!user && entry.username === user.username;
                return (
                  <ScoreRow
                    key={entry.user_id ?? entry.team_id}
                    entry={entry}
                    ranks={ranks}
                    isMe={isMe}
                    rowRef={isMe ? myRowRef : undefined}
                  />
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
