// RateStance Dashboard Main Page
"use client";

import { useState, useEffect } from "react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { RefreshCw, Download, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Dialog, DialogContent, DialogDescription, DialogHeader, DialogTitle } from "@/components/ui/dialog";
import { Progress } from "@/components/ui/progress";
import { StatCard } from "@/components/dashboard/StatCard";
import { EventDetailPanel } from "@/components/dashboard/EventDetailPanel";
import { NewsDetailPanel } from "@/components/dashboard/NewsDetailPanel";
import { DateRangeSelector } from "@/components/dashboard/DateRangeSelector";
import { NewsStanceChart } from "@/components/charts/NewsStanceChart";
import { RateSeriesChart } from "@/components/charts/RateSeriesChart";
import { EventStudyChart } from "@/components/charts/EventStudyChart";
import { calculateDateRange } from "@/components/dashboard/DateRangeSelector";
import {
  useNewsDaily,
  useRateSeries,
  useEvents,
  useEventStudy,
  useStatistics,
} from "@/lib/hooks/use-news-data";
import { api } from "@/lib/api/client";
import { useToast } from "@/components/ui/use-toast";
import type { Event, RefreshJobStatus, RefreshStage, NewsArticle } from "@/types";
import { REFRESH_STAGES } from "@/types";
import {
  FileText,
  TrendingUp,
  AlertCircle,
  Calendar,
} from "lucide-react";

