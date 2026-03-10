// Event Study Chart Component
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
  Area,
} from "recharts";
import type { EventStudyData } from "@/types";

interface EventStudyChartProps {
  data: EventStudyData[];
}

const EVENT_TYPE_COLORS: Record<string, string> = {
  hike: "#ef4444", // Red for rate hikes
  cut: "#3b82f6", // Blue for rate cuts
  hold: "#9ca3af", // Gray for holds
};

const EVENT_TYPE_LABELS: Record<string, string> = {
  hike: "금리 인상",
  cut: "금리 인하",
  hold: "금리 유지",
};

export function EventStudyChart({ data }: EventStudyChartProps) {
  // Process data for chart - group by event type
  const chartData = useMemo(() => {
    const grouped: Record<
      string,
      Record<number, { value: number; count: number; std?: number }>
    > = {};

    data.forEach((d) => {
      if (!grouped[d.event_type]) {
        grouped[d.event_type] = {};
      }
      if (!grouped[d.event_type][d.day_offset]) {
        grouped[d.event_type][d.day_offset] = { value: 0, count: 0 };
      }
      grouped[d.event_type][d.day_offset].value += d.stance_mean;
      grouped[d.event_type][d.day_offset].count += 1;
      if (d.stance_std !== undefined) {
        grouped[d.event_type][d.day_offset].std = d.stance_std;
      }
    });

    // Calculate averages and convert to array
    const result: Record<number, Record<string, number>> = {};
    Object.entries(grouped).forEach(([eventType, offsets]) => {
      Object.entries(offsets).forEach(([day, stats]) => {
        const dayNum = parseInt(day);
        if (!result[dayNum]) {
          result[dayNum] = { day: dayNum };
        }
        result[dayNum][eventType] = stats.value / stats.count;
        if (stats.std !== undefined) {
          result[dayNum][`${eventType}_std`] = stats.std;
        }
      });
    });

    return Object.values(result).sort((a, b) => a.day - b.day);
  }, [data]);

  // Get event types present in data
  const eventTypes = useMemo(() => {
    const types = new Set(data.map((d) => d.event_type));
    return Array.from(types);
  }, [data]);

  // Get event date range for display
  const eventDateRange = useMemo(() => {
    const eventDates = [...new Set(data.map((d) => d.event_date))].sort();
    if (eventDates.length === 0) return null;
    const latest = eventDates[eventDates.length - 1];
    const earliest = eventDates[0];
    return { earliest, latest, count: eventDates.length };
  }, [data]);

  // Get unique event dates by event type
  const eventDatesByType = useMemo(() => {
    const dates: Record<string, string[]> = {};
    data.forEach((d) => {
      if (!dates[d.event_type]) {
        dates[d.event_type] = [];
      }
      if (!dates[d.event_type].includes(d.event_date)) {
        dates[d.event_type].push(d.event_date);
      }
    });
    // Sort dates
    Object.keys(dates).forEach((type) => {
      dates[type].sort();
    });
    return dates;
  }, [data]);

  // Custom tooltip
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const day = payload[0].payload.day;
    return (
      <div className="bg-background border border-border rounded-lg p-3 shadow-lg">
        <p className="text-sm font-medium text-foreground mb-2">
          이벤트 {day > 0 ? `+${day}일` : day < 0 ? `${day}일` : "당일 (0일)"}
        </p>
        {payload.map((entry: any, index: number) => {
          // Safely convert dataKey to string
          const dataKeyStr = String(entry.dataKey || "");
          const eventType = dataKeyStr.replace("_std", "");
          if (dataKeyStr.includes("_std")) return null;
          return (
            <div key={`${dataKeyStr}-${index}`} className="mb-1">
              <p className="text-sm text-muted-foreground">
                {EVENT_TYPE_LABELS[eventType] || eventType}:{" "}
                <span
                  className="font-semibold"
                  style={{ color: EVENT_TYPE_COLORS[eventType] }}
                >
                  {entry.value?.toFixed(3)}
                </span>
              </p>
              {eventDatesByType[eventType] && (
                <p className="text-xs text-muted-foreground ml-2">
                  이벤트: {eventDatesByType[eventType].length}건
                  ({eventDatesByType[eventType][0]} ~ {eventDatesByType[eventType][eventDatesByType[eventType].length - 1]})
                </p>
              )}
            </div>
          );
        })}
      </div>
    );
  };

  return (
    <div className="w-full h-full flex flex-col">
      {/* Event Date Range Display */}
      {eventDateRange && (
        <div className="mb-4 p-3 bg-muted/50 rounded-lg flex-shrink-0">
          <div className="text-sm text-muted-foreground">
            <span className="font-medium text-foreground">분석 대상 이벤트:</span>{" "}
            총 {eventDateRange.count}건
            ({eventDateRange.earliest} ~ {eventDateRange.latest})
          </div>
          {Object.entries(eventDatesByType).map(([type, dates]) => (
            <div key={type} className="text-xs text-muted-foreground mt-1 ml-2">
              • {EVENT_TYPE_LABELS[type] || type}: {dates.length}건
              ({dates[0]}{dates.length > 1 ? ` ~ ${dates[dates.length - 1]}` : ""})
            </div>
          ))}
        </div>
      )}
      {/* Chart area takes remaining space */}
      <div className="flex-1 min-h-0">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart
            data={chartData}
            margin={{ top: 5, right: 30, left: 20, bottom: 60 }}
          >
            <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
            <XAxis
              dataKey="day"
              label={{
                value: "이벤트 전후 일수",
                position: "insideBottom",
                offset: -5,
                style: { fill: "hsl(var(--muted-foreground))" },
              }}
              tick={{ fill: "hsl(var(--muted-foreground))" }}
            />
            <YAxis
              label={{
                value: "평균 감성 점수",
                angle: -90,
                position: "insideLeft",
                style: { fill: "hsl(var(--muted-foreground))" },
              }}
              tick={{ fill: "hsl(var(--muted-foreground))" }}
            />
            <Tooltip content={<CustomTooltip />} />
            <Legend
              formatter={(value) => {
                return EVENT_TYPE_LABELS[value] || value;
              }}
            />
            {eventTypes.map((eventType) => (
              <Line
                key={eventType}
                type="monotone"
                dataKey={eventType}
                stroke={EVENT_TYPE_COLORS[eventType] || "#9ca3af"}
                strokeWidth={2}
                dot={false}
                name={eventType}
              />
            ))}
            {/* Reference line at 0 */}
            <Line
              dataKey={() => 0}
              stroke="hsl(var(--muted-foreground))"
              strokeDasharray="3 3"
              strokeWidth={1}
              dot={false}
              name=""
              legendType="none"
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
}
