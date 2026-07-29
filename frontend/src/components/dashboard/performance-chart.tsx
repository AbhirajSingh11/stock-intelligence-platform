"use client";

import { useMemo, useState } from "react";

import {
  formatChartDate,
  formatCompactCurrency,
  formatCurrency,
  formatDateRange,
} from "@/lib/formatters";
import type {
  PerformancePeriod,
  PerformanceSeries,
} from "@/types/dashboard";

const chartWidth = 760;
const chartHeight = 270;
const padding = { top: 18, right: 18, bottom: 38, left: 58 };
const plotWidth = chartWidth - padding.left - padding.right;
const plotHeight = chartHeight - padding.top - padding.bottom;
const defaultPerformancePeriod: PerformancePeriod = "1Y";
const performancePeriods: PerformancePeriod[] = [
  "1M",
  "3M",
  "6M",
  "1Y",
  "ALL",
];

interface PerformanceChartProps {
  performance: PerformanceSeries[];
  currency: string;
}

export function PerformanceChart({
  performance,
  currency,
}: PerformanceChartProps) {
  const [selectedPeriod, setSelectedPeriod] =
    useState<PerformancePeriod>(defaultPerformancePeriod);
  const series = useMemo(
    () => {
      const match = performance.find(
        (candidate) => candidate.period === selectedPeriod,
      );
      if (!match) {
        throw new Error(
          `Dashboard response is missing the ${selectedPeriod} series.`,
        );
      }
      return match;
    },
    [performance, selectedPeriod],
  );

  const chart = useMemo(() => {
    const values = series.points.map((point) => point.value);
    const rawMin = Math.min(...values);
    const rawMax = Math.max(...values);
    const range = Math.max(rawMax - rawMin, 1);
    const yMin = Math.floor((rawMin - range * 0.1) / 500) * 500;
    const yMax = Math.ceil((rawMax + range * 0.1) / 500) * 500;
    const yRange = yMax - yMin;

    const points = series.points.map((point, index) => {
      const x =
        padding.left +
        (index / Math.max(series.points.length - 1, 1)) * plotWidth;
      const y =
        padding.top + ((yMax - point.value) / Math.max(yRange, 1)) * plotHeight;
      return {
        ...point,
        label: formatChartDate(point.date, selectedPeriod),
        x,
        y,
      };
    });

    const linePath = points
      .map((point, index) => `${index === 0 ? "M" : "L"}${point.x},${point.y}`)
      .join(" ");
    const areaPath = `${linePath} L${points.at(-1)?.x},${
      padding.top + plotHeight
    } L${points[0]?.x},${padding.top + plotHeight} Z`;
    const ticks = Array.from({ length: 4 }, (_, index) => {
      const ratio = index / 3;
      return {
        value: yMax - ratio * yRange,
        y: padding.top + ratio * plotHeight,
      };
    });

    return { points, linePath, areaPath, ticks };
  }, [selectedPeriod, series]);

  const labelStep = Math.max(1, Math.ceil((chart.points.length - 1) / 4));

  return (
    <section
      className="border border-border bg-panel"
      aria-labelledby="performance-heading"
    >
      <div className="flex flex-col gap-4 border-b border-border p-4 sm:flex-row sm:items-start sm:justify-between sm:p-5">
        <div>
          <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-secondary">
            Portfolio performance
          </p>
          <div className="mt-2 flex flex-wrap items-baseline gap-x-3 gap-y-1">
            <h2
              id="performance-heading"
              className="financial-figure font-mono text-2xl font-semibold text-foreground"
            >
              {formatCurrency(series.points.at(-1)?.value ?? 0, currency)}
            </h2>
            <span className="financial-figure font-mono text-sm font-semibold text-positive">
              {`+${series.change_percent.toFixed(1)}%`}
            </span>
          </div>
          <p className="mt-1 font-mono text-[10px] text-secondary">
            {formatDateRange(series.start_date, series.end_date)}
          </p>
        </div>

        <div
          className="flex w-fit border border-border"
          role="group"
          aria-label="Performance period"
        >
          {performancePeriods.map((period) => {
            const isSelected = period === selectedPeriod;
            return (
              <button
                key={period}
                type="button"
                aria-pressed={isSelected}
                onClick={() => setSelectedPeriod(period)}
                className={`min-w-10 border-r border-border px-2.5 py-2 font-mono text-[10px] font-semibold outline-none last:border-r-0 focus-visible:z-10 focus-visible:ring-2 focus-visible:ring-positive ${
                  isSelected
                    ? "bg-positive text-[#07120E]"
                    : "bg-transparent text-secondary hover:bg-white/[0.04] hover:text-foreground"
                }`}
              >
                {period}
              </button>
            );
          })}
        </div>
      </div>

      <div className="p-3 sm:p-5">
        <figure>
          <svg
            className="block h-auto w-full"
            viewBox={`0 0 ${chartWidth} ${chartHeight}`}
            role="img"
            aria-labelledby="chart-title chart-description"
          >
            <title id="chart-title">
              {`Portfolio value for the ${selectedPeriod} period`}
            </title>
            <desc id="chart-description">
              {`Portfolio value changed ${series.change_percent.toFixed(
                1,
              )} percent from ${series.start_date} through ${series.end_date}.`}
            </desc>

            {chart.ticks.map((tick) => (
              <g key={tick.value}>
                <line
                  x1={padding.left}
                  x2={chartWidth - padding.right}
                  y1={tick.y}
                  y2={tick.y}
                  stroke="#263140"
                  strokeWidth="1"
                  vectorEffect="non-scaling-stroke"
                />
                <text
                  x={padding.left - 10}
                  y={tick.y + 3}
                  fill="#96A2B1"
                  fontFamily="Cascadia Code, Consolas, monospace"
                  fontSize="10"
                  textAnchor="end"
                >
                  {formatCompactCurrency(tick.value, currency)}
                </text>
              </g>
            ))}

            <path d={chart.areaPath} fill="#32C48D" fillOpacity="0.07" />
            <path
              d={chart.linePath}
              fill="none"
              stroke="#32C48D"
              strokeWidth="2.5"
              strokeLinecap="square"
              strokeLinejoin="round"
              vectorEffect="non-scaling-stroke"
            />

            {chart.points.map((point, index) => {
              const showLabel =
                index === 0 ||
                index === chart.points.length - 1 ||
                index % labelStep === 0;
              return (
                <g key={point.date}>
                  {showLabel && (
                    <text
                      x={point.x}
                      y={chartHeight - 10}
                      fill="#96A2B1"
                      fontFamily="Cascadia Code, Consolas, monospace"
                      fontSize="9"
                      textAnchor={
                        index === 0
                          ? "start"
                          : index === chart.points.length - 1
                            ? "end"
                            : "middle"
                      }
                    >
                      {point.label}
                    </text>
                  )}
                  {index === chart.points.length - 1 && (
                    <>
                      <circle
                        cx={point.x}
                        cy={point.y}
                        r="6"
                        fill="#131C27"
                        stroke="#32C48D"
                        strokeWidth="2"
                        vectorEffect="non-scaling-stroke"
                      />
                      <circle
                        cx={point.x}
                        cy={point.y}
                        r="2"
                        fill="#32C48D"
                      />
                    </>
                  )}
                </g>
              );
            })}
          </svg>

          <table className="sr-only">
            <caption>
              {`${selectedPeriod} portfolio performance data`}
            </caption>
            <thead>
              <tr>
                <th scope="col">Date</th>
                <th scope="col">Portfolio value</th>
              </tr>
            </thead>
            <tbody>
              {series.points.map((point) => (
                <tr key={point.date}>
                  <td>{formatChartDate(point.date, selectedPeriod)}</td>
                  <td>{formatCurrency(point.value, currency)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </figure>
      </div>
    </section>
  );
}
