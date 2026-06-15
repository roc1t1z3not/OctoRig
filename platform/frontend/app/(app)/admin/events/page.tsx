"use client";
import "../admin.css";

import { useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import {
  Plus, ChevronRight, X, Save, Calendar, Lock, Globe, Link2,
} from "lucide-react";
import {
  getEvents, createEvent, updateEvent, transitionEvent,
  addEventChallenge, removeEventChallenge,
  type CtfEvent, type EventStatus, type EventVisibility, type EventScoringMode,
  type CreateEventPayload, type UpdateEventPayload,
} from "@/lib/api/events";
import { getChallenges } from "@/lib/api/challenges";
import { useNotificationsStore } from "@/stores/notifications.store";
import { useConfirmStore } from "@/stores/confirm.store";
import { useUserStore } from "@/stores/user.store";
import { useAdminGuard } from "@/hooks/useAdminGuard";
import { formatDateTime } from "@/lib/utils/date";
import { EVENT_STATUS_COLORS } from "@/lib/utils/status";

const STATUS_ORDER: EventStatus[] = ["draft", "published", "running", "ended", "archived"];

function nextStatus(s: EventStatus): EventStatus | null {
  const i = STATUS_ORDER.indexOf(s);
  return i < STATUS_ORDER.length - 1 ? STATUS_ORDER[i + 1] : null;
}

function toLocalInput(val: string | null | undefined): string {
  if (!val) return "";
  try { return new Date(val).toISOString().slice(0, 16); } catch { return ""; }
}
function toISOOrNull(val: string): string | null {
  if (!val) return null;
  try { return new Date(val).toISOString(); } catch { return null; }
}

interface SheetState {
  open: boolean;
  editing: CtfEvent | null;
}

const BLANK_FORM = {
  slug: "", title: "", description: "",
  start_at: "", end_at: "", freeze_scoreboard_at: "",
  visibility: "private" as EventVisibility,
  scoring_mode: "static" as EventScoringMode,
  max_team_size: "",
};

function slugify(s: string) {
  return s.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "");
}

