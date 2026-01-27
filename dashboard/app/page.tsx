// RateStance Dashboard Main Page
"use client";

import { useState } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { RefreshCw } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { StatCard } from "@/components/dashboard/StatCard";
import { EventDetailPanel } from "@/components/dashboard/EventDetailPanel";
import { NewsStanceChart } from "@/components/charts/NewsStanceChart";
import { RateSeriesChart } from "@/components/charts/RateSeriesChart";
import { EventStudyChart } from "@/components/charts/EventStudyChart";
import {
  useNewsDaily,
  useRateSeries,
  useEvents,
  useEventStudy,
  useStatistics,
} from "@/lib/hooks/use-news-data";
import type { Event } from "@/types";
import {
  FileText,
  TrendingUp,
  AlertCircle,
  Calendar,
} from "lucide-react";

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [isPanelOpen, setIsPanelOpen] = useState(false);

  // Fetch all data
  const { data: newsDaily, isLoading: isLoadingNews, error: newsError } = useNewsDaily();
  const { data: rateSeries, isLoading: isLoadingRate, error: rateError } = useRateSeries();
  const { data: events, isLoading: isLoadingEvents, error: eventsError } = useEvents();
  const { data: eventStudy, isLoading: isLoadingStudy, error: studyError } = useEventStudy();
  const { data: statistics, isLoading: isLoadingStats } = useStatistics();

  // Handle refresh
  const handleRefresh = async () => {
    await queryClient.invalidateQueries();
  };

  // Handle event click
  const handleEventClick = (event: Event) => {
    setSelectedEvent(event);
    setIsPanelOpen(true);
  };

  // Calculate loading state
  const isLoading =
    isLoadingNews || isLoadingRate || isLoadingEvents || isLoadingStudy || isLoadingStats;

  // Check for errors
  const hasError = newsError || rateError || eventsError || studyError;

  return (
    <div className="min-h-screen bg-background">
      {/* Header */}
      <header className="border-b border-border bg-card">
        <div className="container mx-auto px-4 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-foreground">
                RateStance: 금융 뉴스 감성 분석
              </h1>
              <p className="text-sm text-muted-foreground mt-1">
                한국은행 금리 결정과 뉴스 감성의 상관관계 분석
              </p>
            </div>
            <Button
              onClick={handleRefresh}
              disabled={isLoading}
              variant="outline"
              size="sm"
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? "animate-spin" : ""}`} />
              데이터 새로고침
            </Button>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-6">
        {hasError && (
          <div className="mb-6 p-4 bg-destructive/10 border border-destructive rounded-lg">
            <p className="text-sm text-destructive">
              데이터를 불러오는데 실패했습니다. 백엔드 서버가 실행 중인지 확인해주세요.
            </p>
          </div>
        )}

        {/* Statistics Cards */}
        {statistics && (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <StatCard
              title="총 뉴스 기사 수"
              value={statistics.total_articles.toLocaleString()}
              icon={FileText}
              description="분석된 기사 총합"
            />
            <StatCard
              title="평균 감성 점수"
              value={statistics.avg_stance.toFixed(3)}
              icon={TrendingUp}
              description={
                statistics.avg_stance > 0
                  ? "전반적으로 매파적"
                  : statistics.avg_stance < 0
                    ? "전반적으로 비둘기적"
                    : "중립적"
              }
            />
            <StatCard
              title="금리 변화 횟수"
              value={statistics.event_count}
              icon={AlertCircle}
              description="분석 기간 내 이벤트"
            />
            <StatCard
              title="최근 이벤트"
              value={statistics.latest_event}
              icon={Calendar}
              description="가장 최신 금리 결정"
            />
          </div>
        )}

        {/* Main Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
          {/* News Stance Timeseries Chart */}
          <Card className="lg:col-span-2">
            <CardHeader>
              <CardTitle>뉴스 감성 시계열</CardTitle>
            </CardHeader>
            <CardContent>
              {newsDaily && newsDaily.length > 0 && events && events.length > 0 ? (
                <div className="h-[400px]">
                  <NewsStanceChart data={newsDaily} events={events} />
                </div>
              ) : (
                <div className="h-[400px] flex items-center justify-center text-muted-foreground">
                  데이터를 불러오는 중...
                </div>
              )}
            </CardContent>
          </Card>

          {/* Rate Series Chart */}
          <Card>
            <CardHeader>
              <CardTitle>금리 시계열</CardTitle>
            </CardHeader>
            <CardContent>
              {rateSeries && rateSeries.length > 0 ? (
                <div className="h-[400px]">
                  <RateSeriesChart data={rateSeries} />
                </div>
              ) : (
                <div className="h-[400px] flex items-center justify-center text-muted-foreground">
                  데이터를 불러오는 중...
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Event Study Chart */}
        <Card className="mb-6">
          <CardHeader>
            <CardTitle>이벤트 스터디 분석</CardTitle>
          </CardHeader>
          <CardContent>
            {eventStudy && eventStudy.length > 0 ? (
              <div className="h-[400px]">
                <EventStudyChart data={eventStudy} />
              </div>
            ) : (
              <div className="h-[400px] flex items-center justify-center text-muted-foreground">
                데이터를 불러오는 중...
              </div>
            )}
          </CardContent>
        </Card>

        {/* Footer */}
        <footer className="text-center text-sm text-muted-foreground py-4">
          <p>
            데이터 출처: 한국은행 경제통계시스템 (ECOS), 연합뉴스 RSS
          </p>
          <p className="mt-1">
            마지막 업데이트: {new Date().toLocaleString("ko-KR")}
          </p>
        </footer>
      </main>

      {/* Event Detail Panel */}
      <EventDetailPanel
        event={selectedEvent}
        relatedNews={[]}
        open={isPanelOpen}
        onClose={() => setIsPanelOpen(false)}
      />
    </div>
  );
}
