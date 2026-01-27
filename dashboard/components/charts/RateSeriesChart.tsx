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
}

export function RateSeriesChart({ data }: RateSeriesChartProps) {
  // Process data for chart
  const chartData = useMemo(() => {
    return data.map((d) => ({
      date: new Date(d.date).toLocaleDateString("ko-KR", {
        month: "short",
        day: "numeric",
      }),
      fullDate: d.date,
      rate: d.value,
    }));
  }, [data]);

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
    <div className="w-full h-full">
      <ResponsiveContainer width="100%" height="100%">
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
            name="기준금리"
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
