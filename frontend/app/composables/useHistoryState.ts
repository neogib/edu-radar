import { useMap } from "@indoorequal/vue-maplibre-gl"
import type { Map } from "maplibre-gl"
import { MAP_CONFIG } from "~/constants/mapConfig"
import { getBoundingBoxFromBounds } from "~/utils/bbox"

export const useHistoryState = () => {
    const { loadSchoolsFromBbox, loadSchoolsStreaming } =
        useSchoolGeoJSONSource()
    const mapInstance = useMap(MAP_CONFIG.mapKey)

    const waitForMoveEnd = (map: Map): Promise<void> =>
        new Promise((resolve) => {
            map.once("moveend", resolve)
        })

    const handleHistoryNavigation = async () => {
        // only handle naviagtion to map page
        if (window.location.pathname !== "/map") return

        // map needs to be loaded
        if (!mapInstance.isLoaded) return

        const map = mapInstance.map as Map
        if (!map) return

        const urlParams = new URLSearchParams(window.location.search)
        const x = Number(urlParams.get("x"))
        const y = Number(urlParams.get("y"))
        const z = Number(urlParams.get("z"))

        if (Number.isFinite(x) && Number.isFinite(y) && Number.isFinite(z)) {
            map.easeTo({
                center: [x, y],
                zoom: z,
            })
            if (map.isMoving()) {
                await waitForMoveEnd(map)
            }
        }

        // under threshold we load all schools directly (no bbox split)
        if (map.getZoom() < MAP_CONFIG.zoomThreshold) {
            await loadSchoolsStreaming()
            return
        }

        // first load schools currently visible in bbox
        await loadSchoolsFromBbox()

        // then stream schools outside current bbox
        const bounds = map.getBounds()
        await loadSchoolsStreaming(getBoundingBoxFromBounds(bounds))
    }

    const handlePopState = () => {
        void handleHistoryNavigation()
    }

    onMounted(() => {
        window.addEventListener("popstate", handlePopState)
    })

    onUnmounted(() => {
        window.removeEventListener("popstate", handlePopState)
    })
}
