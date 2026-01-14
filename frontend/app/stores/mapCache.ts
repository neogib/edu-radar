import { defineStore } from "pinia"
import type { BoundingBox } from "~/types/boundingBox"
import type { SchoolFilterParams, SzkolaPublicShort } from "~/types/schools"

type State = {
    schools: Map<number, SzkolaPublicShort>
    fetchedAreas: Record<string, BoundingBox[]>
}

export const useMapCacheStore = defineStore("mapCache", {
    state: (): State => ({
        schools: new Map(),
        fetchedAreas: {},
    }),

    actions: {
        getFilterHash(filters: Record<string, any>): string {
            // Create a stable hash key from filters
            // 1. Remove non-filter keys like 'bbox'
            // 2. Sort keys
            // 3. Stringify
            const cleanFilters = { ...filters }
            delete cleanFilters.bbox

            console.log(`Clean Filters:`, cleanFilters)
            if (Object.keys(cleanFilters).length === 0) {
                return "{}"
            }

            // Remove null/undefined/empty values to normalize
            Object.keys(cleanFilters).forEach((key) => {
                if (
                    cleanFilters[key] === undefined ||
                    cleanFilters[key] === null ||
                    cleanFilters[key] === ""
                ) {
                    delete cleanFilters[key]
                }
            })

            const sortedKeys = Object.keys(cleanFilters).sort()
            const sortedObj: Record<string, any> = {}
            for (const key of sortedKeys) {
                sortedObj[key] = cleanFilters[key]
            }
            console.log(`Sorted Filters for Hash:`, sortedObj)
            console.log(JSON.stringify(sortedObj))
            return JSON.stringify(sortedObj)
        },

        isCovered(
            viewport: BoundingBox,
            filters: Record<string, any>,
        ): boolean {
            const currentHash = this.getFilterHash(filters)
            const emptyHash = "{}" // Hash for no filters (all schools)

            // Check if covered by current specific filters
            const specificCoverage = this.checkCoverageForHash(
                viewport,
                currentHash,
            )
            console.log(
                `Coverage Check for Hash ${currentHash}: ${specificCoverage}`,
            )
            if (specificCoverage) return true

            // Optimization: If we have fetched "All Schools" (empty filters) for this area,
            // we implicitly have the data for ANY filter subset.
            // Note: This assumes the API returns ALL fields necessary for local filtering.
            if (currentHash !== emptyHash) {
                const allDataCoverage = this.checkCoverageForHash(
                    viewport,
                    emptyHash,
                )
                console.log(
                    `Coverage Check for All Schools Hash: ${allDataCoverage}`,
                )
                if (allDataCoverage) return true
            }

            return false
        },

        checkCoverageForHash(viewport: BoundingBox, hash: string): boolean {
            const areas = this.fetchedAreas[hash] || []
            return areas.some(
                (area) =>
                    area.minLat <= viewport.minLat &&
                    area.minLon <= viewport.minLon &&
                    area.maxLat >= viewport.maxLat &&
                    area.maxLon >= viewport.maxLon,
            )
        },

        addSchools(data: SzkolaPublicShort[]) {
            // Build new Map from existing + new data
            const newSchools = new Map(this.schools)
            for (const inst of data) {
                newSchools.set(inst.id, markRaw(inst))
            }

            // Single reactive update
            this.schools = newSchools
        },

        addFetchedArea(viewport: BoundingBox, filters: Record<string, any>) {
            const hash = this.getFilterHash(filters)
            if (!this.fetchedAreas[hash]) {
                this.fetchedAreas[hash] = []
            }
            this.fetchedAreas[hash]!.push(viewport)
            this.fetchedAreas[hash] = mergeBoundingBoxes(
                this.fetchedAreas[hash]!,
            )
        },

        getCachedSchools(viewport: BoundingBox, filters: Record<string, any>) {
            return Array.from(this.schools.values()).filter((inst) => {
                // 1. Geoloc Check
                if (
                    inst.geolokalizacja_latitude < viewport.minLat ||
                    inst.geolokalizacja_latitude > viewport.maxLat ||
                    inst.geolokalizacja_longitude < viewport.minLon ||
                    inst.geolokalizacja_longitude > viewport.maxLon
                ) {
                    return false
                }

                // 2. Client-side Filtering matching Backend Logic
                // We must match the filters passed in 'filters' (from route.query)

                // check is filters empty or consists only of bbox
                const { bbox, ...rest } = filters

                if (Object.keys(rest).length === 0) {
                    return true
                }

                if (
                    filters.type &&
                    !filters.type?.includes(inst.typ.id.toString())
                ) {
                    console.log(`Type Filter: ${filters.type}`)
                    return false
                }

                if (
                    filters.status &&
                    !filters.status?.includes(
                        inst.status_publicznoprawny.id.toString(),
                    )
                ) {
                    console.log(
                        `Status Filter: ${filters.status}, ${typeof filters.status}, ${typeof filters.status[0]}`,
                    )
                    return false
                }

                if (
                    filters.category &&
                    !filters.category?.includes(
                        inst.kategoria_uczniow.id.toString(),
                    )
                ) {
                    console.log(`Category Filter: ${filters.category}`)
                    return false
                }

                if (filters.vocational_training) {
                    console.log(
                        `Vocational Training Filter: ${filters.vocational_training}`,
                    )
                    const hasVocationalTraining =
                        inst.ksztalcenie_zawodowe.some((vt) =>
                            filters.vocational_training?.includes(
                                vt.id.toString(),
                            ),
                        )
                    if (!hasVocationalTraining) {
                        return false
                    }
                }

                const hasScoreFilter =
                    filters.min_score !== undefined ||
                    filters.max_score !== undefined

                if (hasScoreFilter) {
                    if (inst.score == null) return false

                    if (filters.min_score && inst.score < filters.min_score) {
                        return false
                    }

                    if (filters.max_score && inst.score > filters.max_score) {
                        return false
                    }
                }

                return true
            })
        },
    },
})

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

function mergeTwo(a: BoundingBox, b: BoundingBox): BoundingBox {
    return {
        minLat: Math.min(a.minLat, b.minLat),
        maxLat: Math.max(a.maxLat, b.maxLat),
        minLon: Math.min(a.minLon, b.minLon),
        maxLon: Math.max(a.maxLon, b.maxLon),
    }
}

function mergeBoundingBoxes(boxes: BoundingBox[]): BoundingBox[] {
    if (boxes.length === 0) return []

    // Copy input array to avoid mutating the original
    let result = [...boxes]
    let merged = true

    // Keep looping until no more merges are possible
    while (merged) {
        merged = false

        outer: for (let i = 0; i < result.length; i++) {
            // Check against all subsequent boxes
            for (let j = i + 1; j < result.length; j++) {
                if (shouldMergeStrict(result[i]!, result[j]!)) {
                    const combined = mergeTwo(result[i]!, result[j]!)

                    // Replace the 'i' box with the merged one
                    result[i] = combined

                    // Remove the 'j' box
                    result.splice(j, 1)

                    merged = true
                    break outer
                }
            }
        }
    }

    return result
}
