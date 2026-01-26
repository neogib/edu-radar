import { watchDebounced } from "@vueuse/core"
import { MAP_CONFIG } from "~/constants/mapConfig"
import { useMap } from "@indoorequal/vue-maplibre-gl"
import { GeoJSONSource, type Map } from "maplibre-gl"
import type { BoundingBox } from "~/types/boundingBox"
import { useToast } from "#ui/composables/useToast"

export type LoadSchoolsResult =
    | { status: "success" }
    | { status: "zoom_too_low"; threshold: number }
    | { status: "map_not_loaded" }
    | { status: "aborted" }

export const useSchoolGeoJSONSource = () => {
    // computed filters which update when url changes or user modifies them
    const { filters, filterKey } = useSchoolFilters()
    const route = useRoute()

    const mapInstance = useMap("mainMap")
    const { schoolsGeoJSONFeatures } = useSchools()
    const updateSchoolsFeatures = useSchoolsFeaturesUpdater()
    const toast = useToast()

    const schoolsSource = ref<GeoJSON.FeatureCollection>({
        type: "FeatureCollection",
        features: [],
    })

    // controllers for aborting previous requests
    const { bboxController, streamingController } = useControllers()

    const { isUnderZoomThreshold } = useMapState()

    const startFiltersWatcher = () => {
        watchDebounced(
            filterKey,
            async () => {
                console.log("Filters changed, reloading schools...")
                toast.clear()

                const result = await loadSchoolsFromBbox()

                if (result.status === "zoom_too_low") {
                    toast.add({
                        title: "Mapa jest zbyt oddalona",
                        description: `Przybliż mapę do poziomu ${result.threshold}, aby zobaczyć wyniki filtrowania.`,
                        id: "zoom-threshold-warning", // unique ID to prevent multiples
                        color: "warning",
                        icon: "i-mdi-magnify-plus",
                    })
                }
            },
            { debounce: 300 },
        )
    }
    async function loadSchoolsFromBbox(
        bbox?: BoundingBox,
    ): Promise<LoadSchoolsResult> {
        if (isUnderZoomThreshold.value) {
            return {
                status: "zoom_too_low",
                threshold: MAP_CONFIG.zoomThreshold,
            }
        }

        // abort previous bbox request and create a new controller
        bboxController.value?.abort()
        bboxController.value = new AbortController()
        const signal = bboxController.value.signal

        // bbox load invalidates streaming
        streamingController.value?.abort()

        if (!mapInstance.isLoaded) {
            // initial load
            if (!bbox) {
                // bbox is required on initial load
                return { status: "map_not_loaded" }
            }

            // on initial load of the map fetch from default or voivodeship bbox
            const schools = await schoolsGeoJSONFeatures({
                query: {
                    ...filters.value,
                    ...bbox,
                },
                signal,
            })
            schoolsSource.value = {
                type: "FeatureCollection",
                features: schools,
            }
            return { status: "success" }
        }

        const map = mapInstance.map as Map

        const bounds = map.getBounds()

        // fetch schools within current map bounds
        const schools = await schoolsGeoJSONFeatures({
            query: {
                ...filters.value,
                ...getBoundingBoxFromBounds(bounds),
            },
            signal,
        })

        const source = map.getSource("schools") as GeoJSONSource
        console.log(`source ${source}`)
        if (source) {
            source.setData({
                type: "FeatureCollection",
                features: schools,
            })
        }

        return { status: "success" }
    }

    async function loadSchoolsStreaming(bbox?: BoundingBox) {
        // map needs to be loaded
        if (!mapInstance.isLoaded) {
            return
        }
        console.log(
            "Checking source in loadSchoolsStreaming",
            mapInstance.map?.getSource("schools"),
        )

        // abort previous streaming
        streamingController.value?.abort()
        streamingController.value = new AbortController()
        const signal = streamingController.value.signal

        const map = mapInstance.map as Map
        const source = map.getSource("schools") as GeoJSONSource

        const { x, y, z, ...otherParams } = route.query
        const params = new URLSearchParams()

        Object.entries(otherParams).forEach(([key, value]) => {
            if (Array.isArray(value)) {
                value.forEach((v) => params.append(key, String(v)))
            } else if (value !== undefined && value !== null) {
                params.append(key, String(value))
            }
        })

        if (bbox) {
            Object.entries(bbox).forEach(([key, value]) => {
                params.append(key, value.toString())
            })
            params.append("bbox_mode", "outside")
        } else {
            // clear features if no bbox so that after updates we don't show old data
            await source.updateData(
                {
                    removeAll: true,
                },
                true,
            )
        }
        await updateSchoolsFeatures(params, signal, source)
    }

    return {
        startFiltersWatcher,
        loadSchoolsFromBbox,
        schoolsSource,
        loadSchoolsStreaming,
    }
}
