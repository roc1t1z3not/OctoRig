"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Printer } from "lucide-react";
import {
  publishSubmission,
  type ContentSubmission,
} from "@/lib/api/content";
import { useNotificationsStore } from "@/stores/notifications.store";
import { BodyPreview } from "./BodyPreview";
import { StatusBadge } from "./StatusBadge";

export function ApprovedRow({ sub }: { sub: ContentSubmission }) {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const [showBody, setShowBody] = useState(false);

  const { mutate: publish, isPending } = useMutation({
    mutationFn: () => publishSubmission(sub.id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["content", "queue", "approved"] });
      push("success", "Submission published.");
    },
    onError: (err: any) => push("error", err?.response?.data?.detail ?? "Failed to publish."),
  });

  return (
    <>
      <tr>
        <td>
          <button
            className="g-btn g-btn-ghost g-btn-sm"
            style={{ padding: "0.1rem 0.4rem", fontSize: "0.7rem" }}
            onClick={() => setShowBody((v) => !v)}
            title="Toggle body"
          >
            {showBody ? "▾" : "▸"}
          </button>
          {" "}
          <span style={{ color: "var(--g-text)" }}>{sub.title}</span>
        </td>
        <td><span className="role-pill role-pill--on">{sub.content_type}</span></td>
        <td style={{ color: "var(--g-text-muted)", fontSize: "0.75rem" }}>
          {sub.author_username ?? `#${sub.author_id}`}
        </td>
        <td><StatusBadge status={sub.status} /></td>
        <td>
          <button className="g-btn g-btn-primary g-btn-sm" disabled={isPending} onClick={() => publish()}>
            <Printer size={12} />
            {isPending ? "Publishing…" : "Publish"}
          </button>
        </td>
      </tr>
      {showBody && (
        <tr>
          <td colSpan={5} style={{ padding: "0 0.75rem 0.75rem" }}>
            <BodyPreview body={sub.body} contentType={sub.content_type} />
          </td>
        </tr>
      )}
    </>
  );
}