export default function AdminEventsPage() {
  const { push } = useNotificationsStore();
  const { confirm } = useConfirmStore();
  const { user } = useUserStore();
  const qc = useQueryClient();

  useAdminGuard();

  const { data: events = [], isLoading } = useQuery({
    queryKey: ["admin-events"],
    queryFn: () => getEvents(),
    enabled: !!(user?.is_admin || user?.is_superuser),
  });

  const [sheet, setSheet] = useState<SheetState>({ open: false, editing: null });
  const [form, setForm] = useState(BLANK_FORM);

  // Challenge mapping panel
  const [mapSlug, setMapSlug] = useState<string | null>(null);
  const [challSearch, setChallSearch] = useState("");

  const mapEvent = mapSlug ? events.find((e) => e.slug === mapSlug) : null;

  const { data: eventChallenges = [] } = useQuery({
    queryKey: ["event-challenges", mapSlug],
    queryFn: () => import("@/lib/api/events").then((m) => m.getEventChallenges(mapSlug!)),
    enabled: !!mapSlug,
  });

  const { data: allChallenges = [] } = useQuery({
    queryKey: ["challenges-all"],
    queryFn: () => getChallenges(),
    staleTime: 60_000,
  });

  function openCreate() {
    setForm(BLANK_FORM);
    setSheet({ open: true, editing: null });
  }

  function openEdit(ev: CtfEvent) {
    setForm({
      slug: ev.slug,
      title: ev.title,
      description: ev.description ?? "",
      start_at: toLocalInput(ev.start_at),
      end_at: toLocalInput(ev.end_at),
      freeze_scoreboard_at: toLocalInput(ev.freeze_scoreboard_at),
      visibility: ev.visibility,
      scoring_mode: ev.scoring_mode,
      max_team_size: ev.max_team_size?.toString() ?? "",
    });
    setSheet({ open: true, editing: ev });
  }

  const saveMutation = useMutation({
    mutationFn: async () => {
      const payload = {
        title: form.title,
        description: form.description || null,
        start_at: toISOOrNull(form.start_at),
        end_at: toISOOrNull(form.end_at),
        freeze_scoreboard_at: toISOOrNull(form.freeze_scoreboard_at),
        visibility: form.visibility,
        scoring_mode: form.scoring_mode,
        max_team_size: form.max_team_size ? parseInt(form.max_team_size) : null,
      };
      if (sheet.editing) {
        return updateEvent(sheet.editing.slug, payload as UpdateEventPayload);
      } else {
        return createEvent({ slug: form.slug, ...payload } as CreateEventPayload);
      }
    },
    onSuccess: () => {
      push("success", sheet.editing ? "Event updated" : "Event created");
      setSheet({ open: false, editing: null });
      qc.invalidateQueries({ queryKey: ["admin-events"] });
    },
    onError: () => push("error", "Failed to save event"),
  });

  const transitionMutation = useMutation({
    mutationFn: ({ slug, status }: { slug: string; status: EventStatus }) =>
      transitionEvent(slug, status),
    onSuccess: () => {
      push("success", "Status updated");
      qc.invalidateQueries({ queryKey: ["admin-events"] });
    },
    onError: () => push("error", "Failed to update status"),
  });

  const addChallMutation = useMutation({
    mutationFn: (challengeId: number) => addEventChallenge(mapSlug!, challengeId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["event-challenges", mapSlug] }),
    onError: () => push("error", "Failed to add challenge"),
  });

  const removeChallMutation = useMutation({
    mutationFn: (challengeId: number) => removeEventChallenge(mapSlug!, challengeId),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["event-challenges", mapSlug] }),
    onError: () => push("error", "Failed to remove challenge"),
  });

  const mappedIds = new Set(eventChallenges.map((c) => c.id));
  const filteredAll = allChallenges.filter((c) =>
    !mappedIds.has(c.id) &&
    (challSearch === "" || c.title.toLowerCase().includes(challSearch.toLowerCase()))
  );

  const visIcon = (v: EventVisibility) =>
    v === "public" ? <Globe size={11} /> : v === "private" ? <Lock size={11} /> : <Link2 size={11} />;

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">Events</h1>
        <button className="g-btn g-btn-primary g-btn-sm" onClick={openCreate}>
          <Plus size={13} />
          New Event
        </button>
      </div>

      {isLoading ? (
        <p style={{ color: "var(--g-text-muted)", fontSize: "0.875rem" }}>Loading…</p>
      ) : events.length === 0 ? (
        <div className="g-card" style={{ textAlign: "center", padding: "2rem", color: "var(--g-text-muted)" }}>
          No events yet. Create one to get started.
        </div>
      ) : (
        <div className="g-card" style={{ padding: 0, overflow: "hidden" }}>
          <table className="g-table">
            <thead>
              <tr>
                <th>Event</th>
                <th>Status</th>
                <th>Visibility</th>
                <th>Scoring</th>
                <th>Start / End</th>
                <th>Challenges</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {events.map((ev) => {
                const next = nextStatus(ev.status);
                return (
                  <tr key={ev.id}>
                    <td>
                      <div style={{ fontWeight: 600, fontSize: "0.8125rem" }}>{ev.title}</div>
                      <div style={{ fontSize: "0.6875rem", color: "var(--g-text-muted)", fontFamily: "monospace" }}>{ev.slug}</div>
                    </td>
                    <td>
                      <span style={{
                        fontSize: "0.6875rem", fontWeight: 700, fontFamily: "monospace",
                        textTransform: "uppercase", color: EVENT_STATUS_COLORS[ev.status],
                      }}>
                        {ev.status}
                      </span>
                    </td>
                    <td>
                      <span style={{ display: "flex", alignItems: "center", gap: 4, fontSize: "0.75rem", color: "var(--g-text-muted)" }}>
                        {visIcon(ev.visibility)}
                        {ev.visibility}
                      </span>
                    </td>
                    <td style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>{ev.scoring_mode}</td>
                    <td style={{ fontSize: "0.6875rem", color: "var(--g-text-muted)" }}>
                      {formatDateTime(ev.start_at)}
                      {" / "}
                      {formatDateTime(ev.end_at)}
                    </td>
                    <td>
                      <button
                        className="g-btn g-btn-ghost g-btn-sm"
                        onClick={() => setMapSlug(ev.slug === mapSlug ? null : ev.slug)}
                      >
                        Challenges
                        <ChevronRight size={12} style={{ transform: mapSlug === ev.slug ? "rotate(90deg)" : "none", transition: "transform 0.15s" }} />
                      </button>
                    </td>
                    <td>
                      <div style={{ display: "flex", gap: 6 }}>
                        {next && (
                          <button
                            className="g-btn g-btn-ghost g-btn-sm"
                            disabled={transitionMutation.isPending}
                            onClick={() => confirm({
                              title: `Set status to "${next}"?`,
                              body: `This will move "${ev.title}" from ${ev.status} to ${next}.`,
                              confirmLabel: "Confirm",
                              onConfirm: () => transitionMutation.mutate({ slug: ev.slug, status: next }),
                            })}
                          >
                            → {next}
                          </button>
                        )}
                        <button className="g-btn g-btn-ghost g-btn-sm" onClick={() => openEdit(ev)}>
                          Edit
                        </button>
                      </div>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* ── Challenge mapping panel ─────────────────────────────────────────── */}
      {mapSlug && mapEvent && (
        <div className="g-card" style={{ marginTop: "1rem" }}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
            <h3 style={{ margin: 0, fontSize: "0.875rem", fontWeight: 600 }}>
              Challenges in <em>{mapEvent.title}</em>
            </h3>
            <button className="g-btn g-btn-ghost g-btn-sm" onClick={() => setMapSlug(null)}>
              <X size={12} /> Close
            </button>
          </div>

          {eventChallenges.length === 0 ? (
            <p style={{ color: "var(--g-text-muted)", fontSize: "0.8125rem" }}>No challenges mapped yet.</p>
          ) : (
            <table className="g-table" style={{ marginBottom: "1rem" }}>
              <thead><tr><th>Challenge</th><th>Category</th><th>Points</th><th></th></tr></thead>
              <tbody>
                {eventChallenges.map((c) => (
                  <tr key={c.id}>
                    <td style={{ fontSize: "0.8125rem" }}>{c.title}</td>
                    <td style={{ fontSize: "0.75rem", color: "var(--g-text-muted)" }}>{c.category}</td>
                    <td style={{ fontSize: "0.75rem" }}>{c.points}</td>
                    <td>
                      <button
                        className="g-btn g-btn-danger g-btn-sm"
                        disabled={removeChallMutation.isPending}
                        onClick={() => removeChallMutation.mutate(c.id)}
                      >
                        Remove
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}

          <div style={{ borderTop: "1px solid var(--g-border)", paddingTop: "1rem" }}>
            <p style={{ fontSize: "0.75rem", color: "var(--g-text-muted)", marginBottom: "0.5rem" }}>Add challenge:</p>
            <input
              className="g-input"
              placeholder="Search challenges…"
              value={challSearch}
              onChange={(e) => setChallSearch(e.target.value)}
              style={{ marginBottom: "0.5rem", width: 280 }}
            />
            <div style={{ maxHeight: 200, overflowY: "auto", display: "flex", flexDirection: "column", gap: 4 }}>
              {filteredAll.slice(0, 20).map((c) => (
                <div key={c.id} style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.25rem 0" }}>
                  <span style={{ fontSize: "0.8125rem" }}>{c.title} <span style={{ color: "var(--g-text-muted)", fontSize: "0.6875rem" }}>({c.category})</span></span>
                  <button
                    className="g-btn g-btn-ghost g-btn-sm"
                    disabled={addChallMutation.isPending}
                    onClick={() => addChallMutation.mutate(c.id)}
                  >
                    + Add
                  </button>
                </div>
              ))}
              {filteredAll.length === 0 && <p style={{ color: "var(--g-text-muted)", fontSize: "0.75rem" }}>All challenges added.</p>}
            </div>
          </div>
        </div>
      )}

      {/* ── Create/Edit Sheet ───────────────────────────────────────────────── */}
      {sheet.open && (
        <>
          <div
            className="g-backdrop"
            onClick={() => setSheet({ open: false, editing: null })}
          />
          <div className="ev-sheet">
            <div className="ev-sheet-header">
              <h2 style={{ margin: 0, fontSize: "1rem", fontWeight: 700 }}>
                {sheet.editing ? "Edit Event" : "New Event"}
              </h2>
              <button className="g-btn g-btn-ghost g-btn-sm" onClick={() => setSheet({ open: false, editing: null })}>
                <X size={14} />
              </button>
            </div>

            <div className="ev-sheet-body">
              <label className="ev-field">
                <span className="ev-label">Title</span>
                <input
                  className="g-input"
                  value={form.title}
                  onChange={(e) => setForm((f) => ({
                    ...f,
                    title: e.target.value,
                    slug: sheet.editing ? f.slug : slugify(e.target.value),
                  }))}
                />
              </label>

              {!sheet.editing && (
                <label className="ev-field">
                  <span className="ev-label">Slug</span>
                  <input
                    className="g-input"
                    value={form.slug}
                    onChange={(e) => setForm((f) => ({ ...f, slug: slugify(e.target.value) }))}
                  />
                </label>
              )}

              <label className="ev-field">
                <span className="ev-label">Description</span>
                <textarea
                  className="g-input"
                  rows={3}
                  style={{ resize: "vertical" }}
                  value={form.description}
                  onChange={(e) => setForm((f) => ({ ...f, description: e.target.value }))}
                />
              </label>

              <div className="ev-field-row">
                <label className="ev-field">
                  <span className="ev-label"><Calendar size={11} style={{ display: "inline", marginRight: 4 }} />Start</span>
                  <input
                    type="datetime-local"
                    className="g-input"
                    value={form.start_at}
                    onChange={(e) => setForm((f) => ({ ...f, start_at: e.target.value }))}
                  />
                </label>
                <label className="ev-field">
                  <span className="ev-label"><Calendar size={11} style={{ display: "inline", marginRight: 4 }} />End</span>
                  <input
                    type="datetime-local"
                    className="g-input"
                    value={form.end_at}
                    onChange={(e) => setForm((f) => ({ ...f, end_at: e.target.value }))}
                  />
                </label>
              </div>

              <label className="ev-field">
                <span className="ev-label">Freeze Scoreboard At</span>
                <input
                  type="datetime-local"
                  className="g-input"
                  value={form.freeze_scoreboard_at}
                  onChange={(e) => setForm((f) => ({ ...f, freeze_scoreboard_at: e.target.value }))}
                />
              </label>

              <div className="ev-field-row">
                <label className="ev-field">
                  <span className="ev-label">Visibility</span>
                  <select
                    className="g-input"
                    value={form.visibility}
                    onChange={(e) => setForm((f) => ({ ...f, visibility: e.target.value as EventVisibility }))}
                  >
                    <option value="private">Private</option>
                    <option value="unlisted">Unlisted</option>
                    <option value="public">Public</option>
                  </select>
                </label>
                <label className="ev-field">
                  <span className="ev-label">Scoring Mode</span>
                  <select
                    className="g-input"
                    value={form.scoring_mode}
                    onChange={(e) => setForm((f) => ({ ...f, scoring_mode: e.target.value as EventScoringMode }))}
                  >
                    <option value="static">Static</option>
                    <option value="dynamic">Dynamic</option>
                  </select>
                </label>
              </div>

              <label className="ev-field">
                <span className="ev-label">Max Team Size</span>
                <input
                  type="number"
                  className="g-input"
                  min={1}
                  placeholder="Unlimited"
                  value={form.max_team_size}
                  onChange={(e) => setForm((f) => ({ ...f, max_team_size: e.target.value }))}
                />
              </label>
            </div>

            <div className="ev-sheet-footer">
              <button className="g-btn g-btn-ghost" onClick={() => setSheet({ open: false, editing: null })}>
                Cancel
              </button>
              <button
                className="g-btn g-btn-primary"
                disabled={!form.title || (!sheet.editing && !form.slug) || saveMutation.isPending}
                onClick={() => saveMutation.mutate()}
              >
                <Save size={13} />
                {saveMutation.isPending ? "Saving…" : sheet.editing ? "Save Changes" : "Create Event"}
              </button>
            </div>
          </div>
        </>
      )}

      <style>{`
        .ev-sheet {
          position: fixed; top: 0; right: 0; bottom: 0; width: 440px;
          background: var(--g-chrome); border-left: 1px solid var(--g-border);
          display: flex; flex-direction: column; z-index: 200;
        }
        .ev-sheet-header {
          display: flex; justify-content: space-between; align-items: center;
          padding: 1rem 1.25rem;
          border-bottom: 1px solid var(--g-border);
        }
        .ev-sheet-body { flex: 1; overflow-y: auto; padding: 1.25rem; display: flex; flex-direction: column; gap: 1rem; }
        .ev-sheet-footer {
          display: flex; justify-content: flex-end; gap: 0.5rem;
          padding: 1rem 1.25rem; border-top: 1px solid var(--g-border);
        }
        .ev-field { display: flex; flex-direction: column; gap: 0.25rem; flex: 1; }
        .ev-field-row { display: flex; gap: 0.75rem; }
        .ev-label { font-size: 0.75rem; font-weight: 600; color: var(--g-text-muted); }
      `}</style>
    </div>
  );
}
