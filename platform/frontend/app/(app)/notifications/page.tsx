"use client";
import "./notifications.css";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { Bell, CheckCheck } from "lucide-react";
import {
  getNotifications, markAllRead, markRead,
  type AppNotification,
} from "@/lib/api/notifications";
import { useNotificationsStore } from "@/stores/notifications.store";

function NotificationRow({ n, onRead }: { n: AppNotification; onRead: (id: number) => void }) {
  const isUnread = !n.read_at;
  const timeAgo = (() => {
    const ms = Date.now() - new Date(n.created_at).getTime();
    const m = Math.floor(ms / 60_000);
    if (m < 1) return "just now";
    if (m < 60) return `${m}m ago`;
    const h = Math.floor(m / 60);
    if (h < 24) return `${h}h ago`;
    return `${Math.floor(h / 24)}d ago`;
  })();

  return (
    <div
      className={`notif-row ${isUnread ? "notif-row--unread" : ""}`}
      onClick={() => isUnread && onRead(n.id)}
    >
      {isUnread && <span className="notif-dot" />}
      <div className="notif-content">
        <div className="notif-title">{n.title}</div>
        {n.body && <p className="notif-body">{n.body}</p>}
      </div>
      <span className="notif-time">{timeAgo}</span>
    </div>
  );
}

export default function NotificationsPage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();

  const { data: notifications = [], isLoading } = useQuery({
    queryKey: ["notifications"],
    queryFn: () => getNotifications(false, 100),
  });

  const readMutation = useMutation({
    mutationFn: markRead,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: ["notifications-unread"] });
    },
  });

  const readAllMutation = useMutation({
    mutationFn: markAllRead,
    onSuccess: (count) => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
      qc.invalidateQueries({ queryKey: ["notifications-unread"] });
      push("success", `Marked ${count} notification${count !== 1 ? "s" : ""} as read`);
    },
    onError: () => push("error", "Failed to mark all as read"),
  });

  const unread = notifications.filter((n) => !n.read_at).length;

  return (
    <div className="page">
      <div className="page-header">
        <div>
          <h1 className="page-title font-mono">
            <Bell size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
            Notifications
          </h1>
          {!isLoading && unread > 0 && (
            <p className="page-sub">{unread} unread</p>
          )}
        </div>
        {unread > 0 && (
          <button
            className="g-btn g-btn-ghost"
            onClick={() => readAllMutation.mutate()}
            disabled={readAllMutation.isPending}
          >
            <CheckCheck size={13} />
            Mark all read
          </button>
        )}
      </div>

      {isLoading ? (
        <div className="text-muted text-sm">Loading…</div>
      ) : notifications.length === 0 ? (
        <div className="empty-state g-card">
          <Bell size={24} style={{ color: "var(--g-text-muted)" }} />
          <p className="text-muted text-sm">No notifications yet.</p>
        </div>
      ) : (
        <div className="notif-list g-panel">
          {notifications.map((n) => (
            <NotificationRow
              key={n.id}
              n={n}
              onRead={(id) => readMutation.mutate(id)}
            />
          ))}
        </div>
      )}
    </div>
  );
}
