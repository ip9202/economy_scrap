// Date Range Selector Component
"use client";

import { useState, useEffect } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Calendar } from "@/components/ui/calendar";
import { Calendar as CalendarIcon } from "lucide-react";

interface DateRange {
  startDate: string;
  endDate: string;
}

interface DateRangeSelectorProps {
  onDateRangeChange: (range: DateRange) => void;
  disabled?: boolean;
}

const MONTH_OPTIONS = [1, 3, 6] as const;
const MAX_MONTHS = 6; // 최대 6개월 제한

// Calculate date range based on months from today
export function calculateDateRange(months: number): DateRange {
  const endDate = new Date();
  const startDate = new Date();

  // Subtract months from start date
  startDate.setMonth(startDate.getMonth() - months);

  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  };
}

// Format date for display (YYYY-MM-DD -> YYYY년 MM월 DD일)
export function formatDateRange(startDate: string, endDate: string): string {
  const start = new Date(startDate);
  const end = new Date(endDate);

  const formatDate = (date: Date): string => {
    return `${date.getFullYear()}년 ${date.getMonth() + 1}월 ${date.getDate()}일`;
  };

  return `${formatDate(start)} - ${formatDate(end)}`;
}

// 날짜 범위가 유효한지 확인 (최대 6개월, 종료일 >= 시작일)
function isValidDateRange(startDate: string, endDate: string): boolean {
  const start = new Date(startDate);
  const end = new Date(endDate);
  const today = new Date();

  // 종료일은 오늘 이하여야 함
  if (end > today) {
    return false;
  }

  // 시작일은 종료일 이하여야 함
  if (start > end) {
    return false;
  }

  // 최대 6개월 제한
  const maxStartDate = new Date(end);
  maxStartDate.setMonth(maxStartDate.getMonth() - MAX_MONTHS);

  if (start < maxStartDate) {
    return false;
  }

  return true;
}

export function DateRangeSelector({ onDateRangeChange, disabled = false }: DateRangeSelectorProps) {
  const [selectedMonths, setSelectedMonths] = useState<number>(1); // 기본 1개월
  const [isCustomMode, setIsCustomMode] = useState<boolean>(false);
  const [customStartDate, setCustomStartDate] = useState<string>("");
  const [customEndDate, setCustomEndDate] = useState<string>("");
  const [dateRange, setDateRange] = useState<DateRange>(() => calculateDateRange(1)); // 기본 1개월
  const [errorMessage, setErrorMessage] = useState<string>("");

  // 미리 설정된 기간 선택
  useEffect(() => {
    if (!isCustomMode) {
      const newRange = calculateDateRange(selectedMonths);
      setDateRange(newRange);
      onDateRangeChange(newRange);
      setErrorMessage("");
    }
  }, [selectedMonths, isCustomMode, onDateRangeChange]);

  // 사용자 정의 날짜 적용
  const handleCustomDateApply = () => {
    if (!customStartDate || !customEndDate) {
      setErrorMessage("시작일과 종료일을 모두 선택해주세요.");
      return;
    }

    if (!isValidDateRange(customStartDate, customEndDate)) {
      setErrorMessage("날짜 범위가 유효하지 않습니다. (최대 6개월, 종료일은 오늘 이내)");
      return;
    }

    const newRange = { startDate: customStartDate, endDate: customEndDate };
    setDateRange(newRange);
    onDateRangeChange(newRange);
    setErrorMessage("");
  };

  // 미리 설정된 기간 버튼 클릭
  const handlePresetClick = (months: number) => {
    setIsCustomMode(false);
    setSelectedMonths(months);
  };

  // 사용자 정의 모드 전환
  const handleCustomModeClick = () => {
    setIsCustomMode(true);
    // 현재 날짜 범위를 기본값으로 설정
    setCustomStartDate(dateRange.startDate);
    setCustomEndDate(dateRange.endDate);
    setErrorMessage("");
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center gap-2 text-base">
          <CalendarIcon className="h-4 w-4" />
          스크래핑 기간 설정
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {/* 기간 선택 방법 토글 */}
          <div>
            <label className="text-sm font-medium text-foreground mb-2 block">
              기간 선택 방법
            </label>
            <div className="flex flex-wrap gap-2">
              <Button
                variant={!isCustomMode ? "default" : "outline"}
                size="sm"
                onClick={() => handlePresetClick(selectedMonths)}
                disabled={disabled}
              >
                미리 설정
              </Button>
              <Button
                variant={isCustomMode ? "default" : "outline"}
                size="sm"
                onClick={handleCustomModeClick}
                disabled={disabled}
              >
                직접 설정
              </Button>
            </div>
          </div>

          {/* 미리 설정된 기간 버튼 */}
          {!isCustomMode && (
            <div>
              <label className="text-sm font-medium text-foreground mb-2 block">
                기간 선택
              </label>
              <div className="flex flex-wrap gap-2">
                {MONTH_OPTIONS.map((months) => (
                  <Button
                    key={months}
                    variant={selectedMonths === months ? "default" : "outline"}
                    size="sm"
                    onClick={() => handlePresetClick(months)}
                    disabled={disabled}
                    className="min-w-[60px]"
                  >
                    {months}개월
                  </Button>
                ))}
              </div>
            </div>
          )}

          {/* 사용자 정의 날짜 선택기 */}
          {isCustomMode && (
            <div className="space-y-3">
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  시작일
                </label>
                <Calendar
                  value={customStartDate}
                  onChange={(e) => setCustomStartDate(e.target.value)}
                  disabled={disabled}
                  max={customEndDate || new Date().toISOString().split('T')[0]}
                />
              </div>
              <div>
                <label className="text-sm font-medium text-foreground mb-2 block">
                  종료일
                </label>
                <Calendar
                  value={customEndDate}
                  onChange={(e) => setCustomEndDate(e.target.value)}
                  disabled={disabled}
                  max={new Date().toISOString().split('T')[0]}
                />
              </div>
              {errorMessage && (
                <p className="text-sm text-destructive">{errorMessage}</p>
              )}
              <Button
                onClick={handleCustomDateApply}
                disabled={disabled}
                className="w-full"
                size="sm"
              >
                적용
              </Button>
            </div>
          )}

          {/* 선택된 기간 표시 */}
          <div className="rounded-lg bg-muted p-3">
            <div className="text-xs text-muted-foreground mb-1">선택된 기간</div>
            <div className="text-sm font-medium text-foreground">
              {formatDateRange(dateRange.startDate, dateRange.endDate)}
            </div>
            {isCustomMode && (
              <div className="text-xs text-muted-foreground mt-1">
                ({dateRange.startDate} ~ {dateRange.endDate})
              </div>
            )}
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
