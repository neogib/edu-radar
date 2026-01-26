import type { LngLatBounds } from "maplibre-gl"
import type { BoundingBox } from "~/types/boundingBox"

/**
 * Utility to construct a BoundingBox from MapLibre's LngLatBounds
 */
export const getBoundingBoxFromBounds = (bounds: LngLatBounds): BoundingBox => {
    return {
        minLng: parseFloat(bounds.getWest().toFixed(6)),
        minLat: parseFloat(bounds.getSouth().toFixed(6)),
        maxLng: parseFloat(bounds.getEast().toFixed(6)),
        maxLat: parseFloat(bounds.getNorth().toFixed(6)),
    }
}
