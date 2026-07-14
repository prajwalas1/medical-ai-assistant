import { type LucideIcon, ChevronDown } from "lucide-react";

interface ProviderOption {
  value: string;
  label: string;
  supportedLanguages: string[];
}

interface ProviderSelectorProps {
  label: string;
  icon: LucideIcon;
  value: string;
  onChange: (value: string) => void;
  options: ProviderOption[];
  disabled?: boolean;
  language: string;
}

export default function ProviderSelector({
  label,
  icon: Icon,
  value,
  onChange,
  options,
  disabled,
  language,
}: ProviderSelectorProps) {
  return (
    <div>
      <label className="flex items-center gap-1.5 text-xs font-medium tracking-wide text-slate-500 mb-1.5">
        <Icon size={13} />
        {label}
      </label>
      <div className="relative">
        <select
          className="w-full appearance-none rounded-xl border border-slate-200 bg-white px-4 py-3 pr-9 text-sm text-slate-800 shadow-sm transition focus:outline-none focus:ring-2 focus:ring-[#1F6F64]/30 focus:border-[#1F6F64] disabled:bg-slate-50 disabled:text-slate-400"
          value={value}
          disabled={disabled}
          onChange={(e) => onChange(e.target.value)}
        >
          {options.map((opt) => {
            const locked = !opt.supportedLanguages.includes(language);
            return (
              <option key={opt.value} value={opt.value} disabled={locked}>
                {opt.label}
                {locked ? " — not supported" : ""}
              </option>
            );
          })}
        </select>
        <ChevronDown
          size={16}
          className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-slate-400"
        />
      </div>
    </div>
  );
}