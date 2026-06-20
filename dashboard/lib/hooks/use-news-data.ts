// TanStack Query Hooks for RateStance Dashboard
"use client";

import { useQuery, UseQueryResult } from "@tanstack/react-query";
import { api, ApiError } from "@/lib/api/client";
import type {
  NewsDaily,
  RateSeries,
  Event,
  EventStudyData,
  Statistics,
  NewsArticle,
} from "@/types";

// Query keys factory
export const queryKeys = {
  newsDaily: ["news-daily"] as const,
  rateSeries: ["rate-series"] as const,
  events: ["events"] as const,
  eventStudy: ["event-study"] as const,
  statistics: ["statistics"] as const,
  newsArticles: (limit: number, offset: number) =>
    ["news-articles", limit, offset] as const,
  all: () => [...queryKeys.newsDaily, ...queryKeys.rateSeries, ...queryKeys.events] as const,
};

// 날짜 범위가 설정되었을 때만 fetch (빈 초기값일 때 전체 데이터/과도한 호출 방지)
const dateRangeEnabled = (startDate?: string) => Boolean(startDate);

// Custom hooks
export function useNewsDaily(startDate?: string, endDate?: string): UseQueryResult<NewsDaily[], ApiError> {
  return useQuery({
    queryKey: ["news-daily", startDate, endDate],
    queryFn: () => api.getNewsDaily(startDate, endDate),
    enabled: dateRangeEnabled(startDate),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

export function useRateSeries(startDate?: string, endDate?: string): UseQueryResult<RateSeries[], ApiError> {
  return useQuery({
    queryKey: ["rate-series", startDate, endDate],
    queryFn: () => api.getRateSeries(startDate, endDate),
    enabled: dateRangeEnabled(startDate),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

// 미국 금리는 월별 데이터 → 날짜 필터 없이 전체 시리즈 fetch (차트에서 기간 매핑)
export function useUsRateSeries(): UseQueryResult<RateSeries[], ApiError> {
  return useQuery({
    queryKey: ["us-rate-series"],
    queryFn: () => api.getUsRateSeries(),
    staleTime: 60 * 60 * 1000, // 1시간 (FRED 월별 업데이트)
    gcTime: 4 * 60 * 60 * 1000,
  });
}

export function useEvents(startDate?: string, endDate?: string): UseQueryResult<Event[], ApiError> {
  return useQuery({
    queryKey: ["events", startDate, endDate],
    queryFn: () => api.getEvents(startDate, endDate),
    enabled: dateRangeEnabled(startDate),
    staleTime: 15 * 60 * 1000, // 15 minutes (events change rarely)
    gcTime: 30 * 60 * 1000,
  });
}

// 이벤트 스터디는 역사적 분석 → 날짜 범위 무관하게 항상 fetch
export function useEventStudy(): UseQueryResult<EventStudyData[], ApiError> {
  return useQuery({
    queryKey: ["event-study"],
    queryFn: () => api.getEventStudy(),
    staleTime: 30 * 60 * 1000,
    gcTime: 60 * 60 * 1000,
  });
}

export function useStatistics(startDate?: string, endDate?: string): UseQueryResult<Statistics, ApiError> {
  return useQuery({
    queryKey: ["statistics", startDate, endDate],
    queryFn: () => api.getStatistics(startDate, endDate),
    enabled: dateRangeEnabled(startDate),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

export function useNewsArticles(
  limit = 100,
  offset = 0
): UseQueryResult<NewsArticle[], ApiError> {
  return useQuery({
    queryKey: queryKeys.newsArticles(limit, offset),
    queryFn: () => api.getNewsArticles(limit, offset),
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

export function useNextMeetings() {
  return useQuery({
    queryKey: ["next-meetings"],
    queryFn: () => api.getNextMeetings(),
    staleTime: 60 * 60 * 1000, // 1시간 (발표일 일정은 거의 변하지 않음)
    gcTime: 24 * 60 * 60 * 1000,
  });
}
