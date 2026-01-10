import { defineStore } from "pinia"
import type { BoundingBox } from "~/types/boundingBox"
import type { SzkolaPublicShort } from "~/types/schools"

type State = {
    schools: Map<number, SzkolaPublicShort>
    fetchedAreas: BoundingBox[]
}

export const useMapCacheStore = defineStore("mapCache", {
    state: (): State => ({
        schools: new Map(),
        fetchedAreas: [],
    }),

    actions: {
        isCovered(viewport: BoundingBox): boolean {
            return this.fetchedAreas.some(
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

        addFetchedArea(viewport: BoundingBox) {
            this.fetchedAreas.push(viewport)
            this.fetchedAreas = mergeBoundingBoxes(this.fetchedAreas)
        },

        getCachedSchools(
            viewport: BoundingBox,
            filters: Record<string, any> = {},
        ) {
            return Array.from(this.schools.values()).filter(
                (inst) =>
                    inst.geolokalizacja_latitude >= viewport.minLat &&
                    inst.geolokalizacja_latitude <= viewport.maxLat &&
                    inst.geolokalizacja_longitude >= viewport.minLon &&
                    inst.geolokalizacja_longitude <= viewport.maxLon &&
                    Object.entries(filters).every(
                        ([k, v]) => v == null || inst[k] === v,
                    ),
            )
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
