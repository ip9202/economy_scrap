// Calendar Component (Native HTML5 date input with Tailwind styling)
"use client";

import { forwardRef } from "react";

export interface CalendarProps extends React.InputHTMLAttributes<HTMLInputElement> {}

const Calendar = forwardRef<HTMLInputElement, CalendarProps>(
  ({ className, type = "date", ...props }, ref) => {
    return (
      <input
        type={type}
        className={
          "flex h-9 w-full rounded-md border border-input bg-transparent px-3 py-1 text-sm shadow-sm transition-colors file:border-0 file:bg-transparent file:text-sm file:font-medium file:text-foreground placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-ring disabled:cursor-not-allowed disabled:opacity-50 cursor-pointer"
        }
        ref={ref}
        {...props}
      />
    );
  }
);
Calendar.displayName = "Calendar";

export { Calendar };
