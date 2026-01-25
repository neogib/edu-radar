import type { LngLatBounds } from "maplibre-gl"
import type { BoundingBox } from "~/types/boundingBox"

/**
 * Utility to construct a BoundingBox from MapLibre's LngLatBounds
 */
export const getBoundingBoxFromBounds = (bounds: LngLatBounds): BoundingBox => {
    return {
        minLng: bounds.getWest(),
        minLat: bounds.getSouth(),
        maxLng: bounds.getEast(),
        maxLat: bounds.getNorth(),
    }
}
