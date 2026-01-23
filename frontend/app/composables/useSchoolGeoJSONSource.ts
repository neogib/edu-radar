import { watchDebounced } from "@vueuse/core"
import { MAP_CONFIG } from "~/constants/mapConfig"
import { useMap } from "@indoorequal/vue-maplibre-gl"
import type { GeoJSONSource, Map } from "maplibre-gl"
import type { BoundingBox } from "~/types/boundingBox"
import { useToast } from "#ui/composables/useToast"

export type LoadSchoolsResult =
    | { status: "success" }
    | { status: "zoom_too_low"; threshold: number }
    | { status: "map_not_loaded" }
    | { status: "aborted" }

export const useSchoolGeoJSONSource = () => {
    // computed filters which update when url changes or user modifies them
    const { filters } = useSchoolFilters()
    const route = useRoute()

    const map = useMap("mainMap")
    const { schoolsGeoJSONFeatures } = useSchools()
    const updateSchoolsFeatures = useSchoolsFeaturesUpdater()
    const toast = useToast()

    const schoolsSource = shallowRef<GeoJSON.FeatureCollection>({
        type: "FeatureCollection",
        features: [],
    })

    const { isUnderZoomThreshold } = useMapState()

    const startFiltersWatcher = () => {
        watchDebounced(
            filters,
            async () => {
                // controller used for aborting previous requests
                const controller = new AbortController()

                const result = await loadSchoolsFromBbox(
                    undefined,
                    controller.signal,
                )

                if (result.status === "zoom_too_low") {
                    toast.add({
                        title: "Mapa jest zbyt oddalona",
                        description: `Przybliż mapę do poziomu ${result.threshold}, aby zobaczyć wyniki filtrowania.`,
                        id: "zoom-threshold-warning", // unique ID to prevent multiples
                        color: "warning",
                        icon: "i-mdi-magnify-plus",
                    })
                }

                onWatcherCleanup(() => controller.abort())
            },
            { debounce: 300 },
        )
    }
    async function loadSchoolsFromBbox(
        bbox?: BoundingBox,
        signal?: AbortSignal,
    ): Promise<LoadSchoolsResult> {
        if (!map.isLoaded) {
            if (!bbox) {
                return { status: "map_not_loaded" }
            }

            // on initial load of the map fetch from default or voivodeship bbox
            const schools = await schoolsGeoJSONFeatures({
                query: {
                    ...filters.value,
                    ...bbox,
                },
            })
            schoolsSource.value = {
                type: "FeatureCollection",
                features: schools,
            }
            return { status: "success" }
        }

        const loadedMap = map.map as Map

        if (isUnderZoomThreshold.value) {
            return {
                status: "zoom_too_low",
                threshold: MAP_CONFIG.zoomThreshold,
            }
        }

        const bounds = loadedMap.getBounds()

        // fetch schools within current map bounds
        const schools = await schoolsGeoJSONFeatures({
            query: {
                ...filters.value,
                min_lng: bounds.getWest(),
                min_lat: bounds.getSouth(),
                max_lng: bounds.getEast(),
                max_lat: bounds.getNorth(),
            },
            signal,
        })

        schoolsSource.value = {
            type: "FeatureCollection",
            features: schools,
        }

        const source = loadedMap.getSource("schools") as GeoJSONSource
        if (source) {
            source.setData(schoolsSource.value)
        }

        return { status: "success" }
    }

    async function loadSchoolsStreaming(
        bbox?: BoundingBox,
        signal?: AbortSignal,
    ) {
        // map needs to be loaded
        if (!map.isLoaded) {
            return
        }

        const loadedMap = map.map as Map
        const { x, y, z, ...otherParams } = route.query
        const params = new URLSearchParams(otherParams as any)

        if (bbox) {
            Object.entries(bbox).forEach(([key, value]) => {
                params.append(key, value.toString())
            })
            params.append("bbox_mode", "outside")
        }
        console.log(`source : ${loadedMap.getSource("schools")}`)
        await updateSchoolsFeatures(params, loadedMap, "schools")
    }

    return {
        startFiltersWatcher,
        loadSchoolsFromBbox,
        schoolsSource,
        loadSchoolsStreaming,
    }
}