export default function DashboardPage() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [selectedEvent, setSelectedEvent] = useState<Event | null>(null);
  const [isEventPanelOpen, setIsEventPanelOpen] = useState(false);

  // News detail panel state
  const [selectedDate, setSelectedDate] = useState<string | null>(null);
  const [newsArticles, setNewsArticles] = useState<NewsArticle[]>([]);
  const [isNewsPanelOpen, setIsNewsPanelOpen] = useState(false);
  const [isLoadingNewsDetail, setIsLoadingNewsDetail] = useState(false);

  // Refresh state
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [refreshJobId, setRefreshJobId] = useState<string | null>(null);
  const [refreshStatus, setRefreshStatus] = useState<RefreshJobStatus | null>(null);
  const [showProgressDialog, setShowProgressDialog] = useState(false);
  const [currentTime, setCurrentTime] = useState<string>("");
  const [scrapeDateRange, setScrapeDateRange] = useState<{ startDate: string; endDate: string }>(
    calculateDateRange(6)
  );

  // Set current time on client side only to avoid hydration mismatch
  useEffect(() => {
    setCurrentTime(new Date().toLocaleString("ko-KR"));
  }, []);

  // Fetch all data with date range filtering
  const { data: newsDaily, isLoading: isLoadingNews, error: newsError } = useNewsDaily(
    scrapeDateRange.startDate,
    scrapeDateRange.endDate
  );
  const { data: rateSeries, isLoading: isLoadingRate, error: rateError } = useRateSeries(
    scrapeDateRange.startDate,
    scrapeDateRange.endDate
  );
  const { data: events, isLoading: isLoadingEvents, error: eventsError } = useEvents(
    scrapeDateRange.startDate,
    scrapeDateRange.endDate
  );
  const { data: eventStudy, isLoading: isLoadingStudy, error: studyError } = useEventStudy(
    scrapeDateRange.startDate,
    scrapeDateRange.endDate
  );
  const { data: statistics, isLoading: isLoadingStats } = useStatistics(
    scrapeDateRange.startDate,
    scrapeDateRange.endDate
  );

  // Handle simple refresh
  const handleRefresh = async () => {
    await queryClient.invalidateQueries();
  };

  // Handle data scraping refresh
  const handleScrapeRefresh = async () => {
    try {
      setIsRefreshing(true);
      setShowProgressDialog(true);

      // Start the refresh job with date range parameters
      const response = await api.startRefresh(scrapeDateRange.startDate, scrapeDateRange.endDate);
      setRefreshJobId(response.job_id);

      // Poll for status updates
      pollJobStatus(response.job_id);
    } catch (error) {
      console.error("Failed to start refresh:", error);
      toast({
        variant: "destructive",
        title: "스크래핑 시작 실패",
        description: "데이터 스크래핑을 시작하지 못했습니다. 백엔드 서버가 실행 중인지 확인해주세요.",
      });
      setIsRefreshing(false);
      setShowProgressDialog(false);
    }
  };

  // Poll job status
  const pollJobStatus = async (jobId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const status = await api.getRefreshStatus(jobId);
        setRefreshStatus(status);

        // Check if job is complete
        if (status.status === "completed") {
          clearInterval(pollInterval);
          setIsRefreshing(false);
          setShowProgressDialog(false);
          setRefreshJobId(null);

          // Show success notification
          toast({
            title: "스크래핑 완료",
            description: "데이터가 성공적으로 업데이트되었습니다.",
          });

          // Invalidate queries to reload data
          await queryClient.invalidateQueries();
        } else if (status.status === "failed") {
          clearInterval(pollInterval);
          setIsRefreshing(false);
          setShowProgressDialog(false);
          setRefreshJobId(null);

          // Show error notification
          toast({
            variant: "destructive",
            title: "스크래핑 실패",
            description: status.error || "데이터 스크래핑 중 오류가 발생했습니다.",
          });
        }
      } catch (error) {
        console.error("Failed to poll job status:", error);
        clearInterval(pollInterval);
        setIsRefreshing(false);
        setShowProgressDialog(false);
        setRefreshJobId(null);

        toast({
          variant: "destructive",
          title: "상태 확인 실패",
          description: "작업 상태를 확인하지 못했습니다.",
        });
      }
    }, 1500); // Poll every 1.5 seconds
  };

  // Get stage label in Korean
  const getStageLabel = (stage: RefreshStage): string => {
    return REFRESH_STAGES[stage]?.label || stage;
  };

  // Handle event click
  const handleEventClick = (event: Event) => {
    setSelectedEvent(event);
    setIsEventPanelOpen(true);
  };

  // Handle date click on chart
  const handleDateClick = async (date: string) => {
    try {
      setIsLoadingNewsDetail(true);
      setSelectedDate(date);
      setIsNewsPanelOpen(true);

      // Fetch news articles for the selected date
      const articles = await api.getNewsByDate(date, 3);
      setNewsArticles(articles);
    } catch (error) {
      console.error("Failed to fetch news articles:", error);
      toast({
        variant: "destructive",
        title: "뉴스 기사 불러오기 실패",
        description: "선택한 날짜의 뉴스 기사를 불러오는데 실패했습니다.",
      });
    } finally {
      setIsLoadingNewsDetail(false);
    }
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
            <div className="flex gap-2">
              <Button
                onClick={handleScrapeRefresh}
                disabled={isRefreshing || isLoading}
                variant="default"
                size="sm"
              >
                {isRefreshing ? (
                  <Loader2 className="h-4 w-4 mr-2 animate-spin" />
                ) : (
                  <Download className="h-4 w-4 mr-2" />
                )}
                스크래핑
              </Button>
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
        </div>
      </header>

      {/* Progress Dialog */}
      <Dialog open={showProgressDialog} onOpenChange={setShowProgressDialog}>
        <DialogContent className="sm:max-w-md">
          <DialogHeader>
            <DialogTitle>데이터 스크래핑 진행 중</DialogTitle>
            <DialogDescription>
              {refreshStatus ? getStageLabel(refreshStatus.stage as RefreshStage) : "작업 시작 중..."}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4 py-4">
            <Progress value={refreshStatus?.progress || 0} max={100} />
            <div className="flex items-center justify-between text-sm text-muted-foreground">
              <span>
                {refreshStatus ? getStageLabel(refreshStatus.stage as RefreshStage) : "초기화 중..."}
              </span>
              <span>{refreshStatus?.progress || 0}%</span>
            </div>
            {refreshStatus?.message && (
              <p className="text-sm text-muted-foreground">{refreshStatus.message}</p>
            )}
          </div>
        </DialogContent>
      </Dialog>

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

        {/* Date Range Selector */}
        <div className="mb-6">
          <DateRangeSelector
            onDateRangeChange={setScrapeDateRange}
            disabled={isRefreshing || isLoading}
          />
        </div>

        {/* Main Charts Row */}
        <div className="grid grid-cols-1 gap-6 mb-6">
          {/* News Stance Timeseries Chart */}
          <Card>
            <CardHeader>
              <CardTitle>뉴스 감성 시계열</CardTitle>
            </CardHeader>
            <CardContent>
              {newsDaily && newsDaily.length > 0 && events && events.length > 0 ? (
                <div className="h-[400px]">
                  <NewsStanceChart
                    data={newsDaily}
                    events={events}
                    selectedDate={selectedDate}
                    onDateClick={handleDateClick}
                  />
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
              <div className="h-[600px]">
                <EventStudyChart data={eventStudy} />
              </div>
            ) : (
              <div className="h-[600px] flex items-center justify-center text-muted-foreground">
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
            마지막 업데이트: {currentTime}
          </p>
        </footer>
      </main>

      {/* Event Detail Panel */}
      <EventDetailPanel
        event={selectedEvent}
        relatedNews={[]}
        open={isEventPanelOpen}
        onClose={() => setIsEventPanelOpen(false)}
      />

      {/* News Detail Panel */}
      <NewsDetailPanel
        date={selectedDate}
        articles={newsArticles}
        open={isNewsPanelOpen}
        onClose={() => setIsNewsPanelOpen(false)}
        isLoading={isLoadingNewsDetail}
      />
    </div>
  );
}
