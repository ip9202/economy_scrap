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

// Custom hooks
export function useNewsDaily(): UseQueryResult<NewsDaily[], ApiError> {
  return useQuery({
    queryKey: queryKeys.newsDaily,
    queryFn: api.getNewsDaily,
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 10 * 60 * 1000, // 10 minutes
  });
}

export function useRateSeries(): UseQueryResult<RateSeries[], ApiError> {
  return useQuery({
    queryKey: queryKeys.rateSeries,
    queryFn: api.getRateSeries,
    staleTime: 5 * 60 * 1000,
    gcTime: 10 * 60 * 1000,
  });
}

export function useEvents(): UseQueryResult<Event[], ApiError> {
  return useQuery({
    queryKey: queryKeys.events,
    queryFn: api.getEvents,
    staleTime: 15 * 60 * 1000, // 15 minutes (events change rarely)
    gcTime: 30 * 60 * 1000,
  });
}

export function useEventStudy(): UseQueryResult<EventStudyData[], ApiError> {
  return useQuery({
    queryKey: queryKeys.eventStudy,
    queryFn: api.getEventStudy,
    staleTime: 10 * 60 * 1000,
    gcTime: 20 * 60 * 1000,
  });
}

export function useStatistics(): UseQueryResult<Statistics, ApiError> {
  return useQuery({
    queryKey: queryKeys.statistics,
    queryFn: api.getStatistics,
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
