export interface FilterPillGroup {
  options: string[];
  value: string;
  onChange: (v: string) => void;
  label?: (v: string) => string;
}
