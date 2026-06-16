// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import type { ReactNode } from "react";

export function SettingRow({
  label,
  description,
  control,
  indent,
}: {
  label: ReactNode;
  description: ReactNode;
  control: ReactNode;
  indent?: boolean;
}) {
  return (
    <div className={`settings-row${indent ? " settings-row--indent" : ""}`}>
      <div className="settings-row-info">
        <span className="settings-row-label">{label}</span>
        <span className="settings-row-desc">{description}</span>
      </div>
      {control}
    </div>
  );
}
