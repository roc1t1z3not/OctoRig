import { clsx } from "clsx";

const COLORS: Record<string, string> = {
  world: "var(--g-sky)",
  firerange: "var(--g-orange)",
  thirdparty: "var(--g-zinc)",
};

const LABELS: Record<string, string> = {
  world: "World",
  firerange: "Fire Range",
  thirdparty: "Third Party",
};

export function LabCategoryBadge({ category }: { category: string }) {
  return (
    <span
      className="g-badge"
      style={{ color: COLORS[category] ?? "var(--g-text-muted)", borderColor: COLORS[category] ?? "var(--g-border)" }}
    >
      {LABELS[category] ?? category}
    </span>
  );
}
