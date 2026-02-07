import type { ExpressionSpecification } from "maplibre-gl"

export const NULL_SCORE_COLOR = "#87CEFA"

export const SCORE_COLOR_STOPS = [
    [0, "#7A0000"],
    [25, "#FF5A36"],
    [50, "#FFD400"],
    [75, "#66D96B"],
    [100, "#007A1A"],
] as const

const colorStopsForExpression = SCORE_COLOR_STOPS.flatMap(([stop, color]) => [
    stop,
    color,
])

export const createScoreColorInterpolation = (
    inputExpression: ExpressionSpecification,
): ExpressionSpecification => [
    "interpolate",
    ["linear"],
    inputExpression,
    ...colorStopsForExpression,
]

export const getScoreColor = (score: number | null | undefined): string => {
    if (score === null || score === undefined) {
        return NULL_SCORE_COLOR
    }

    const firstStop = SCORE_COLOR_STOPS[0]!
    const lastStop = SCORE_COLOR_STOPS[SCORE_COLOR_STOPS.length - 1]!

    // handle min/max values
    if (score == firstStop[0]) return firstStop[1]
    if (score == lastStop[0]) return lastStop[1]

    for (let i = 0; i < SCORE_COLOR_STOPS.length - 1; i++) {
        const [startStop, startColor] = SCORE_COLOR_STOPS[i]!
        const [endStop, endColor] = SCORE_COLOR_STOPS[i + 1]!

        if (score <= endStop) {
            const ratio = (score - startStop) / (endStop - startStop)
            const startRgb = hexToRgb(startColor)
            const endRgb = hexToRgb(endColor)

            const r = interpolateChannel(startRgb.r, endRgb.r, ratio)
            const g = interpolateChannel(startRgb.g, endRgb.g, ratio)
            const b = interpolateChannel(startRgb.b, endRgb.b, ratio)

            return `rgb(${r}, ${g}, ${b})`
        }
    }

    return lastStop[1]
}

const hexToRgb = (hexColor: string): { r: number; g: number; b: number } => {
    const normalized = hexColor.replace("#", "")
    const value = Number.parseInt(normalized, 16)

    return {
        r: (value >> 16) & 255,
        g: (value >> 8) & 255,
        b: value & 255,
    }
}

const interpolateChannel = (start: number, end: number, ratio: number) =>
    Math.round(start + (end - start) * ratio)
