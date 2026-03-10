// NewsDetailPanel Component - Side panel for news articles at a specific date
"use client";

import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { ExternalLink, Calendar } from "lucide-react";
import type { NewsArticle } from "@/types";

interface NewsDetailPanelProps {
  date: string | null;
  articles: NewsArticle[];
  open: boolean;
  onClose: () => void;
  isLoading?: boolean;
}

export function NewsDetailPanel({
  date,
  articles,
  open,
  onClose,
  isLoading = false,
}: NewsDetailPanelProps) {
  const getStanceLabel = (stance: number) => {
    if (stance > 0.1) return "매파";
    if (stance < -0.1) return "비둘기";
    return "중립";
  };

  const getStanceDescription = (stance: number) => {
    if (stance > 0.1) return "금리 인하를 반대하는 매파적 성향의 뉴스입니다.";
    if (stance < -0.1) return "금리 인하를 지지하는 비둘기적 성향의 뉴스입니다.";
    return "중립적인 성향의 뉴스입니다.";
  };

  const getStanceColor = (stance: number) => {
    if (stance > 0.1) return "bg-red-100 text-red-700 hover:bg-red-200";
    if (stance < -0.1) return "bg-blue-100 text-blue-700 hover:bg-blue-200";
    return "bg-gray-100 text-gray-700 hover:bg-gray-200";
  };

  const getStanceValue = (stance: number) => {
    const sign = stance > 0 ? "+" : "";
    return `${sign}${stance.toFixed(3)}`;
  };

  return (
    <Dialog open={open} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>해당 날짜의 뉴스 기사</DialogTitle>
          <DialogDescription className="flex items-center gap-1">
            <Calendar className="h-3 w-3" />
            {date || "선택된 날짜"}
          </DialogDescription>
        </DialogHeader>

        <div className="mt-6">
          {isLoading ? (
            <div className="flex items-center justify-center py-12">
              <p className="text-sm text-muted-foreground">불러오는 중...</p>
            </div>
          ) : articles.length === 0 ? (
            <div className="flex flex-col items-center justify-center py-12 text-center">
              <p className="text-sm text-muted-foreground">
                해당 기간에 뉴스 기사가 없습니다.
              </p>
            </div>
          ) : (
            <>
              <div className="mb-6 p-4 bg-muted rounded-lg">
                <h3 className="text-sm font-semibold text-foreground mb-2">감성 분석 설명</h3>
                <div className="space-y-2 text-xs text-muted-foreground">
                  <div className="flex items-start gap-2">
                    <span className="font-semibold text-red-600">매파 (Hawkish)</span>
                    <span>: 금리 인상을 선호하거나 금리 인하를 반대하는 뉴스</span>
                  </div>
                  <div className="flex items-start gap-2">
                    <span className="font-semibold text-blue-600">비둘기 (Dovish)</span>
                    <span>: 금리 인하를 선호하거나 금통 완화를 지지하는 뉴스</span>
                  </div>
                </div>
              </div>

              <div className="mb-4">
                <p className="text-sm text-muted-foreground">
                  총 <span className="font-semibold text-foreground">{articles.length}</span>개의 기사
                </p>
                <p className="text-xs text-muted-foreground mt-1">
                  감성 점수 절대값 기준 정렬 (가장 매파/비둘기적 순)
                </p>
              </div>

              <div className="space-y-3">
                {articles.map((article, index) => (
                  <div
                    key={`${article.date}-${index}`}
                    className="p-4 bg-muted/50 rounded-lg hover:bg-muted/70 transition-colors"
                  >
                    {/* Article header with date and stance */}
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground line-clamp-2 mb-1">
                          {article.title}
                        </p>
                        <p className="text-xs text-muted-foreground flex items-center gap-1">
                          <Calendar className="h-3 w-3" />
                          {article.date}
                        </p>
                      </div>
                      <Badge
                        variant="secondary"
                        className={`text-xs font-semibold shrink-0 ${getStanceColor(article.stance)}`}
                      >
                        {getStanceLabel(article.stance)}
                      </Badge>
                    </div>

                    {/* Stance score */}
                    <div className="flex items-center justify-between mt-2">
                      <div className="flex items-center gap-2">
                        <span className="text-xs text-muted-foreground">감성 점수:</span>
                        <span
                          className={`text-sm font-semibold ${
                            article.stance > 0
                              ? "text-red-600"
                              : article.stance < 0
                                ? "text-blue-600"
                                : "text-gray-600"
                          }`}
                        >
                          {getStanceValue(article.stance)}
                        </span>
                      </div>

                      {/* URL link if available */}
                      {article.url && (
                        <a
                          href={article.url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-xs text-primary hover:text-primary/80 flex items-center gap-1 transition-colors"
                        >
                          <ExternalLink className="h-3 w-3" />
                          원문
                        </a>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </>
          )}
        </div>
      </DialogContent>
    </Dialog>
  );
}
