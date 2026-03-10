// API Client for RateStance Dashboard
import type {
  NewsDaily,
  RateSeries,
  Event,
  EventStudyData,
  Statistics,
  NewsArticle,
  RefreshJobResponse,
  RefreshJobStatus,
} from "@/types";

// Use relative path for production (proxied through nginx), localhost for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "";

class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public statusText: string
  ) {
    super(message);
    this.name = "ApiError";
  }
}

async function fetchApi<T>(
  endpoint: string,
  options?: RequestInit
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;

  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        "Content-Type": "application/json",
        ...options?.headers,
      },
    });

    if (!response.ok) {
      throw new ApiError(
        `API request failed: ${endpoint}`,
        response.status,
        response.statusText
      );
    }

    return (await response.json()) as T;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(
      `Network error: ${endpoint}`,
      0,
      error instanceof Error ? error.message : "Unknown error"
    );
  }
}

export const api = {
  // Get daily news sentiment data
  getNewsDaily: (startDate?: string, endDate?: string): Promise<NewsDaily[]> => {
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    const queryString = params.toString();
    return fetchApi<NewsDaily[]>(`/api/data/news-daily${queryString ? `?${queryString}` : ""}`);
  },

  // Get rate series data
  getRateSeries: (startDate?: string, endDate?: string): Promise<RateSeries[]> => {
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    const queryString = params.toString();
    return fetchApi<RateSeries[]>(`/api/data/rate-series${queryString ? `?${queryString}` : ""}`);
  },

  // Get events
  getEvents: (startDate?: string, endDate?: string): Promise<Event[]> => {
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    const queryString = params.toString();
    return fetchApi<Event[]>(`/api/data/events${queryString ? `?${queryString}` : ""}`);
  },

  // Get event study data
  getEventStudy: (startDate?: string, endDate?: string): Promise<EventStudyData[]> => {
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    const queryString = params.toString();
    return fetchApi<EventStudyData[]>(`/api/data/event-study${queryString ? `?${queryString}` : ""}`);
  },

  // Get statistics with optional date range filter
  getStatistics: (startDate?: string, endDate?: string): Promise<Statistics> => {
    const params = new URLSearchParams();
    if (startDate) params.append("start_date", startDate);
    if (endDate) params.append("end_date", endDate);
    const queryString = params.toString();
    return fetchApi<Statistics>(`/api/data/statistics${queryString ? `?${queryString}` : ""}`);
  },

  // Get news articles (optional - for detail view)
  getNewsArticles: (limit = 100, offset = 0): Promise<NewsArticle[]> =>
    fetchApi<NewsArticle[]>(`/api/data/news-articles?limit=${limit}&offset=${offset}`),

  // Get news articles by date range
  getNewsByDate: (date: string, days = 3): Promise<NewsArticle[]> =>
    fetchApi<NewsArticle[]>(`/api/data/news-articles/by-date?date=${date}&days=${days}`),

  // Data refresh methods
  startRefresh: (startDate?: string, endDate?: string): Promise<RefreshJobResponse> => {
    const body = startDate && endDate ? { start_date: startDate, end_date: endDate } : {};
    return fetchApi<RefreshJobResponse>("/api/data/refresh", {
      method: "POST",
      body: JSON.stringify(body),
    });
  },

  getRefreshStatus: (jobId: string): Promise<RefreshJobStatus> =>
    fetchApi<RefreshJobStatus>(`/api/data/refresh/status/${jobId}`),
};

export { ApiError };
