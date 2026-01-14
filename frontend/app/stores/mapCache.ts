import { defineStore } from "pinia"
import type { BoundingBox } from "~/types/boundingBox"
import type { SchoolFilterParams, SzkolaPublicShort } from "~/types/schools"

type QueryCacheEntry = {
    bbox: BoundingBox
    ids: number[]
}

type State = {
    schoolsById: Map<number, SzkolaPublicShort>
    queries: Map<string, QueryCacheEntry[]>
}

export const useMapCacheStore = defineStore("mapCache", {
    state: (): State => ({
        schoolsById: markRaw(new Map()),
        queries: markRaw(new Map()),
    }),

    actions: {
        getFilterHash(filters: SchoolFilterParams): string {
            const { bbox, ...rest } = filters

            const normalized: Record<string, unknown> = {}

            Object.entries(rest).forEach(([key, value]) => {
                if (value === undefined) return

                if (Array.isArray(value)) {
                    normalized[key] = value.length
                        ? [...value].sort((a, b) => a - b)
                        : undefined
                    return
                }

                normalized[key] = value
            })

            return JSON.stringify(
                Object.keys(normalized)
                    .sort()
                    .reduce(
                        (acc, key) => {
                            acc[key] = normalized[key]
                            return acc
                        },
                        {} as Record<string, unknown>,
                    ),
            )
        },

        findReusableQuery(
            filterKey: string,
            requestedBbox: BoundingBox,
        ): QueryCacheEntry | null {
            const entries = this.queries.get(filterKey)
            if (!entries) return null

            for (const entry of entries) {
                if (contains(entry.bbox, requestedBbox)) {
                    return entry
                }
            }
            return null
        },

        getSchoolsFromCache(
            requestedBbox: BoundingBox,
            filters: SchoolFilterParams,
        ): SzkolaPublicShort[] | null {
            const filterKey = this.getFilterHash(filters)

            // Find a reusable cached query
            const cachedEntry = this.findReusableQuery(filterKey, requestedBbox)

            if (!cachedEntry) {
                // cache miss
                return null
            }

            // If found, derive result from cached data
            return cachedEntry.ids
                .map((id) => this.schoolsById.get(id))
                .filter((s): s is SzkolaPublicShort => {
                    if (!s) return false
                    return (
                        s.geolokalizacja_longitude >= requestedBbox.minLon &&
                        s.geolokalizacja_longitude <= requestedBbox.maxLon &&
                        s.geolokalizacja_latitude >= requestedBbox.minLat &&
                        s.geolokalizacja_latitude <= requestedBbox.maxLat
                    )
                })
        },

        addQuery(
            bbox: BoundingBox,
            filters: SchoolFilterParams,
            data: SzkolaPublicShort[],
        ) {
            // 1. Store schools in flat map
            for (const inst of data) {
                this.schoolsById.set(inst.id, markRaw(inst))
            }

            // 2. Add to queries map
            const filterKey = this.getFilterHash(filters)
            if (!this.queries.has(filterKey)) {
                this.queries.set(filterKey, [])
            }

            const entries = this.queries.get(filterKey)!
            entries.push({
                bbox,
                ids: data.map((d) => d.id),
            })

            // 3. Merge overlapping/contiguous bboxes for this filterKey
            this.queries.set(filterKey, mergeQueryEntries(entries))
        },
    },
})

// --- Bounding Box Merging Logic ---
// todo, round coordinates to fixed precision to avoid floating point issues

function shareFullEdge(a: BoundingBox, b: BoundingBox): boolean {
    const sameLatRange = a.minLat === b.minLat && a.maxLat === b.maxLat
    const touchHorizontally = a.maxLon === b.minLon || b.maxLon === a.minLon

    const sameLonRange = a.minLon === b.minLon && a.maxLon === b.maxLon
    const touchVertically = a.maxLat === b.minLat || b.maxLat === a.minLat

    return (
        (sameLatRange && touchHorizontally) || (sameLonRange && touchVertically)
    )
}

function contains(outer: BoundingBox, inner: BoundingBox): boolean {
    return (
        outer.minLat <= inner.minLat &&
        outer.maxLat >= inner.maxLat &&
        outer.minLon <= inner.minLon &&
        outer.maxLon >= inner.maxLon
    )
}

function shouldMergeStrict(a: BoundingBox, b: BoundingBox): boolean {
    return shareFullEdge(a, b) || contains(a, b) || contains(b, a)
}

function mergeBboxes(a: BoundingBox, b: BoundingBox): BoundingBox {
    return {
        minLat: Math.min(a.minLat, b.minLat),
        maxLat: Math.max(a.maxLat, b.maxLat),
        minLon: Math.min(a.minLon, b.minLon),
        maxLon: Math.max(a.maxLon, b.maxLon),
    }
}

function mergeQueryEntries(entries: QueryCacheEntry[]): QueryCacheEntry[] {
    if (entries.length === 0) return []

    let result = [...entries]
    let merged = true

    while (merged) {
        merged = false

        outer: for (let i = 0; i < result.length; i++) {
            for (let j = i + 1; j < result.length; j++) {
                if (shouldMergeStrict(result[i].bbox, result[j].bbox)) {
                    // Merge BBoxes
                    const newBbox = mergeBboxes(result[i].bbox, result[j].bbox)

                    // Merge IDs (Set for uniqueness)
                    const combinedIds = Array.from(
                        new Set([...result[i].ids, ...result[j].ids]),
                    )

                    // Replace i
                    result[i] = {
                        bbox: newBbox,
                        ids: combinedIds,
                    }

                    // Remove j
                    result.splice(j, 1)

                    merged = true
                    break outer
                }
            }
        }
    }

    return result
}
