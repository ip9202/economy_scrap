// RateStance Dashboard Type Definitions

export interface NewsDaily {
  date: string;
  stance_mean: number;
  n_articles: number;
}

export interface RateSeries {
  date: string;
  value: number;
  unit: string;
}

export interface Event {
  date: string;
  event_type: 'hike' | 'cut' | 'hold';
  description: string;
}

export interface EventStudyData {
  event_date: string;
  event_type: string;
  day_offset: number;
  stance_mean: number;
  stance_std?: number;
}

export interface Statistics {
  total_articles: number;
  avg_stance: number;
  event_count: number;
  latest_event: string;
}

export interface NewsArticle {
  date: string;
  title: string;
  stance: number;
  url?: string;
}

// API Response types
export interface ApiResponse<T> {
  data: T;
  error?: string;
}

// Chart data types
export interface ChartDataPoint {
  date: string;
  value: number;
  label?: string;
}

export interface EventStudyChartData {
  eventType: string;
  data: { day: number; value: number }[];
}

// Data refresh types
export interface RefreshJobResponse {
  job_id: string;
  status: "pending" | "running" | "completed" | "failed";
  message: string;
}

export interface RefreshJobStatus {
  job_id: string;
  status: "pending" | "running" | "completed" | "failed";
  stage: string;
  progress: number;
  message?: string;
  error?: string;
}

export type RefreshStage =
  | "collecting_news"
  | "analyzing_sentiment"
  | "aggregating_daily"
  | "collecting_rates"
  | "detecting_events"
  | "analyzing_events";

export const REFRESH_STAGES: Record<RefreshStage, { label: string; minProgress: number; maxProgress: number }> = {
  collecting_news: { label: "뉴스 수집 중...", minProgress: 0, maxProgress: 20 },
  analyzing_sentiment: { label: "감성 분석 중...", minProgress: 20, maxProgress: 40 },
  aggregating_daily: { label: "일별 집계 중...", minProgress: 40, maxProgress: 60 },
  collecting_rates: { label: "금리 데이터 수집 중...", minProgress: 60, maxProgress: 80 },
  detecting_events: { label: "이벤트 탐지 중...", minProgress: 80, maxProgress: 90 },
  analyzing_events: { label: "이벤트 스터디 분석 중...", minProgress: 90, maxProgress: 100 },
};
