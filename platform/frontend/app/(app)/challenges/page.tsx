"use client";
import "./challenges.css";

import { useState } from "react";
import Link from "next/link";
import { useQuery } from "@tanstack/react-query";
import { Search, CheckCircle2, Clock, Target } from "lucide-react";
import { getChallenges, type ChallengeListItem, type ChallengeDifficulty } from "@/lib/api/challenges";
import { getLabs, type LabTemplate } from "@/lib/api/labs";

const CATEGORIES = [
  { id: undefined, label: "All" },
  { id: "sqli", label: "SQLi" },
  { id: "xss", label: "XSS" },
  { id: "idor", label: "IDOR" },
  { id: "web", label: "Web" },
  { id: "recon", label: "Recon" },
] as const;

const DIFFICULTIES: { id: ChallengeDifficulty | undefined; label: string }[] = [
  { id: undefined, label: "Any" },
  { id: "easy", label: "Easy" },
  { id: "medium", label: "Medium" },
  { id: "hard", label: "Hard" },
  { id: "insane", label: "Insane" },
];

const LAB_CATEGORIES: { id: string | undefined; label: string }[] = [
  { id: undefined, label: "All Labs" },
  { id: "world", label: "World" },
  { id: "firerange", label: "Fire Range" },
  { id: "thirdparty", label: "3rd Party" },
];

const DIFF_COLOR: Record<ChallengeDifficulty, string> = {
  easy:   "diff-easy",
  medium: "diff-medium",
  hard:   "diff-hard",
  insane: "diff-insane",
};

function DiffBadge({ difficulty }: { difficulty: ChallengeDifficulty }) {
  return (
    <span className={`diff-badge ${DIFF_COLOR[difficulty]}`}>
      {difficulty}
    </span>
  );
}

function ChallengeCard({ ch }: { ch: ChallengeListItem }) {
  return (
    <Link href={`/challenges/${ch.slug}`} className="ch-card g-card">
      <div className="ch-card-header">
        <span className="ch-category">{ch.category.replace("-", " ")}</span>
        <DiffBadge difficulty={ch.difficulty} />
      </div>

      <h3 className="ch-title">{ch.title}</h3>

      {ch.lab_name && (
        <span className="ch-lab-tag">{ch.lab_name}</span>
      )}

      <div className="ch-tags">
        {ch.tags.slice(0, 3).map((t) => (
          <span key={t} className="ch-tag">{t}</span>
        ))}
      </div>

      <div className="ch-footer">
        <span className="ch-points">{ch.points} pts</span>
        <div className="ch-meta">
          {ch.estimated_minutes && (
            <span className="ch-meta-item">
              <Clock size={11} />
              {ch.estimated_minutes}m
            </span>
          )}
          <span className="ch-meta-item">
            <Target size={11} />
            {ch.solve_count} solves
          </span>
          {ch.solved_by_me && (
            <span className="ch-solved-badge">
              <CheckCircle2 size={11} />
              Solved
            </span>
          )}
        </div>
      </div>
    </Link>
  );
}

export default function ChallengesPage() {
  const [category, setCategory] = useState<string | undefined>(undefined);
  const [difficulty, setDifficulty] = useState<ChallengeDifficulty | undefined>(undefined);
  const [labCategory, setLabCategory] = useState<string | undefined>(undefined);
  const [labSlug, setLabSlug] = useState<string | undefined>(undefined);
  const [search, setSearch] = useState("");

  const { data: challenges = [], isLoading } = useQuery({
    queryKey: ["challenges", category, difficulty, search, labCategory, labSlug],
    queryFn: () => getChallenges({
      category,
      difficulty,
      search: search || undefined,
      lab_category: labCategory,
      lab_slug: labSlug || undefined,
    }),
  });

  const { data: labs = [] } = useQuery<LabTemplate[]>({
    queryKey: ["labs"],
    queryFn: () => getLabs(),
    staleTime: 60_000,
  });

  // Filter to only labs that actually have challenges
  const labsWithChallenges = labCategory
    ? labs.filter((l) => l.category === labCategory)
    : labs;

  const solved = challenges.filter((c) => c.solved_by_me).length;
  const total = challenges.length;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title font-mono">Challenges</h1>
          {!isLoading && (
            <p className="page-sub">{solved}/{total} solved</p>
          )}
        </div>
      </div>

      <div className="filter-bar">
        <div className="g-input-icon">
          <Search size={14} className="icon-left" />
          <input
            className="g-input"
            placeholder="Search challenges…"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
          />
        </div>

        <div className="flex gap-1">
          {CATEGORIES.map((c) => (
            <button
              key={String(c.id)}
              className={`g-btn ${category === c.id ? "g-btn-primary" : "g-btn-ghost"}`}
              onClick={() => setCategory(c.id)}
            >
              {c.label}
            </button>
          ))}
        </div>

        <div className="flex gap-1">
          {DIFFICULTIES.map((d) => (
            <button
              key={String(d.id)}
              className={`g-btn ${difficulty === d.id ? "g-btn-primary" : "g-btn-ghost"}`}
              onClick={() => setDifficulty(d.id)}
            >
              {d.label}
            </button>
          ))}
        </div>
      </div>

      {/* Lab filters */}
      <div className="ch-lab-filters">
        <div className="flex gap-1">
          {LAB_CATEGORIES.map((lc) => (
            <button
              key={String(lc.id)}
              className={`g-btn g-btn-sm ${labCategory === lc.id ? "g-btn-primary" : "g-btn-ghost"}`}
              onClick={() => { setLabCategory(lc.id); setLabSlug(undefined); }}
            >
              {lc.label}
            </button>
          ))}
        </div>

        {labsWithChallenges.length > 0 && (
          <div className="flex gap-1 flex-wrap">
            <button
              className={`g-btn g-btn-sm ${!labSlug ? "g-btn-subtle" : "g-btn-ghost"}`}
              onClick={() => setLabSlug(undefined)}
            >
              All
            </button>
            {labsWithChallenges.map((lab) => (
              <button
                key={lab.slug}
                className={`g-btn g-btn-sm ${labSlug === lab.slug ? "g-btn-subtle" : "g-btn-ghost"}`}
                onClick={() => setLabSlug(lab.slug === labSlug ? undefined : lab.slug)}
              >
                {lab.name}
              </button>
            ))}
          </div>
        )}
      </div>

      {isLoading ? (
        <div className="text-muted text-sm mt-4">Loading challenges…</div>
      ) : (
        <>
          <div className="ch-grid mt-4">
            {challenges.map((ch) => (
              <ChallengeCard key={ch.id} ch={ch} />
            ))}
          </div>
          {challenges.length === 0 && (
            <div className="text-muted text-sm mt-4">No challenges match your filter.</div>
          )}
        </>
      )}
    </div>
  );
}
