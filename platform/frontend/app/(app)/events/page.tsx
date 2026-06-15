"use client";
import "./events.css";

import { useState } from "react";
import Link from "next/link";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Calendar, Clock, Trophy, Users, Lock, Globe, Eye, Plus, X } from "lucide-react";
import {
  getEvents,
  createEvent,
  type CtfEvent,
  type EventStatus,
  type CreateEventPayload,
} from "@/lib/api/events";
import { useUserStore } from "@/stores/user.store";
import { formatDateTime } from "@/lib/utils/date";
import { useNotificationsStore } from "@/stores/notifications.store";
import { EVENT_STATUS_COLORS } from "@/lib/utils/status";

const STATUS_TABS: { id: EventStatus | undefined; label: string }[] = [
  { id: undefined, label: "All" },
  { id: "published", label: "Upcoming" },
  { id: "running", label: "Live" },
  { id: "ended", label: "Past" },
];

const VIS_ICON: Record<string, React.ReactNode> = {
  public:   <Globe size={10} />,
  private:  <Lock size={10} />,
  unlisted: <Eye size={10} />,
};

function CountdownBadge({ end_at }: { end_at: string | null }) {
  if (!end_at) return null;
  const ms = new Date(end_at).getTime() - Date.now();
  if (ms <= 0) return <span className="ev-ended-label">Ended</span>;
  const h = Math.floor(ms / 3_600_000);
  const m = Math.floor((ms % 3_600_000) / 60_000);
  return (
    <span className="ev-countdown">
      <Clock size={10} />
      {h > 0 ? `${h}h ${m}m remaining` : `${m}m remaining`}
    </span>
  );
}

function EventCard({ ev }: { ev: CtfEvent }) {
  const isLive = ev.status === "running";
  return (
    <Link href={`/events/${ev.slug}`} className={`ev-card g-card ${isLive ? "ev-card--live" : ""}`}>
      <div className="ev-card-header">
        <span className="ev-vis">{VIS_ICON[ev.visibility]}</span>
        <span className="ev-status" style={{ color: EVENT_STATUS_COLORS[ev.status] }}>
          {isLive ? "● LIVE" : ev.status}
        </span>
        {isLive && <CountdownBadge end_at={ev.end_at} />}
      </div>
      <h3 className="ev-title">{ev.title}</h3>
      {ev.description && <p className="ev-desc">{ev.description}</p>}
      <div className="ev-meta">
        <span className="ev-meta-item">
          <Calendar size={11} />
          {formatDateTime(ev.start_at)}
        </span>
        {ev.max_team_size && (
          <span className="ev-meta-item">
            <Users size={11} />
            Max {ev.max_team_size}/team
          </span>
        )}
        <span className="ev-meta-item">
          <Trophy size={11} />
          {ev.scoring_mode}
        </span>
      </div>
    </Link>
  );
}

