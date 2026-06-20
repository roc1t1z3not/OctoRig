"use client";
// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab

import { useEffect, useState } from "react";
import { X } from "lucide-react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { updateMyProfile, type ProfileUpdatePayload, type UserProfile } from "@/lib/api/profiles";
import { useNotificationsStore } from "@/stores/notifications.store";
import { ProfileForm } from "@/components/profile/ProfileForm";
import { useEscapeKey } from "@/hooks/useEscapeKey";

export function EditProfileSheet({
  open,
  profile,
  onClose,
}: {
  open: boolean;
  profile: UserProfile | null | undefined;
  onClose: () => void;
}) {
  const qc = useQueryClient();
  const { push } = useNotificationsStore();
  const [form, setForm] = useState<ProfileUpdatePayload>({});

  useEffect(() => {
    if (!open || !profile) return;
    setForm({
      bio: profile.bio ?? "",
      avatar_url: profile.avatar_url ?? "",
      website_url: profile.website_url ?? "",
      location: profile.location ?? "",
      github_handle: profile.github_handle ?? "",
      privacy_level: profile.privacy_level,
      show_activity: profile.show_activity,
    });
  }, [open, profile]);

  const saveMutation = useMutation({
    mutationFn: () => updateMyProfile(form),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["profile"] });
      push("success", "Profile saved");
      onClose();
    },
    onError: () => push("error", "Failed to save profile"),
  });

  useEscapeKey(onClose, open);

  if (!open) return null;

  return (
    <>
      <div className="g-backdrop" onClick={onClose} />
      <div className="ev-sheet">
        <div className="ev-sheet-header">
          <h2 style={{ margin: 0, fontSize: "1rem", fontWeight: 700 }}>Edit Profile</h2>
          <button className="g-btn g-btn-ghost g-btn-sm" onClick={onClose}>
            <X size={14} />
          </button>
        </div>

        <div className="ev-sheet-body">
          <ProfileForm
            form={form}
            onChange={(key, value) => setForm((prev) => ({ ...prev, [key]: value }))}
            onSubmit={(e) => { e.preventDefault(); saveMutation.mutate(); }}
            isPending={saveMutation.isPending}
          />
        </div>
      </div>
    </>
  );
}
