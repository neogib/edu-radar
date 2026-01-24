import { MAP_CONFIG } from "~/constants/mapConfig"
import type { BoundingBox } from "~/types/boundingBox"

export const parseArrayOfIds = (
    v: string | (string | null)[] | null | undefined,
): number[] | undefined => {
    if (!v) return undefined
    const arr = (Array.isArray(v) ? v : [v])
        .filter((i): i is string => i !== null)
        .map(Number)
        .filter((n) => Number.isFinite(n) && n > 0)
        .sort((a, b) => a - b)
    return arr.length ? arr : undefined
}

export const parseNumber = (
    v: string | (string | null)[] | null | undefined,
): number | undefined => {
    if (!v) return undefined
    const val = Array.isArray(v) ? v[0] : v
    if (val === null) return undefined
    const n = Number(val)
    return Number.isFinite(n) ? n : undefined
}

export const parseQueryString = (
    v: string | (string | null)[] | null | undefined,
): string | undefined => {
    if (!v) return undefined
    const s = String(Array.isArray(v) ? v[0] : v)
    return s.trim().length >= 2 ? s.trim() : undefined
}
