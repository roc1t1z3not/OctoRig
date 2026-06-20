"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import { useEffect, useState } from "react";
import { Save, X } from "lucide-react";
import { type AdminTeam } from "@/lib/api/admin";
import { useEscapeKey } from "@/hooks/useEscapeKey";

interface TeamEditSheetProps {
  open: boolean;
  team: AdminTeam | null;
  saveMutation: { mutate: (data: { name: string }) => void; isPending: boolean };
  onClose: () => void;
}

export function TeamEditSheet({ open, team, saveMutation, onClose }: TeamEditSheetProps) {
  const [name, setName] = useState("");

  useEffect(() => {
    if (open) setName(team?.name ?? "");
  }, [open, team]);

  useEscapeKey(onClose, open);

  if (!open || !team) return null;

  return (
    <>
      <div className="g-backdrop" onClick={onClose} />
      <div className="ev-sheet">
        <div className="ev-sheet-header">
          <h2 style={{ margin: 0, fontSize: "1rem", fontWeight: 700 }}>Edit Team — {team.slug}</h2>
          <button className="g-btn g-btn-ghost g-btn-sm" onClick={onClose}>
            <X size={14} />
          </button>
        </div>

        <div className="ev-sheet-body">
          <label className="ev-field">
            <span className="ev-label">Name</span>
            <input
              className="g-input"
              value={name}
              onChange={(e) => setName(e.target.value)}
              autoFocus
            />
          </label>
        </div>

        <div className="ev-sheet-footer">
          <button className="g-btn g-btn-ghost" onClick={onClose}>Cancel</button>
          <button
            className="g-btn g-btn-primary"
            disabled={!name || saveMutation.isPending}
            onClick={() => saveMutation.mutate({ name })}
          >
            <Save size={13} />
            {saveMutation.isPending ? "Saving…" : "Save Changes"}
          </button>
        </div>
      </div>
    </>
  );
}
