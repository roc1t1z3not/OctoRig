// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
import type { ReactNode } from "react";
import { SettingRow } from "./SettingRow";

export function SettingToggle({
  label,
  description,
  checked,
  onChange,
  indent,
}: {
  label: ReactNode;
  description: ReactNode;
  checked: boolean;
  onChange: (checked: boolean) => void;
  indent?: boolean;
}) {
  return (
    <SettingRow
      label={label}
      description={description}
      indent={indent}
      control={
        <label className="toggle">
          <input
            type="checkbox"
            checked={checked}
            onChange={(e) => onChange(e.target.checked)}
          />
          <span className="toggle-track" />
        </label>
      }
    />
  );
}
