import { useDebounceFn, watchDebounced } from "@vueuse/core"
import { MAP_CONFIG } from "~/constants/mapConfig"
import { useMap } from "@indoorequal/vue-maplibre-gl"
import { GeoJSONSource, type Map } from "maplibre-gl"
import type { BoundingBox } from "~/types/boundingBox"
import { useToast } from "#ui/composables/useToast"

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
        watch(filterKey, async () => {
            // this logic is to prevent only schools from bbox appearing on the map after user chnages filters and immediately closes them
            // it only happens when zoom is higher than threshold and user changes filters quickly

            toast.clear()
            if (isUnderZoomThreshold.value) {
                // if under zoom threshold, no need to abort anything, just show the message
                toast.add({
                    title: "Mapa jest zbyt oddalona",
                    description: `Przybliż mapę do poziomu ${MAP_CONFIG.zoomThreshold}, aby zobaczyć wyniki filtrowania.`,
                    id: "zoom-threshold-warning", // unique ID to prevent multiples
                    color: "warning",
                    icon: "i-mdi-magnify-plus",
                    duration: 2000,
                })
                return
            }
            // first abort previous streaming
            streamingController.value?.abort()

            // then clear the map
            const map = mapInstance.map as Map
            const source = map.getSource("schools") as GeoJSONSource
            if (source) {
                source.setData({
                    type: "FeatureCollection",
                    features: [],
                })
            }

            // now we can safely reload schools with debounce
            // and schools already streamed for new filters won't be interrupted
            deobounceReload()
        })
    }
    const deobounceReload = useDebounceFn(
        async () => {
            console.log("Filters changed, reloading schools...")

            await loadSchoolsFromBbox()
        },
        300,
        { maxWait: 1000 },
    )

    async function loadSchoolsFromBbox(bbox?: BoundingBox) {
        // abort previous bbox request and create a new controller
        bboxController.value?.abort()
        bboxController.value = new AbortController()
        const signal = bboxController.value.signal

        if (!mapInstance.isLoaded) {
            // initial load
            if (!bbox) {
                // bbox is required on initial load
                return
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
            return
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
        await source.updateData(
            {
                add: schools,
            },
            true,
        )
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
