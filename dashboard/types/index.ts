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
