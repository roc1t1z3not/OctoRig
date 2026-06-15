import { Trash2, X } from "lucide-react";
import type { Rank } from "@/lib/api/ranks";
import { RankChip } from "@/components/ui/RankChip";

const EMPTY_FORM = { name: "", min_points: 0, icon: "", color: "#6b7280" };
export type RankFormState = typeof EMPTY_FORM;

export function RankForm({
  selected,
  form,
  onChange,
  onSave,
  onToggleActive,
  onDelete,
  onClose,
  isPending,
}: {
  selected: Rank | null;
  form: RankFormState;
  onChange: (patch: Partial<RankFormState>) => void;
  onSave: () => void;
  onToggleActive: (rank: Rank) => void;
  onDelete: (rank: Rank) => void;
  onClose: () => void;
  isPending: boolean;
}) {
  const isEditing = selected !== null;

  const previewRank = form.name
    ? { id: 0, name: form.name, color: form.color || null, icon: null, min_points: 0, is_active: true }
    : null;

  return (
    <div className="g-card">
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1rem" }}>
        <h2 className="font-mono" style={{ fontSize: "0.85rem" }}>
          {isEditing ? `Edit "${selected!.name}"` : "New Rank"}
        </h2>
        {isEditing && (
          <button className="g-btn g-btn-ghost" onClick={onClose} style={{ padding: "0.2rem" }}>
            <X size={14} />
          </button>
        )}
      </div>

      <div style={{ marginBottom: "1rem" }}>
        <RankChip rank={previewRank} />
      </div>

      <div className="rank-form">
        <label>
          Name
          <input
            type="text"
            value={form.name}
            onChange={(e) => onChange({ name: e.target.value })}
            placeholder="e.g. Hacker"
          />
        </label>

        <label>
          Min Points
          <input
            type="number"
            value={form.min_points}
            onChange={(e) => onChange({ min_points: Number(e.target.value) })}
            min={0}
          />
        </label>

        <label>
          Icon (lucide name)
          <input
            type="text"
            value={form.icon}
            onChange={(e) => onChange({ icon: e.target.value })}
            placeholder="e.g. terminal, skull, crown"
          />
        </label>

        <label>
          Color
          <div className="color-row">
            <input
              type="color"
              value={form.color}
              onChange={(e) => onChange({ color: e.target.value })}
            />
            <input
              type="text"
              value={form.color}
              onChange={(e) => onChange({ color: e.target.value })}
              placeholder="#6b7280"
              style={{ flex: 1 }}
            />
          </div>
        </label>

        {isEditing && (
          <label style={{ flexDirection: "row", alignItems: "center", gap: "0.5rem" }}>
            <input
              type="checkbox"
              checked={selected!.is_active}
              onChange={() => onToggleActive(selected!)}
            />
            Active
          </label>
        )}

        <div className="rank-form-actions">
          <button
            className="g-btn g-btn-primary"
            onClick={onSave}
            disabled={!form.name || isPending}
          >
            {isPending ? "Saving…" : isEditing ? "Save Changes" : "Create Rank"}
          </button>
          {isEditing && (
            <button
              className="g-btn g-btn-ghost"
              style={{ color: "var(--g-danger)" }}
              onClick={() => onDelete(selected!)}
            >
              <Trash2 size={12} />
              Delete
            </button>
          )}
        </div>
      </div>
    </div>
  );
}

export { EMPTY_FORM as EMPTY_RANK_FORM };
