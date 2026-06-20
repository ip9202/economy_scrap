// Rate Series Chart Component
"use client";

import { useMemo } from "react";
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from "recharts";
import type { RateSeries } from "@/types";

interface RateSeriesChartProps {
  data: RateSeries[];
  usRate?: RateSeries[];
}

export function RateSeriesChart({ data, usRate }: RateSeriesChartProps) {
  // Process data for chart
  const chartData = useMemo(() => {
    // 미국 금리는 월별 → YYYY-MM 키로 매핑하여 한국 일별 날짜에 forward-fill
    const usMap = new Map<string, number>();
    if (usRate && usRate.length) {
      usRate.forEach((u) => {
        const month = String(u.date).slice(0, 7); // YYYY-MM
        if (u.value != null) usMap.set(month, u.value);
      });
    }
    return data.map((d) => {
      const month = String(d.date).slice(0, 7);
      return {
        date: new Date(d.date).toLocaleDateString("ko-KR", {
          month: "short",
          day: "numeric",
        }),
        fullDate: d.date,
        rate: d.value,
        usRate: usMap.has(month) ? usMap.get(month) ?? null : null,
      };
    });
  }, [data, usRate]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    return (
      <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
        <p className="text-sm font-medium text-foreground">{data.fullDate}</p>
        <p className="text-sm text-muted-foreground">
          금리: <span className="font-semibold text-primary">{data.rate}%</span>
        </p>
      </div>
    );
  };

  return (
    <div className="w-full" style={{ height: 400 }}>
      <ResponsiveContainer width="100%" height={400}>
        <AreaChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <defs>
            <linearGradient id="rateGradient" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="hsl(var(--primary))" stopOpacity={0.3} />
              <stop offset="95%" stopColor="hsl(var(--primary))" stopOpacity={0} />
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
          <XAxis
            dataKey="date"
            className="text-xs text-muted-foreground"
            tick={{ fill: "hsl(var(--muted-foreground))" }}
          />
          <YAxis
            domain={["dataMin - 0.25", "dataMax + 0.25"]}
            label={{
              value: "금리 (%)",
              angle: -90,
              position: "insideLeft",
              style: { fill: "hsl(var(--muted-foreground))" },
            }}
            tick={{ fill: "hsl(var(--muted-foreground))" }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Area
            type="monotone"
            dataKey="rate"
            stroke="hsl(var(--primary))"
            strokeWidth={2}
            fill="url(#rateGradient)"
            name="한국 기준금리"
          />
          {usRate && usRate.length > 0 && (
            <Area
              type="stepAfter"
              dataKey="usRate"
              stroke="#3b82f6"
              strokeWidth={2}
              fill="rgba(59,130,246,0.1)"
              name="미국 기준금리"
              connectNulls
            />
          )}
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
