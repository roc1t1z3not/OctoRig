"use client";
import "../profile.css";

import { useEffect, useState } from "react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { User } from "lucide-react";
import { getMyProfile, updateMyProfile, type ProfileUpdatePayload } from "@/lib/api/profiles";
import { getMyRank } from "@/lib/api/ranks";
import { useNotificationsStore } from "@/stores/notifications.store";
import { ProfileForm } from "@/components/profile/ProfileForm";

export default function MyProfilePage() {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();

  const { data: profile, isLoading } = useQuery({
    queryKey: ["profile", "me"],
    queryFn: getMyProfile,
  });

  const { data: myRank } = useQuery({
    queryKey: ["rank", "me"],
    queryFn: getMyRank,
    staleTime: 60_000,
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

  if (isLoading) return <div className="page text-muted text-sm">Loading…</div>;

  return (
    <div className="page">
      <div className="page-header">
        <h1 className="page-title font-mono">
          <User size={18} style={{ display: "inline", marginRight: "0.5rem", verticalAlign: "middle" }} />
          My Profile
        </h1>
        {myRank?.rank && (
          <span
            style={{
              display: "inline-block",
              padding: "0.15rem 0.6rem",
              borderRadius: 99,
              fontSize: "0.7rem",
              fontFamily: "var(--font-mono, monospace)",
              fontWeight: 600,
              border: `1px solid ${myRank.rank.color ?? "var(--g-border)"}`,
              color: myRank.rank.color ?? "var(--g-text-muted)",
            }}
          >
            {myRank.rank.name}
          </span>
        )}
      </div>

      <ProfileForm
        form={form}
        onChange={(key, value) => setForm((prev) => ({ ...prev, [key]: value }))}
        onSubmit={(e) => { e.preventDefault(); saveMutation.mutate(); }}
        isPending={saveMutation.isPending}
      />
    </div>
  );
}
