import type { LngLatBounds } from "maplibre-gl"
import type { BoundingBox } from "~/types/boundingBox"

export const useBoundingBox = () => {
    const route = useRoute()

    /**
     * Parse bbox string from URL parameter
     * @param bboxString - Comma-separated string "minLon,minLat,maxLon,maxLat"
     * @returns BoundingBox object or null if invalid
     */
    const parseBbox = (bboxString: string | null): BoundingBox | null => {
        if (!bboxString) return null

        try {
            const coords = bboxString.split(",").map(Number)

            if (coords.length !== 4 || coords.some(isNaN)) {
                console.error("Invalid bbox format: must have 4 numeric values")
                return null
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
                return null
            }

            if (minLat < -90 || minLat > 90 || maxLat < -90 || maxLat > 90) {
                console.error("Latitude values must be between -90 and 90")
                return null
            }

            // Validate ordering
            if (minLon >= maxLon || minLat >= maxLat) {
                console.error(
                    "Invalid bbox: min values must be less than max values",
                )
                return null
            }

            return {
                minLon: minLon,
                minLat: minLat,
                maxLon: maxLon,
                maxLat: maxLat,
            }
        } catch (error) {
            console.error("Error parsing bbox:", error)
            return null
        }
    }

    // Get bbox from URL as parsed object
    const bboxParam = route.query.bbox as string | undefined
    const bbox: BoundingBox | null = parseBbox(bboxParam || null)

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
