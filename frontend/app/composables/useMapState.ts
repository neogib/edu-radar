import { MAP_CONFIG } from "~/constants/mapConfig"

export const useMapState = () => {
    const route = useRoute()

    const isUnderZoomThreshold = computed(() => {
        const z = Number(route.query.z)
        const currentZoom = isNaN(z) ? MAP_CONFIG.defaultZoom : z
        return currentZoom < MAP_CONFIG.zoomThreshold
    })

    return {
        isUnderZoomThreshold,
    }
}
