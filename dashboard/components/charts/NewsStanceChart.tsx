// News Stance Timeseries Chart Component
"use client";

import { useMemo } from "react";
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
} from "recharts";
import type { NewsDaily, Event } from "@/types";

interface NewsStanceChartProps {
  data: NewsDaily[];
  events: Event[];
}

export function NewsStanceChart({ data, events }: NewsStanceChartProps) {
  // Process data for chart
  const chartData = useMemo(() => {
    return data.map((d) => ({
      date: new Date(d.date).toLocaleDateString("ko-KR", {
        month: "short",
        day: "numeric",
      }),
      fullDate: d.date,
      stance: d.stance_mean,
      articles: d.n_articles,
    }));
  }, [data]);

  // Get stance color based on value
  const getStanceColor = (value: number) => {
    if (value > 0) return "#ef4444"; // Red for hawkish
    if (value < 0) return "#3b82f6"; // Blue for dovish
    return "#9ca3af"; // Gray for neutral
  };

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;
    return (
      <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
        <p className="text-sm font-medium text-foreground">{data.fullDate}</p>
        <p className="text-sm text-muted-foreground">
          감성 점수:{" "}
          <span
            className="font-semibold"
            style={{ color: getStanceColor(data.stance) }}
          >
            {data.stance.toFixed(3)}
          </span>
        </p>
        <p className="text-sm text-muted-foreground">
          기사 수: <span className="font-semibold">{data.articles}</span>
        </p>
      </div>
    );
  };

  return (
    <div className="w-full h-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
          <XAxis
            dataKey="date"
            className="text-xs text-muted-foreground"
            tick={{ fill: "hsl(var(--muted-foreground))" }}
          />
          <YAxis
            domain={[-1, 1]}
            label={{
              value: "감성 점수",
              angle: -90,
              position: "insideLeft",
              style: { fill: "hsl(var(--muted-foreground))" },
            }}
            tick={{ fill: "hsl(var(--muted-foreground))" }}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            formatter={(value) => (
              <span style={{ color: "hsl(var(--muted-foreground))" }}>{value}</span>
            )}
          />
          <Line
            type="monotone"
            dataKey="stance"
            stroke="#8b5cf6"
            strokeWidth={2}
            dot={false}
            name="일별 평균 감성"
          />
          {/* Reference line at 0 */}
          <ReferenceLine
            y={0}
            stroke="hsl(var(--muted-foreground))"
            strokeDasharray="3 3"
            strokeWidth={1}
          />
          {/* Event markers */}
          {events.map((event, index) => (
            <ReferenceLine
              key={`${event.date}-${index}`}
              x={chartData.find((d) => d.fullDate === event.date)?.date}
              stroke={
                event.event_type === "hike"
                  ? "#ef4444"
                  : event.event_type === "cut"
                    ? "#3b82f6"
                    : "#9ca3af"
              }
              strokeDasharray="5 5"
              strokeWidth={1.5}
              label={{
                value: event.description,
                position: "top",
                fill: "hsl(var(--muted-foreground))",
                fontSize: 10,
              }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
