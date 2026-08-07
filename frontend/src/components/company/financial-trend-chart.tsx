"use client";

import { useEffect, useRef, useState } from "react";

import {
  formatFinancialChartDate,
  formatFundamentalValue,
  formatSecDate,
} from "@/lib/formatters";
import type { FundamentalMetricSeries } from "@/types/company";

const initialWidth = 760;
const minimumMeasuredWidth = 240;
const height = 260;
const padding = { top: 20, right: 30, bottom: 42, left: 82 };
const plotHeight = height - padding.top - padding.bottom;
const xAxisFontSize = 10;
const estimatedCharacterWidth = 6.4;
const minimumLabelGap = 12;
const targetLabelSpacing = 140;
const maximumLabelCount = 5;
const millisecondsPerDay = 86_400_000;
const gapThresholdDays = {
  annual: 550,
  quarterly: 155,
} as const;

type TickAnchor = "start" | "middle" | "end";

interface ChartPoint {
  x: number;
  y: number;
  timestamp: number;
  fact: FundamentalMetricSeries["facts"][number];
}

interface XAxisTick {
  point: ChartPoint;
  label: string;
  anchor: TickAnchor;
  left: number;
  right: number;
}

interface ChartSegment {
  start: ChartPoint;
  end: ChartPoint;
  gapDays: number;
  hasMissingPeriod: boolean;
}

function parseUtcTimestamp(periodEnd: string): number {
  const match = /^(\d{4})-(\d{2})-(\d{2})$/.exec(periodEnd);
  if (!match) {
    throw new Error(`Invalid SEC period-end date: ${periodEnd}`);
  }

  return Date.UTC(Number(match[1]), Number(match[2]) - 1, Number(match[3]));
}

function tickBounds(
  point: ChartPoint,
  label: string,
  anchor: TickAnchor,
): Pick<XAxisTick, "left" | "right"> {
  const width = label.length * estimatedCharacterWidth;
  if (anchor === "start") {
    return { left: point.x, right: point.x + width };
  }
  if (anchor === "end") {
    return { left: point.x - width, right: point.x };
  }
  return { left: point.x - width / 2, right: point.x + width / 2 };
}

function ticksOverlap(first: XAxisTick, second: XAxisTick): boolean {
  return !(
    first.right + minimumLabelGap <= second.left ||
    second.right + minimumLabelGap <= first.left
  );
}

function buildTick(point: ChartPoint, anchor: TickAnchor): XAxisTick {
  const label = formatFinancialChartDate(point.fact.period_end);
  return {
    point,
    label,
    anchor,
    ...tickBounds(point, label, anchor),
  };
}

function selectXAxisTicks(
  points: ChartPoint[],
  plotWidth: number,
): XAxisTick[] {
  if (points.length === 0) {
    return [];
  }
  if (points.length === 1) {
    return [buildTick(points[0], "middle")];
  }

  const firstTick = buildTick(points[0], "start");
  const lastTick = buildTick(points.at(-1)!, "end");
  const selected = [firstTick, lastTick];
  const desiredCount = Math.min(
    points.length,
    maximumLabelCount,
    Math.max(2, Math.floor(plotWidth / targetLabelSpacing) + 1),
  );
  const candidateStep = Math.ceil(
    (points.length - 1) / Math.max(desiredCount - 1, 1),
  );

  for (
    let index = candidateStep;
    index < points.length - 1;
    index += candidateStep
  ) {
    const candidate = buildTick(points[index], "middle");
    if (!selected.some((tick) => ticksOverlap(tick, candidate))) {
      selected.push(candidate);
    }
  }

  return selected.sort((left, right) => left.point.x - right.point.x);
}

function buildChartSegments(
  points: ChartPoint[],
  period: FundamentalMetricSeries["period"],
): ChartSegment[] {
  return points.slice(1).map((end, index) => {
    const start = points[index];
    const gapDays = (end.timestamp - start.timestamp) / millisecondsPerDay;
    return {
      start,
      end,
      gapDays,
      hasMissingPeriod: gapDays > gapThresholdDays[period],
    };
  });
}

