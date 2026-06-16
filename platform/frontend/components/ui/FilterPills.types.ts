// SPDX-License-Identifier: AGPL-3.0-or-later
// Copyright (c) 2026 CommonHuman-Lab
export interface FilterPillGroup {
  options: string[];
  value: string;
  onChange: (v: string) => void;
  label?: (v: string) => string;
}
