"use client";

import { Calendar } from "lucide-react";

interface MeetingInfo {
  date: string | null;
  days_until: number | null;
}

interface Props {
  bok: MeetingInfo;
  fomc: MeetingInfo;
}

function formatDate(dateStr: string | null): string {
  if (!dateStr) return "-";
  const d = new Date(dateStr);
  return `${d.getFullYear()}. ${d.getMonth() + 1}. ${d.getDate()}.`;
}

function DaysChip({ days }: { days: number | null }) {
  if (days == null) return null;
  const label = days === 0 ? "오늘" : `D-${days}`;
  const color =
    days <= 7
      ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
      : days <= 30
      ? "bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400"
      : "bg-muted text-muted-foreground";
  return (
    <span className={`text-xs font-semibold px-2 py-0.5 rounded-full ${color}`}>
      {label}
    </span>
  );
}

export function NextMeetingBanner({ bok, fomc }: Props) {
  return (
    <div className="flex flex-wrap gap-3 mb-4">
      {/* BOK */}
      <div className="flex items-center gap-2 bg-card border border-border rounded-lg px-4 py-2 shadow-sm">
        <Calendar className="w-4 h-4 text-primary shrink-0" />
        <span className="text-sm text-muted-foreground">🇰🇷 한국 금통위</span>
        <span className="text-sm font-medium">{formatDate(bok.date)}</span>
        <DaysChip days={bok.days_until} />
      </div>
      {/* FOMC */}
      <div className="flex items-center gap-2 bg-card border border-border rounded-lg px-4 py-2 shadow-sm">
        <Calendar className="w-4 h-4 text-blue-500 shrink-0" />
        <span className="text-sm text-muted-foreground">🇺🇸 미국 FOMC</span>
        <span className="text-sm font-medium">{formatDate(fomc.date)}</span>
        <DaysChip days={fomc.days_until} />
      </div>
    </div>
  );
}
