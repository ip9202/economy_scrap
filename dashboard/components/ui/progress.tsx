"use client"

import * as React from "react"

import { cn } from "@/lib/utils"

function Progress({
  className,
  value,
  max = 100,
  ...props
}: React.ComponentProps<"div"> & {
  value?: number
  max?: number
}) {
  const percentage = value !== undefined ? Math.min(Math.max((value / max) * 100, 0), 100) : 0

  return (
    <div
      data-slot="progress"
      role="progressbar"
      aria-valuemax={max}
      aria-valuemin={0}
      aria-valuenow={value}
      className={cn(
        "relative h-2 w-full overflow-hidden rounded-full bg-primary/20",
        className
      )}
      {...props}
    >
      <div
        className="h-full w-full flex-1 bg-primary transition-all duration-300 ease-in-out"
        style={{ transform: `translateX(-${100 - percentage}%)` }}
      />
    </div>
  )
}

export { Progress }
