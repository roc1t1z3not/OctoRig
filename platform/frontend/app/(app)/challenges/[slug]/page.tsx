"use client";
import "../challenges.css";

import { useState, useEffect } from "react";
import { useParams } from "next/navigation";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import {
  ArrowLeft, CheckCircle2, XCircle, Eye, EyeOff,
  Clock, Target, Zap, Lightbulb, Flag, Container, Trash2, Copy, FlaskConical, ExternalLink,
} from "lucide-react";
import Link from "next/link";
import {
  getChallenge, submitFlag, unlockHint,
  type ChallengeDifficulty, type HintSummary,
} from "@/lib/api/challenges";
import { getMyProfile } from "@/lib/api/profiles";
import { deployInstance, getMyInstance, stopDeployment, type Deployment } from "@/lib/api/deployments";
import { getLabs } from "@/lib/api/labs";
import { useNotificationsStore } from "@/stores/notifications.store";

const DIFF_COLOR: Record<ChallengeDifficulty, string> = {
  easy:   "var(--g-success)",
  medium: "var(--g-warning)",
  hard:   "var(--g-orange)",
  insane: "var(--g-danger)",
};

function useCountdown(target: string | null): string {
  const [label, setLabel] = useState("");
  useEffect(() => {
    if (!target) return;
    function tick() {
      const diff = Math.max(0, new Date(target!).getTime() - Date.now());
      const h = Math.floor(diff / 3_600_000);
      const m = Math.floor((diff % 3_600_000) / 60_000);
      const s = Math.floor((diff % 60_000) / 1_000);
      setLabel(diff === 0 ? "Expired" : `${h}h ${m.toString().padStart(2, "0")}m ${s.toString().padStart(2, "0")}s`);
    }
    tick();
    const id = setInterval(tick, 1_000);
    return () => clearInterval(id);
  }, [target]);
  return label;
}

function InstanceCard({
  instance,
  onStop,
  isStopping,
}: {
  instance: Deployment;
  onStop: () => void;
  isStopping: boolean;
}) {
  const countdown = useCountdown(instance.auto_destroy_at);
  const [copied, setCopied] = useState(false);

  function copyFlag() {
    if (!instance.dynamic_flag) return;
    navigator.clipboard.writeText(instance.dynamic_flag).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    });
  }

  const isActive = instance.status === "running" || instance.status === "starting";

  return (
    <div
      className="g-card"
      style={{ borderColor: isActive ? "var(--g-accent)" : "var(--g-border)" }}
    >
      <div className="flex items-center justify-between gap-2 mb-3">
        <div className="flex items-center gap-2">
          <Container size={14} style={{ color: "var(--g-accent)" }} />
          <span className="text-11 font-mono" style={{ color: "var(--g-text)" }}>
            Instance #{instance.id}
          </span>
          <span
            className="text-9px font-mono uppercase px-1.5 py-0.5 rounded"
            style={{
              background: isActive ? "color-mix(in srgb, var(--g-accent) 15%, transparent)" : "var(--g-surface)",
              color: isActive ? "var(--g-accent)" : "var(--g-text-muted)",
            }}
          >
            {instance.status}
          </span>
        </div>
        <button
          className="g-btn g-btn-danger g-btn-icon"
          onClick={onStop}
          disabled={isStopping || instance.status === "stopping"}
          title="Destroy instance"
        >
          <Trash2 size={12} />
        </button>
      </div>

      {instance.auto_destroy_at && (
        <div className="flex items-center gap-1.5 mb-2 text-9px font-mono" style={{ color: "var(--g-warning)" }}>
          <Clock size={10} />
          Auto-destroys in {countdown}
        </div>
      )}

      {instance.dynamic_flag && (
        <div className="mt-2">
          <div className="text-9px font-mono uppercase mb-1" style={{ color: "var(--g-text-muted)" }}>
            Dynamic Flag
          </div>
          <div className="flex items-center gap-2">
            <code
              className="flex-1 text-11 font-mono px-2 py-1 rounded truncate"
              style={{ background: "var(--g-surface)", color: "var(--g-success)", border: "1px solid var(--g-border)" }}
            >
              {instance.dynamic_flag}
            </code>
            <button
              className="g-btn g-btn-ghost g-btn-icon"
              onClick={copyFlag}
              title="Copy flag"
              style={{ flexShrink: 0 }}
            >
              <Copy size={12} style={{ color: copied ? "var(--g-success)" : undefined }} />
            </button>
          </div>
        </div>
      )}
    </div>
  );
}

