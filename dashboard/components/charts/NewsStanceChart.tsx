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
  Brush,
} from "recharts";
import type { NewsDaily, Event } from "@/types";

interface NewsStanceChartProps {
  data: NewsDaily[];
  events: Event[];
  selectedDate: string | null;
  onDateClick?: (date: string) => void;
}

export function NewsStanceChart({ data, events, selectedDate, onDateClick }: NewsStanceChartProps) {
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

  // Custom tooltip with click button
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;

    const handleButtonClick = (e: React.MouseEvent) => {
      e.stopPropagation();
      if (onDateClick && data.fullDate) {
        onDateClick(data.fullDate);
      }
    };

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
        {onDateClick && (
          <button
            onClick={handleButtonClick}
            className="mt-2 w-full bg-primary text-primary-foreground hover:bg-primary/90 text-xs py-2 px-3 rounded-md font-medium transition-colors"
          >
            이 시점 뉴스 보기
          </button>
        )}
      </div>
    );
  };

  // Handle chart click
  const handleChartClick = (data: any) => {
    if (data && data.activePayload && data.activePayload.length > 0) {
      const clickedData = data.activePayload[0].payload;
      if (clickedData.fullDate && onDateClick) {
        onDateClick(clickedData.fullDate);
      }
    }
  };

  // Custom dot component to show clickable points
  const CustomDot = (props: any) => {
    const { cx, cy, payload } = props;
    const isSelected = selectedDate === payload.fullDate;

    const handleClick = (e: React.MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();
      if (onDateClick && payload.fullDate) {
        onDateClick(payload.fullDate);
      }
    };

    return (
      <g onClick={handleClick} style={{ cursor: "pointer" }}>
        {/* Outer circle for selection */}
        {isSelected && (
          <circle
            cx={cx}
            cy={cy}
            r={8}
            fill="none"
            stroke="#8b5cf6"
            strokeWidth={2}
          />
        )}
        {/* Inner dot */}
        <circle
          cx={cx}
          cy={cy}
          r={isSelected ? 5 : 4}
          fill={getStanceColor(payload.stance)}
          stroke={isSelected ? "#8b5cf6" : "#fff"}
          strokeWidth={isSelected ? 2 : 1}
          className="hover:r-6 transition-all"
        />
      </g>
    );
  };

  return (
    <div className="w-full h-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={chartData}
          margin={{ top: 5, right: 30, left: 20, bottom: 20 }}
          onClick={handleChartClick}
        >
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
            dot={<CustomDot />}
            activeDot={({ cx, cy, payload }: any) => (
              <g
                onClick={(e) => {
                  e.stopPropagation();
                  if (onDateClick && payload.fullDate) {
                    onDateClick(payload.fullDate);
                  }
                }}
                style={{ cursor: "pointer" }}
              >
                <circle cx={cx} cy={cy} r={8} fill="#8b5cf6" fillOpacity={0.2} />
                <circle cx={cx} cy={cy} r={6} fill="#8b5cf6" stroke="#fff" strokeWidth={2} />
              </g>
            )}
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
          {/* Brush for zooming */}
          <Brush
            dataKey="date"
            height={30}
            stroke="#8b5cf6"
            fill="hsl(var(--muted))"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