function CreateEventModal({ onClose }: { onClose: () => void }) {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();

  const [form, setForm] = useState<{
    title: string;
    slug: string;
    description: string;
    start_at: string;
    end_at: string;
    visibility: "public" | "private" | "unlisted";
    scoring_mode: "static" | "dynamic";
    max_team_size: string;
  }>({
    title: "",
    slug: "",
    description: "",
    start_at: "",
    end_at: "",
    visibility: "private",
    scoring_mode: "static",
    max_team_size: "",
  });

  const set = (k: string, v: string) => setForm((f) => ({ ...f, [k]: v }));

  // Auto-generate slug from title
  const handleTitle = (v: string) => {
    set("title", v);
    if (!form.slug || form.slug === slugify(form.title)) {
      set("slug", slugify(v));
    }
  };

  const mutation = useMutation({
    mutationFn: () => {
      const payload: CreateEventPayload = {
        slug: form.slug,
        title: form.title,
        description: form.description || undefined,
        start_at: form.start_at ? new Date(form.start_at).toISOString() : undefined,
        end_at: form.end_at ? new Date(form.end_at).toISOString() : undefined,
        visibility: form.visibility,
        scoring_mode: form.scoring_mode,
        max_team_size: form.max_team_size ? Number(form.max_team_size) : undefined,
      };
      return createEvent(payload);
    },
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["events"] });
      push("success", `Event "${form.title}" created as draft`);
      onClose();
    },
    onError: (err: unknown) => {
      const msg = (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ?? "Failed to create event";
      push("error", msg);
    },
  });

  const canSubmit = form.title.trim() && form.slug.trim();

  return (
    <div className="ev-create-overlay" onClick={(e) => { if (e.target === e.currentTarget) onClose(); }}>
      <div className="ev-create-modal">
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <h2>Create CTF Event</h2>
          <button className="g-btn g-btn-ghost g-btn-icon" onClick={onClose}>
            <X size={14} />
          </button>
        </div>

        <div className="ev-form-row">
          <label>Title *</label>
          <input className="g-input" value={form.title} onChange={(e) => handleTitle(e.target.value)} placeholder="Autumn CTF 2026" />
        </div>
        <div className="ev-form-row">
          <label>Slug *</label>
          <input className="g-input" value={form.slug} onChange={(e) => set("slug", e.target.value)} placeholder="autumn-ctf-2026" />
        </div>
        <div className="ev-form-row">
          <label>Description</label>
          <textarea className="g-input" rows={2} value={form.description} onChange={(e) => set("description", e.target.value)} placeholder="Optional description…" style={{ resize: "vertical" }} />
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
          <div className="ev-form-row">
            <label>Start</label>
            <input type="datetime-local" className="g-input" value={form.start_at} onChange={(e) => set("start_at", e.target.value)} />
          </div>
          <div className="ev-form-row">
            <label>End</label>
            <input type="datetime-local" className="g-input" value={form.end_at} onChange={(e) => set("end_at", e.target.value)} />
          </div>
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0.75rem" }}>
          <div className="ev-form-row">
            <label>Visibility</label>
            <select className="g-input" value={form.visibility} onChange={(e) => set("visibility", e.target.value)}>
              <option value="private">Private</option>
              <option value="unlisted">Unlisted</option>
              <option value="public">Public</option>
            </select>
          </div>
          <div className="ev-form-row">
            <label>Scoring</label>
            <select className="g-input" value={form.scoring_mode} onChange={(e) => set("scoring_mode", e.target.value)}>
              <option value="static">Static</option>
              <option value="dynamic">Dynamic</option>
            </select>
          </div>
          <div className="ev-form-row">
            <label>Max team size</label>
            <input type="number" min={1} className="g-input" value={form.max_team_size} onChange={(e) => set("max_team_size", e.target.value)} placeholder="Any" />
          </div>
        </div>

        <div className="ev-form-actions">
          <button className="g-btn g-btn-ghost" onClick={onClose}>Cancel</button>
          <button
            className="g-btn g-btn-primary"
            disabled={!canSubmit || mutation.isPending}
            onClick={() => mutation.mutate()}
          >
            {mutation.isPending ? "Creating…" : "Create Event"}
          </button>
        </div>
      </div>
    </div>
  );
}

function slugify(s: string): string {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "");
}

export default function EventsPage() {
  const [statusFilter, setStatusFilter] = useState<EventStatus | undefined>(undefined);
  const [showCreate, setShowCreate] = useState(false);
  const { user } = useUserStore();
  const isAdmin = user?.is_admin || user?.is_superuser;

  const { data: events = [], isLoading } = useQuery({
    queryKey: ["events", statusFilter],
    queryFn: () => getEvents(statusFilter),
  });

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">CTF Events</h1>
        {isAdmin && (
          <button
            className="g-btn g-btn-primary"
            style={{ marginLeft: "auto" }}
            onClick={() => setShowCreate(true)}
          >
            <Plus size={13} />
            New Event
          </button>
        )}
      </div>

      <div className="filter-bar">
        {STATUS_TABS.map((t) => (
          <button
            key={String(t.id)}
            className={`g-btn ${statusFilter === t.id ? "g-btn-primary" : "g-btn-ghost"}`}
            onClick={() => setStatusFilter(t.id)}
          >
            {t.label}
          </button>
        ))}
      </div>

      {isLoading ? (
        <div className="text-muted text-sm" style={{ marginTop: "1.5rem" }}>Loading events…</div>
      ) : events.length === 0 ? (
        <div className="text-muted text-sm" style={{ marginTop: "1.5rem" }}>
          No events found.{isAdmin && " Click “New Event” to create one."}
        </div>
      ) : (
        <div className="ev-grid" style={{ marginTop: "1rem" }}>
          {events.map((ev) => (
            <EventCard key={ev.id} ev={ev} />
          ))}
        </div>
      )}

      {showCreate && <CreateEventModal onClose={() => setShowCreate(false)} />}
    </div>
  );
}
