import type { FilterPillGroup } from "./FilterPills.types";

export function FilterPills({ groups }: { groups: FilterPillGroup[] }) {
  return (
    <div className="filter-bar">
      {groups.map((group, i) => (
        <div key={i} className="filter-group">
          {group.options.map((opt) => (
            <button
              key={opt}
              className={`filter-pill ${group.value === opt ? "active" : ""}`}
              onClick={() => group.onChange(opt)}
            >
              {group.label ? group.label(opt) : opt.charAt(0).toUpperCase() + opt.slice(1)}
            </button>
          ))}
        </div>
      ))}
    </div>
  );
}
