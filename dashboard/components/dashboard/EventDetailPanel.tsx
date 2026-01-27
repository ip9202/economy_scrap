// EventDetailPanel Component - Side panel for event details
"use client";

import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Button } from "@/components/ui/button";
import { X } from "lucide-react";
import type { Event, NewsArticle } from "@/types";

interface EventDetailPanelProps {
  event: Event | null;
  relatedNews: NewsArticle[];
  open: boolean;
  onClose: () => void;
}

export function EventDetailPanel({
  event,
  relatedNews,
  open,
  onClose,
}: EventDetailPanelProps) {
  if (!event) return null;

  const getEventTypeLabel = (type: string) => {
    switch (type) {
      case "hike":
        return "금리 인상";
      case "cut":
        return "금리 인하";
      case "hold":
        return "금리 유지";
      default:
        return type;
    }
  };

  const getEventColor = (type: string) => {
    switch (type) {
      case "hike":
        return "text-red-600";
      case "cut":
        return "text-blue-600";
      case "hold":
        return "text-gray-600";
      default:
        return "text-gray-600";
    }
  };

  return (
    <Sheet open={open} onOpenChange={onClose}>
      <SheetContent className="w-[400px] sm:w-[540px]">
        <SheetHeader>
          <div className="flex items-center justify-between">
            <div>
              <SheetTitle>이벤트 상세 정보</SheetTitle>
              <SheetDescription>{event.date}</SheetDescription>
            </div>
            <Button variant="ghost" size="icon" onClick={onClose}>
              <X className="h-4 w-4" />
            </Button>
          </div>
        </SheetHeader>

        <div className="mt-6 space-y-6">
          {/* Event Type Badge */}
          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-2">
              이벤트 유형
            </h3>
            <p className={`text-lg font-semibold ${getEventColor(event.event_type)}`}>
              {getEventTypeLabel(event.event_type)}
            </p>
          </div>

          {/* Description */}
          <div>
            <h3 className="text-sm font-medium text-muted-foreground mb-2">
              설명
            </h3>
            <p className="text-sm text-foreground">{event.description}</p>
          </div>

          {/* Related News */}
          {relatedNews.length > 0 && (
            <div>
              <h3 className="text-sm font-medium text-muted-foreground mb-3">
                관련 뉴스 ({relatedNews.length})
              </h3>
              <div className="space-y-3 max-h-[400px] overflow-y-auto">
                {relatedNews.map((article, index) => (
                  <div
                    key={`${article.date}-${index}`}
                    className="p-3 bg-muted/50 rounded-lg"
                  >
                    <div className="flex items-start justify-between gap-2">
                      <div className="flex-1 min-w-0">
                        <p className="text-sm font-medium text-foreground line-clamp-2">
                          {article.title}
                        </p>
                        <p className="text-xs text-muted-foreground mt-1">
                          {article.date}
                        </p>
                      </div>
                      <div
                        className={`text-xs font-semibold px-2 py-1 rounded ${
                          article.stance > 0
                            ? "bg-red-100 text-red-700"
                            : article.stance < 0
                              ? "bg-blue-100 text-blue-700"
                              : "bg-gray-100 text-gray-700"
                        }`}
                      >
                        {article.stance > 0 ? "매파" : article.stance < 0 ? "비둘기" : "중립"}
                      </div>
                    </div>
                    {article.url && (
                      <a
                        href={article.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-xs text-primary hover:underline mt-2 inline-block"
                      >
                        원본 기사 보기
                      </a>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </SheetContent>
    </Sheet>
  );
}
