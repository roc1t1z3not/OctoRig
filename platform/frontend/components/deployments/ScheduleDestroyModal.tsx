"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { addHours } from "@/lib/utils/date";

const PRESETS: { label: string; hours: number }[] = [
  { label: "2 h", hours: 2 },
  { label: "24 h", hours: 24 },
  { label: "7 d", hours: 168 },
];

interface ScheduleDestroyModalProps {
  labName: string;
  scheduledAt: string;
  onChangeScheduledAt: (value: string) => void;
  onConfirm: () => void;
  onClose: () => void;
  isPending: boolean;
}

export function ScheduleDestroyModal({
  labName,
  scheduledAt,
  onChangeScheduledAt,
  onConfirm,
  onClose,
  isPending,
}: ScheduleDestroyModalProps) {
  return (
    <div className="g-backdrop" onClick={onClose}>
      <div className="g-modal" onClick={(e) => e.stopPropagation()}>
        <div className="g-modal-header">
          <span className="font-mono text-sm">Schedule Destroy — {labName}</span>
        </div>
        <div className="g-modal-body">
          <p className="text-muted text-11" style={{ marginBottom: "0.75rem" }}>
            The lab will be automatically stopped at the specified time.
          </p>
          <div className="dd-preset-row">
            {PRESETS.map((p) => (
              <button
                key={p.label}
                className="g-btn g-btn-ghost g-btn-sm"
                onClick={() => onChangeScheduledAt(addHours(p.hours))}
              >
                {p.label}
              </button>
            ))}
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: "0.25rem" }}>
            <label className="text-11 text-muted">Custom time</label>
            <input
              type="datetime-local"
              className="g-input"
              value={scheduledAt}
              min={addHours(0)}
              onChange={(e) => onChangeScheduledAt(e.target.value)}
            />
          </div>
        </div>
        <div className="g-modal-footer">
          <button className="g-btn g-btn-ghost" onClick={onClose}>
            Cancel
          </button>
          <button
            className="g-btn g-btn-danger"
            onClick={onConfirm}
            disabled={isPending}
          >
            {isPending ? "Scheduling…" : "Schedule Destroy"}
          </button>
        </div>
      </div>
    </div>
  );
}
