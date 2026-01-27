// API Client for RateStance Dashboard
import type {
  NewsDaily,
  RateSeries,
  Event,
  EventStudyData,
  Statistics,
  NewsArticle,
} from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

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
  getNewsDaily: (): Promise<NewsDaily[]> =>
    fetchApi<NewsDaily[]>("/api/data/news-daily"),

  // Get rate series data
  getRateSeries: (): Promise<RateSeries[]> =>
    fetchApi<RateSeries[]>("/api/data/rate-series"),

  // Get events
  getEvents: (): Promise<Event[]> =>
    fetchApi<Event[]>("/api/data/events"),

  // Get event study data
  getEventStudy: (): Promise<EventStudyData[]> =>
    fetchApi<EventStudyData[]>("/api/data/event-study"),

  // Get statistics
  getStatistics: (): Promise<Statistics> =>
    fetchApi<Statistics>("/api/data/statistics"),

  // Get news articles (optional - for detail view)
  getNewsArticles: (limit = 100, offset = 0): Promise<NewsArticle[]> =>
    fetchApi<NewsArticle[]>(`/api/data/news-articles?limit=${limit}&offset=${offset}`),
};

export { ApiError };
