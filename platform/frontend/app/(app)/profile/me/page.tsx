"use client";
import "../profile.css";

import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { User } from "lucide-react";
import { getMyProfile, updateMyProfile, type ProfileUpdatePayload } from "@/lib/api/profiles";
import { useNotificationsStore } from "@/stores/notifications.store";

export default function MyProfilePage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();

  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: getMyProfile,
  });

  const [form, setForm] = useState<ProfileUpdatePayload>({});

  useEffect(() => {
    if (!profile) return;
    setForm({
      bio: profile.bio ?? "",
      avatar_url: profile.avatar_url ?? "",
      website_url: profile.website_url ?? "",
      location: profile.location ?? "",
      github_handle: profile.github_handle ?? "",
      twitter_handle: profile.twitter_handle ?? "",
      privacy_level: profile.privacy_level,
      show_activity: profile.show_activity,
    });
  }, [profile]);

  const saveMutation = useMutation({
    mutationFn: () => updateMyProfile(form),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile", "me"] });
      push("success", "Profile saved");
    },
    onError: () => push("error", "Failed to save profile"),
  });

  function set(key: keyof ProfileUpdatePayload, value: unknown) {
    setForm((prev) => ({ ...prev, [key]: value }));
  }

  if (isLoading) return <div className="page text-muted text-sm">Loading…</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">
          <User size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
          My Profile
        </h1>
      </div>

      <form
        className="g-card profile-form"
        onSubmit={(e) => { e.preventDefault(); saveMutation.mutate(); }}
      >
        <div className="form-row">
          <label className="form-label">Bio</label>
          <textarea
            className="g-textarea"
            rows={3}
            value={form.bio ?? ""}
            onChange={(e) => set("bio", e.target.value)}
            placeholder="A short bio about yourself…"
          />
        </div>

        <div className="form-row">
          <label className="form-label">Avatar URL</label>
          <input
            className="g-input"
            value={form.avatar_url ?? ""}
            onChange={(e) => set("avatar_url", e.target.value)}
            placeholder="https://…"
          />
        </div>

        <div className="form-row">
          <label className="form-label">Website</label>
          <input
            className="g-input"
            value={form.website_url ?? ""}
            onChange={(e) => set("website_url", e.target.value)}
            placeholder="https://…"
          />
        </div>

        <div className="form-row">
          <label className="form-label">Location</label>
          <input
            className="g-input"
            value={form.location ?? ""}
            onChange={(e) => set("location", e.target.value)}
            placeholder="City, Country"
          />
        </div>

        <div className="form-two-col">
          <div className="form-row">
            <label className="form-label">GitHub handle</label>
            <input
              className="g-input"
              value={form.github_handle ?? ""}
              onChange={(e) => set("github_handle", e.target.value)}
              placeholder="username"
            />
          </div>
          <div className="form-row">
            <label className="form-label">Twitter handle</label>
            <input
              className="g-input"
              value={form.twitter_handle ?? ""}
              onChange={(e) => set("twitter_handle", e.target.value)}
              placeholder="username"
            />
          </div>
        </div>

        <div className="form-row">
          <label className="form-label">Privacy</label>
          <select
            className="g-select"
            value={form.privacy_level ?? "public"}
            onChange={(e) => set("privacy_level", e.target.value)}
          >
            <option value="public">Public — visible to everyone</option>
            <option value="team_only">Team only</option>
            <option value="private">Private</option>
          </select>
        </div>

        <div className="form-row form-checkbox">
          <input
            type="checkbox"
            id="show_activity"
            checked={form.show_activity ?? true}
            onChange={(e) => set("show_activity", e.target.checked)}
          />
          <label htmlFor="show_activity" className="form-label-inline">Show recent activity on profile</label>
        </div>

        <div className="form-actions">
          <button
            type="submit"
            className="g-btn g-btn-primary"
            disabled={saveMutation.isPending}
          >
            {saveMutation.isPending ? "Saving…" : "Save Changes"}
          </button>
        </div>
      </form>
    </div>
  );
}