function HintCard({
  hint,
  slug,
  userPoints,
  onUnlocked,
}: {
  hint: HintSummary;
  slug: string;
  userPoints: number;
  onUnlocked: (hintId: number, content: string) => void;
}) {
  const [visible, setVisible] = useState(false);
  const { push } = useNotificationsStore();
  const canAfford = hint.cost === 0 || userPoints >= hint.cost;

  const unlockMutation = useMutation({
    mutationFn: () => unlockHint(slug, hint.id),
    onSuccess: (res) => {
      onUnlocked(res.hint_id, res.content);
      setVisible(true);
      if (res.cost > 0) push("info", `-${res.cost} pts spent to unlock hint`);
    },
    onError: (err: unknown) => {
      const detail = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail;
      push("error", detail ?? "Failed to unlock hint");
    },
  });

  if (!hint.unlocked && hint.content === null) {
    return (
      <div className="hint-card hint-locked">
        <div className="hint-header">
          <Lightbulb size={13} className="hint-icon" />
          <span className="hint-label">Hint {hint.order_num}</span>
          {hint.cost > 0 && (
            <span className="hint-cost" style={{ color: canAfford ? undefined : "var(--g-danger)" }}>
              {hint.cost} pts
            </span>
          )}
        </div>
        <button
          className="g-btn g-btn-ghost hint-unlock-btn"
          onClick={() => unlockMutation.mutate()}
          disabled={unlockMutation.isPending || !canAfford}
          title={!canAfford ? `Not enough points (need ${hint.cost}, have ${userPoints})` : undefined}
        >
          {unlockMutation.isPending
            ? "Unlocking…"
            : !canAfford
            ? `Not enough pts`
            : `Unlock${hint.cost > 0 ? ` (−${hint.cost} pts)` : ""}`}
        </button>
      </div>
    );
  }

  const content = hint.content!;
  return (
    <div className="hint-card hint-unlocked">
      <div className="hint-header">
        <Lightbulb size={13} className="hint-icon hint-icon--unlocked" />
        <span className="hint-label">Hint {hint.order_num}</span>
        {hint.cost > 0 && <span className="hint-cost hint-cost--paid">−{hint.cost} pts</span>}
        <button
          className="hint-toggle"
          onClick={() => setVisible((v) => !v)}
          aria-label={visible ? "Hide hint" : "Show hint"}
        >
          {visible ? <EyeOff size={12} /> : <Eye size={12} />}
        </button>
      </div>
      {visible && <p className="hint-content">{content}</p>}
    </div>
  );
}

