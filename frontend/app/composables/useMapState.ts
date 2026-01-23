import { MAP_CONFIG } from "~/constants/mapConfig"

export const useMapState = () => {
    const route = useRoute()

    const mapZoom = useState<number>("mapZoom", () => {
        const z = Number(route.query.z)
        return isNaN(z) ? MAP_CONFIG.defaultZoom : z
    })

    const isUnderZoomThreshold = computed(
        () => mapZoom.value < MAP_CONFIG.zoomThreshold,
    )

    return {
        mapZoom,
        isUnderZoomThreshold,
    }
}
