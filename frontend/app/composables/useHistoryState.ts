import { useMap } from "@indoorequal/vue-maplibre-gl"
export const useHistoryState = () => {
    const { debouncedLoadRemainingSchools } = useSchoolGeoJSONSource()
    const mapInstance = useMap("mainMap")
    const handleHistoryNavigation = () => {
        // only handle naviagtion to map page
        console.log("handling history navigation", window.location.pathname)
        if (window.location.pathname !== "/map") return

        // map needs to be loaded
        if (!mapInstance.isLoaded) return

        const map = mapInstance.map

        const urlParams = new URLSearchParams(window.location.search)
        const x = urlParams.get("x")
        const y = urlParams.get("y")
        const z = urlParams.get("z")

        if (x && y && z) {
            map?.easeTo({
                center: [Number(x), Number(y)],
                zoom: Number(z),
            })
        }

        debouncedLoadRemainingSchools()
    }

    onMounted(() => {
        window.addEventListener("popstate", handleHistoryNavigation)
    })

    onBeforeUnmount(() => {
        console.log("unmounted mapview")
        window.removeEventListener("popstate", handleHistoryNavigation)
    })
}
