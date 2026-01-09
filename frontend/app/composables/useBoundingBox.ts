import type { LngLatBounds } from "maplibre-gl"
import { MAP_CONFIG } from "~/constants/mapConfig"
import type { BoundingBox } from "~/types/boundingBox"

export const useBoundingBox = () => {
    const route = useRoute()

    /**
     * Parse bbox string from URL parameter
     * @param bboxString - Comma-separated string "minLon,minLat,maxLon,maxLat"
     * @returns BoundingBox object or null if invalid
     */
    const parseBbox = (bboxString: string | null): BoundingBox => {
        if (!bboxString) return MAP_CONFIG.defaultBbox

        try {
            const coords = bboxString.split(",").map(Number)

            if (coords.length !== 4 || coords.some(isNaN)) {
                console.error("Invalid bbox format: must have 4 numeric values")
                return MAP_CONFIG.defaultBbox
            }

            const [minLon, minLat, maxLon, maxLat] = coords as [
                number,
                number,
                number,
                number,
            ]

            // Validate coordinate ranges
            if (
                minLon < -180 ||
                minLon > 180 ||
                maxLon < -180 ||
                maxLon > 180
            ) {
                console.error("Longitude values must be between -180 and 180")
                return MAP_CONFIG.defaultBbox
            }

            if (minLat < -90 || minLat > 90 || maxLat < -90 || maxLat > 90) {
                console.error("Latitude values must be between -90 and 90")
                return MAP_CONFIG.defaultBbox
            }

            // Validate ordering
            if (minLon >= maxLon || minLat >= maxLat) {
                console.error(
                    "Invalid bbox: min values must be less than max values",
                )
                return MAP_CONFIG.defaultBbox
            }

            return {
                minLon: minLon,
                minLat: minLat,
                maxLon: maxLon,
                maxLat: maxLat,
            }
        } catch (error) {
            console.error("Error parsing bbox:", error)
            return MAP_CONFIG.defaultBbox
        }
    }

    // Reactive bbox that automatically updates when URL changes
    const bbox = computed(() => {
        const bboxParam = route.query.bbox as string | undefined
        console.log("Current bbox param:", bboxParam)
        return parseBbox(bboxParam || null)
    })

    // Update bbox in URL
    const updateQueryBboxParam = (bounds: LngLatBounds) => {
        return navigateTo({
            query: {
                ...route.query,
                bbox: `${bounds.getWest()},${bounds.getSouth()},${bounds.getEast()},${bounds.getNorth()}`,
            },
        })
    }

    return {
        bbox,
        updateBbox: updateQueryBboxParam,
    }
}
