// RateEventCard — 최근/직전 금리 결정 비교 카드
import { Card, CardContent } from "@/components/ui/card";
import { TrendingDown, TrendingUp, Minus } from "lucide-react";
import type { RateEventDetail } from "@/types";

interface Props {
  latest: RateEventDetail;
  prev: RateEventDetail | null;
}

function formatDate(dateStr: string): string {
  const [y, m, d] = dateStr.split("-");
  return `${y}.${m}.${d}`;
}

function EventTypeLabel({ diff }: { type: string; diff: number }) {
  if (diff > 0) {
    return (
      <span className="inline-flex items-center gap-1 text-red-600 dark:text-red-400 font-semibold text-sm">
        <TrendingUp className="w-4 h-4" />
        인상
      </span>
    );
  }
  if (diff < 0) {
    return (
      <span className="inline-flex items-center gap-1 text-blue-600 dark:text-blue-400 font-semibold text-sm">
        <TrendingDown className="w-4 h-4" />
        인하
      </span>
    );
  }
  return (
    <span className="inline-flex items-center gap-1 text-muted-foreground font-semibold text-sm">
      <Minus className="w-4 h-4" />
      동결
    </span>
  );
}

function DiffBadge({ diff }: { diff: number }) {
  if (diff === 0) return null;
  const sign = diff > 0 ? "+" : "";
  const color =
    diff > 0
      ? "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400"
      : "bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400";
  return (
    <span className={`text-xs font-medium px-1.5 py-0.5 rounded ${color}`}>
      {sign}{diff.toFixed(2)}%p
    </span>
  );
}

export function RateEventCard({ latest, prev }: Props) {
  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardContent className="p-6">
        <p className="text-sm font-medium text-muted-foreground mb-3">최근 금리 결정</p>

        {/* 최근 결정 */}
        <div className="flex items-start justify-between gap-2">
          <div>
            <div className="flex items-center gap-2 mb-1">
              <EventTypeLabel type={latest.event_type} diff={latest.diff} />
              <DiffBadge diff={latest.diff} />
            </div>
            <div className="text-2xl font-bold text-foreground">
              {latest.value.toFixed(2)}%
            </div>
            <div className="text-xs text-muted-foreground mt-0.5">
              {formatDate(latest.date)}
            </div>
          </div>
          <div className="text-right text-xs text-muted-foreground pt-1">
            <div>직전</div>
            <div className="font-medium text-foreground text-sm">
              {latest.prev_value.toFixed(2)}%
            </div>
          </div>
        </div>

        {/* 구분선 + 직전 결정 */}
        {prev && (
          <>
            <div className="border-t border-border my-3" />
            <div className="flex items-center justify-between text-xs">
              <span className="text-muted-foreground">직전 결정</span>
              <div className="flex items-center gap-2">
                <EventTypeLabel type={prev.event_type} diff={prev.diff} />
                <span className="text-muted-foreground">
                  {prev.prev_value.toFixed(2)}% → {prev.value.toFixed(2)}%
                </span>
                <span className="text-muted-foreground">({formatDate(prev.date)})</span>
              </div>
            </div>
          </>
        )}
      </CardContent>
    </Card>
  );
}
