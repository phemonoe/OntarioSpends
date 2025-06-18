// Tremor BarList [v0.1.1]

import React from "react"

import { cn, focusRing } from "@/lib/utils"
import Link from "next/link"

type Bar<T> = T & {
  key?: string
  href?: string
  value: number
  name: string
  className?: string
}

interface BarListProps<T = unknown>
  extends React.HTMLAttributes<HTMLDivElement> {
  data: Bar<T>[]
  valueFormatter?: (value: number) => string
  showAnimation?: boolean
  onValueChange?: (payload: Bar<T>) => void
  sortOrder?: "ascending" | "descending" | "none"
}

function BarListInner<T>(
  {
    data = [],
    valueFormatter = (value) => value.toString(),
    showAnimation = false,
    onValueChange,
    sortOrder = "descending",
    className,
    ...props
  }: BarListProps<T>,
  forwardedRef: React.ForwardedRef<HTMLDivElement>,
) {
  const Component = onValueChange ? "button" : "div"
  const sortedData = React.useMemo(() => {
    if (sortOrder === "none") {
      return data
    }
    return [...data].sort((a, b) => {
      return sortOrder === "ascending" ? a.value - b.value : b.value - a.value
    })
  }, [data, sortOrder])

  const widths = React.useMemo(() => {
    const maxValue = Math.max(...sortedData.map((item) => item.value), 0)
    return sortedData.map((item) =>
      item.value === 0 ? 0 : Math.max((item.value / maxValue) * 100, 2),
    )
  }, [sortedData])

  const rowHeight = "h-8"

  return (
    <div
      ref={forwardedRef}
      className={cn("flex justify-between space-x-6", className)}
      aria-sort={sortOrder}
      tremor-id="tremor-raw"
      {...props}
    >
      <div className="relative w-full space-y-1.5">
        {sortedData.map((item, index) => (
          <Component
            key={item.key ?? item.name}
            onClick={() => {
              onValueChange?.(item)
            }}
            className={cn(
              // base
              "group w-full rounded",
              // focus
              focusRing,
              onValueChange
                ? [
                  "!-m-0 cursor-pointer",
                  // hover
                  "hover:bg-gray-50 ",
                ]
                : "",
            )}
          >
            <div
              className={cn(
                // base
                "flex items-center rounded transition-all",
                rowHeight,
                // background color
                "bg-blue-200 ",
                item.className,
                onValueChange
                  ? "group-hover:bg-blue-300 "
                  : "",
                // margin and duration
                {
                  "mb-0": index === sortedData.length - 1,
                  "duration-800": showAnimation,
                },
              )}
              style={{ width: `${widths[index]}%` }}
            >
              <div className={cn("absolute left-2 flex max-w-full pr-2")}>
                {item.href ? (
                  <Link
                    href={item.href}
                    className={cn(
                      // base
                      "truncate whitespace-nowrap rounded text-sm",
                      // text color
                      "text-gray-900 ",
                      // hover
                      "hover:underline hover:underline-offset-2",
                      // focus
                      focusRing,
                    )}
                  >
                    {item.name}
                  </Link>
                ) : (
                  <p
                    className={cn(

                      // base
                      "truncate whitespace-nowrap text-sm",
                      // text color
                      "text-gray-900 ",
                    )}
                  >
                    {item.name}
                  </p>
                )}
              </div>
            </div>
          </Component>
        ))}
      </div>
      <div>
        {sortedData.map((item, index) => (
          <div
            key={item.key ?? item.name}
            className={cn(
              "flex items-center justify-end",
              rowHeight,
              index === sortedData.length - 1 ? "mb-0" : "mb-1.5",
            )}
          >
            <p
              className={cn(
                // base
                "truncate whitespace-nowrap text-sm leading-none",
                // text color
                "text-gray-900 ",
              )}
            >
              {valueFormatter(item.value)}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

BarListInner.displayName = "BarList"

const BarList = React.forwardRef(BarListInner) as <T>(
  p: BarListProps<T> & { ref?: React.ForwardedRef<HTMLDivElement> },
) => ReturnType<typeof BarListInner>

export { BarList, type BarListProps }