export function FinancialTrendChart({
  series,
}: {
  series: FundamentalMetricSeries;
}) {
  const chartContainerRef = useRef<HTMLDivElement>(null);
  const [width, setWidth] = useState(initialWidth);

  useEffect(() => {
    const container = chartContainerRef.current;
    if (!container) {
      return;
    }

    const updateWidth = () => {
      const measuredWidth = Math.round(container.getBoundingClientRect().width);
      setWidth(Math.max(minimumMeasuredWidth, measuredWidth));
    };
    updateWidth();

    const observer = new ResizeObserver(updateWidth);
    observer.observe(container);
    return () => observer.disconnect();
  }, []);

  const values = series.facts.map((fact) => fact.value);
  const rawMinimum = Math.min(...values);
  const rawMaximum = Math.max(...values);
  const rawRange = Math.max(rawMaximum - rawMinimum, Math.abs(rawMaximum) * 0.1, 1);
  const minimum = rawMinimum - rawRange * 0.12;
  const maximum = rawMaximum + rawRange * 0.12;
  const range = maximum - minimum;
  const plotWidth = width - padding.left - padding.right;
  const chronologicalFacts = [...series.facts].sort(
    (left, right) =>
      parseUtcTimestamp(left.period_end) - parseUtcTimestamp(right.period_end),
  );
  const firstTimestamp = parseUtcTimestamp(chronologicalFacts[0].period_end);
  const lastTimestamp = parseUtcTimestamp(
    chronologicalFacts.at(-1)!.period_end,
  );
  const timestampRange = lastTimestamp - firstTimestamp;
  const points: ChartPoint[] = chronologicalFacts.map((fact) => {
    const timestamp = parseUtcTimestamp(fact.period_end);
    const x =
      timestampRange === 0
        ? padding.left + plotWidth / 2
        : padding.left +
          ((timestamp - firstTimestamp) / timestampRange) * plotWidth;
    return {
      fact,
      timestamp,
      x,
      y: padding.top + ((maximum - fact.value) / range) * plotHeight,
    };
  });
  const segments = buildChartSegments(points, series.period);
  const hasMissingPeriod = segments.some((segment) => segment.hasMissingPeriod);
  const ticks = Array.from({ length: 4 }, (_, index) => {
    const ratio = index / 3;
    return {
      value: maximum - ratio * range,
      y: padding.top + ratio * plotHeight,
    };
  });
  const xAxisTicks = selectXAxisTicks(points, plotWidth);
  const labeledPoints = new Map(xAxisTicks.map((tick) => [tick.point, tick]));

  return (
    <figure className="p-3 sm:p-5">
      <div ref={chartContainerRef} className="w-full">
        <svg
          className="block h-[260px] w-full"
          viewBox={`0 0 ${width} ${height}`}
          role="img"
          aria-labelledby="financial-chart-title financial-chart-description"
        >
          <title id="financial-chart-title">
            {`${series.label} ${series.period} trend`}
          </title>
          <desc id="financial-chart-description">
            {`${series.facts.length} qualifying SEC observations from ${series.facts[0].period_end} through ${series.facts.at(-1)?.period_end}. Dashed segments indicate an interval with one or more missing qualifying SEC reporting periods.`}
          </desc>

          {ticks.map((tick) => (
            <g key={tick.y}>
              <line
                x1={padding.left}
                x2={width - padding.right}
                y1={tick.y}
                y2={tick.y}
                stroke="#263140"
                strokeWidth="1"
                vectorEffect="non-scaling-stroke"
              />
              <text
                x={padding.left - 12}
                y={tick.y + 3}
                fill="#96A2B1"
                fontFamily="Cascadia Code, Consolas, monospace"
                fontSize="9"
                textAnchor="end"
              >
                {formatFundamentalValue(tick.value, series.unit)}
              </text>
            </g>
          ))}

          {segments.map((segment) => (
            <path
              key={`${segment.start.fact.period_end}-${segment.end.fact.period_end}`}
              d={`M${segment.start.x},${segment.start.y} L${segment.end.x},${segment.end.y}`}
              fill="none"
              stroke="#32C48D"
              strokeWidth="2.5"
              strokeDasharray={segment.hasMissingPeriod ? "7 6" : undefined}
              strokeLinecap="square"
              strokeLinejoin="round"
              vectorEffect="non-scaling-stroke"
              data-chart-segment="true"
              data-gap-segment={segment.hasMissingPeriod ? "true" : "false"}
              data-gap-days={segment.gapDays}
            >
              {segment.hasMissingPeriod ? (
                <title>
                  {`Dashed segment from ${formatSecDate(segment.start.fact.period_end)} to ${formatSecDate(segment.end.fact.period_end)} indicates missing qualifying SEC reporting periods.`}
                </title>
              ) : null}
            </path>
          ))}
          {points.map((point, index) => {
            const tick = labeledPoints.get(point);
            return (
              <g
                key={`${point.fact.period_end}-${point.fact.accession_number}`}
                data-period-end={point.fact.period_end}
                data-chart-x={point.x}
              >
                <circle
                  cx={point.x}
                  cy={point.y}
                  r={index === points.length - 1 ? 5 : 3}
                  fill="#131C27"
                  stroke="#32C48D"
                  strokeWidth="2"
                  vectorEffect="non-scaling-stroke"
                >
                  <title>
                    {`${formatSecDate(point.fact.period_end)}: ${formatFundamentalValue(point.fact.value, point.fact.unit)}`}
                  </title>
                </circle>
                {tick ? (
                  <text
                    x={point.x}
                    y={height - 12}
                    fill="#96A2B1"
                    fontFamily="Cascadia Code, Consolas, monospace"
                    fontSize={xAxisFontSize}
                    textAnchor={tick.anchor}
                    data-axis-tick="x"
                    data-period-end={point.fact.period_end}
                  >
                    {tick.label}
                  </text>
                ) : null}
              </g>
            );
          })}
        </svg>
      </div>

      {hasMissingPeriod ? (
        <div
          className="mt-2 flex items-center gap-2 font-mono text-[9px] leading-4 text-secondary"
          role="note"
        >
          <svg
            className="h-3 w-8 shrink-0"
            viewBox="0 0 32 12"
            aria-hidden="true"
          >
            <line
              x1="1"
              x2="31"
              y1="6"
              y2="6"
              stroke="#32C48D"
              strokeWidth="2"
              strokeDasharray="6 5"
            />
          </svg>
          <span>
            Dashed segments indicate missing qualifying SEC reporting periods.
          </span>
        </div>
      ) : null}

      <table className="sr-only">
        <caption>{`${series.label} ${series.period} SEC facts`}</caption>
        <thead>
          <tr>
            <th scope="col">Period end</th>
            <th scope="col">Value</th>
          </tr>
        </thead>
        <tbody>
          {series.facts.map((fact) => (
            <tr key={`${fact.period_end}-${fact.accession_number}`}>
              <td>{fact.period_end}</td>
              <td>{formatFundamentalValue(fact.value, fact.unit)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </figure>
  );
}