export default function ChallengeDetailPage() {
  const { slug } = useParams<{ slug: string }>();
  const qc = useQueryClient();
  const { push } = useNotificationsStore();

  const [flag, setFlag] = useState("");
  const [submitResult, setSubmitResult] = useState<{
    correct: boolean;
    message: string;
    firstBlood: boolean;
    points: number;
  } | null>(null);
  const [localHints, setLocalHints] = useState<Record<number, string>>({});

  const { data: profile } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: getMyProfile,
    staleTime: 30_000,
  });
  const userPoints = profile?.total_points ?? 0;

  const { data: ch, isLoading } = useQuery({
    queryKey: ["challenge", slug],
    queryFn: () => getChallenge(slug),
  });

  const { data: labs = [] } = useQuery({
    queryKey: ["labs"],
    queryFn: () => getLabs(),
    staleTime: 30_000,
    enabled: !!ch?.lab_slug,
  });

  const labTemplate = ch?.lab_slug
    ? labs.find((l) => l.slug === ch.lab_slug) ?? null
    : null;

  const labIsLive =
    labTemplate?.current_deployment?.status === "running" ||
    labTemplate?.current_deployment?.status === "starting";

  const labUrl =
    labTemplate?.access_info.find((a) => a.key === "URL")?.value ?? null;

  const { data: instance = null } = useQuery({
    queryKey: ["challenge-instance", ch?.id],
    queryFn: () => getMyInstance(ch!.id),
    enabled: ch?.challenge_type === "container",
    refetchInterval: (q) => {
      const s = q.state.data?.status;
      return s === "starting" || s === "stopping" ? 3_000 : 15_000;
    },
  });

  const deployMutation = useMutation({
    mutationFn: () => deployInstance(ch!.id, 2),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["challenge-instance", ch?.id] });
      push("success", "Instance starting…");
    },
    onError: (err: unknown) => {
      const detail = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail;
      push("error", detail ?? "Failed to deploy instance");
    },
  });

  const stopMutation = useMutation({
    mutationFn: () => stopDeployment(instance!.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["challenge-instance", ch?.id] });
      push("info", "Instance destroyed");
    },
    onError: () => push("error", "Failed to stop instance"),
  });

  const submitMutation = useMutation({
    mutationFn: (f: string) => submitFlag(slug, f),
    onSuccess: (res) => {
      setSubmitResult({
        correct: res.correct || res.already_solved,
        message: res.message,
        firstBlood: res.first_blood,
        points: res.points_awarded,
      });
      if (res.correct || res.already_solved) {
        qc.invalidateQueries({ queryKey: ["challenge", slug] });
        qc.invalidateQueries({ queryKey: ["challenges"] });
        if (res.first_blood) push("success", `First Blood! +${res.points_awarded} pts`);
        else if (!res.already_solved) push("success", `Correct! +${res.points_awarded} pts`);
        setFlag("");
      } else {
        push("error", "Incorrect flag");
      }
    },
    onError: (err: unknown) => {
      const detail = (err as { response?: { data?: { detail?: string } } })
        ?.response?.data?.detail;
      push("error", detail ?? "Submission failed");
    },
  });

  function handleHintUnlocked(hintId: number, content: string) {
    setLocalHints((prev) => ({ ...prev, [hintId]: content }));
    qc.invalidateQueries({ queryKey: ["challenge", slug] });
  }

  function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!flag.trim()) return;
    setSubmitResult(null);
    submitMutation.mutate(flag.trim());
  }

  if (isLoading) {
    return <div className="page text-muted text-sm">Loading challenge…</div>;
  }
  if (!ch) {
    return <div className="page text-muted text-sm">Challenge not found.</div>;
  }

  const diffColor = DIFF_COLOR[ch.difficulty];
  const solvedByMe = ch.solved_by_me;

  const hints: HintSummary[] = ch.hints.map((h) => ({
    ...h,
    content: localHints[h.id] ?? h.content,
    unlocked: h.unlocked || localHints[h.id] !== undefined,
  }));

  return (
    <div className="page">
      {/* Back navigation */}
      <Link href="/challenges" className="back-link">
        <ArrowLeft size={14} />
        <span>Challenges</span>
      </Link>

      {/* Header */}
      <div className="ch-header">
        <div className="ch-meta-row">
          {ch.lab_name && (
            <span className="ch-lab-status-group">
              <Link href="/labs" className="ch-lab-badge">
                <FlaskConical size={10} />
                {ch.lab_name}
              </Link>
              {labTemplate && (
                <span
                  className={`ch-lab-status-dot ${labIsLive ? "ch-lab-status-dot--live" : "ch-lab-status-dot--off"}`}
                  title={labIsLive ? "Lab is running" : "Lab is offline"}
                />
              )}
              {labIsLive && labUrl && (
                <a
                  href={labUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="ch-lab-open-link"
                  title={`Open ${ch.lab_name}`}
                >
                  <ExternalLink size={10} />
                  Open Lab
                </a>
              )}
            </span>
          )}
          <span className="ch-cat">{ch.category.replace(/-/g, " ")}</span>
          <span className="ch-diff" style={{ color: diffColor }}>{ch.difficulty}</span>
          {solvedByMe && (
            <span className="ch-solved">
              <CheckCircle2 size={12} />
              Solved
            </span>
          )}
        </div>
        <h1 className="ch-title">{ch.title}</h1>
        <div className="ch-stats">
          <span className="ch-stat">
            <Flag size={12} />
            {ch.points} pts
          </span>
          {ch.estimated_minutes && (
            <span className="ch-stat">
              <Clock size={12} />
              ~{ch.estimated_minutes}m
            </span>
          )}
          <span className="ch-stat">
            <Target size={12} />
            {ch.solve_count} solve{ch.solve_count !== 1 ? "s" : ""}
          </span>
        </div>
      </div>

      <div className="ch-body">
        {/* Description */}
        <section className="g-card ch-desc-card">
          <p className="ch-desc">{ch.description}</p>

          {ch.tags.length > 0 && (
            <div className="ch-tags">
              {ch.tags.map((t) => (
                <span key={t} className="ch-tag">{t}</span>
              ))}
            </div>
          )}
        </section>

        {/* Hints */}
        {hints.length > 0 && (
          <section>
            <h2 className="section-title">Hints</h2>
            <div className="hints-list">
              {hints.map((h) => (
                <HintCard
                  key={h.id}
                  hint={h}
                  slug={slug}
                  userPoints={userPoints}
                  onUnlocked={handleHintUnlocked}
                />
              ))}
            </div>
          </section>
        )}

        {/* Container instance */}
        {ch.challenge_type === "container" && (
          <section>
            <h2 className="section-title">Lab Instance</h2>
            {instance && (instance.status === "running" || instance.status === "starting" || instance.status === "stopping") ? (
              <InstanceCard
                instance={instance}
                onStop={() => stopMutation.mutate()}
                isStopping={stopMutation.isPending}
              />
            ) : (
              <div className="g-card" style={{ borderStyle: "dashed" }}>
                <p className="text-11 text-muted mb-3">
                  This challenge requires a personal lab instance. Instances auto-destroy after 2 hours.
                </p>
                <button
                  className="g-btn g-btn-primary"
                  onClick={() => deployMutation.mutate()}
                  disabled={deployMutation.isPending}
                >
                  <Container size={13} />
                  {deployMutation.isPending ? "Deploying…" : "Deploy Instance"}
                </button>
              </div>
            )}
          </section>
        )}

        {/* Flag submission */}
        <section className="g-card submit-card">
          <h2 className="section-title">Submit Flag</h2>

          {solvedByMe ? (
            <div className="submit-solved">
              <CheckCircle2 size={16} />
              You&apos;ve already solved this challenge.
            </div>
          ) : (
            <form onSubmit={handleSubmit} className="submit-form">
              <div className="submit-row">
                <input
                  className="g-input submit-input font-mono"
                  placeholder="FLAG{...}"
                  value={flag}
                  onChange={(e) => setFlag(e.target.value)}
                  disabled={submitMutation.isPending}
                  spellCheck={false}
                  autoComplete="off"
                />
                <button
                  type="submit"
                  className="g-btn g-btn-primary"
                  disabled={submitMutation.isPending || !flag.trim()}
                >
                  {submitMutation.isPending ? "Checking…" : "Submit"}
                </button>
              </div>

              {submitResult && (
                <div className={`submit-feedback ${submitResult.correct ? "fb-correct" : "fb-wrong"}`}>
                  {submitResult.correct ? <CheckCircle2 size={14} /> : <XCircle size={14} />}
                  <span>{submitResult.message}</span>
                  {submitResult.firstBlood && (
                    <span className="fb-firstblood">
                      <Zap size={12} /> First Blood
                    </span>
                  )}
                </div>
              )}
            </form>
          )}
        </section>
      </div>
    </div>
  );
}
