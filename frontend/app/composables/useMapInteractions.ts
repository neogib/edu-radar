import { useDebounceFn } from "@vueuse/core"
import type { GeoJSONFeature } from "maplibre-gl"
import type maplibregl from "maplibre-gl"
import { MAP_CONFIG } from "~/constants/mapConfig"
import type { MapMouseLayerEvent } from "~/types/map"
import type {
    SzkolaPublicWithRelations,
    SchoolFeatureProperties,
    SchoolFeature,
} from "~/types/schools"

export const useMapInteractions = (
    emit: (event: "point-clicked", school: SzkolaPublicWithRelations) => void,
    popupCoordinates: Ref<[number, number] | undefined>,
) => {
    let currentFeatureCoordinates: string | undefined = undefined
    const hoveredSchool: Ref<SchoolFeatureProperties | null> = ref(null)
    const { $api } = useNuxtApp()
    const route = useRoute()

    // Track hovered feature IDs for feature-state
    let hoveredClusterId: number | null = null
    let selectedSchoolId: number | null = null

    const [minLon, minLat, maxLon, maxLat] = MAP_CONFIG.polandBounds

    const inPoland = (lng: number, lat: number) =>
        lng >= minLon && lng <= maxLon && lat >= minLat && lat <= maxLat

    const setupMapEventHandlers = (map: maplibregl.Map) => {
        // Map move end to update URL
        map.on("moveend", () => handleMoveEnd(map))

        // Unclustered point hover and click
        map.on("mousemove", "unclustered-points", (e) =>
            handleMouseMove(map, e),
        )
        map.on("mouseleave", "unclustered-points", () => handleMouseLeave(map))
        map.on("click", "unclustered-points", (e) => handleClick(map, e))

        // Cluster click to zoom in
        map.on("click", "clusters", (e) => handleClusterClick(map, e))

        // Cluster hover effect
        map.on("mousemove", "clusters", (e) => {
            if (e.features && e.features.length > 0) {
                if (hoveredClusterId !== null) {
                    map.setFeatureState(
                        { source: MAP_CONFIG.sourceId, id: hoveredClusterId },
                        { hover: false },
                    )
                }
                hoveredClusterId = (e.features[0] as GeoJSONFeature)
                    .id as number
                map.setFeatureState(
                    { source: MAP_CONFIG.sourceId, id: hoveredClusterId },
                    { hover: true },
                )
            }
        })
        map.on("mouseleave", "clusters", () => {
            map.getCanvas().style.cursor = ""
            if (hoveredClusterId !== null) {
                map.setFeatureState(
                    { source: MAP_CONFIG.sourceId, id: hoveredClusterId },
                    { hover: false },
                )
                hoveredClusterId = null
            }
        })
        map.on("mouseenter", "clusters", () => {
            map.getCanvas().style.cursor = "pointer"
        })
    }

    const handleMoveEnd = (map: maplibregl.Map) => {
        const { lng, lat } = map.getCenter()
        const zoom = map.getZoom()

        // Check if selected school is now clustered
        if (selectedSchoolId !== null) {
            const features = map.querySourceFeatures(MAP_CONFIG.sourceId, {
                filter: ["==", ["get", "id"], selectedSchoolId],
            })

            // Toggle visibility: if features.length === 0, school is clustered or out of view
            const visibility = features.length > 0 ? "visible" : "none"

            map.setLayoutProperty("selected-point", "visibility", visibility)
            map.setLayoutProperty(
                "selected-point-border",
                "visibility",
                visibility,
            )
        }

        updateQueryCenterZoomDebounced(lng, lat, zoom, map)
    }

    const handleMouseMove = (map: maplibregl.Map, e: MapMouseLayerEvent) => {
        const feature = e.features?.[0] as SchoolFeature | undefined
        if (!feature) return

        const pointGeometry = feature.geometry
        const featureCoordinates = pointGeometry.coordinates.toString()
        if (currentFeatureCoordinates !== featureCoordinates) {
            currentFeatureCoordinates = featureCoordinates

            // Change the cursor style as a UI indicator.
            map.getCanvas().style.cursor = "pointer"

            const coordinates = pointGeometry.coordinates.slice() as [
                number,
                number,
            ]
            // Update the hovered school data
            hoveredSchool.value = feature.properties

            // Ensure that if the map is zoomed out such that multiple
            // copies of the feature are visible, the popup appears
            // over the copy being pointed to.
            while (Math.abs(e.lngLat.lng - coordinates[0]) > 180) {
                coordinates[0] += e.lngLat.lng > coordinates[0] ? 360 : -360
            }

            // Use the MglPopup component instead of native popup
            popupCoordinates.value = coordinates
        }
    }

    const handleMouseLeave = (map: maplibregl.Map) => {
        currentFeatureCoordinates = undefined
        map.getCanvas().style.cursor = ""
        popupCoordinates.value = undefined
        hoveredSchool.value = null
    }

    const handleClick = async (map: maplibregl.Map, e: MapMouseLayerEvent) => {
        const feature = e.features?.[0]
        if (!feature) return
        if (feature.geometry.type !== "Point") return

        // MapLibre click features are runtime objects; create plain GeoJSON
        // before passing data to sources to avoid serialization issues.
        const selectedFeature: SchoolFeature = {
            type: "Feature",
            properties: {
                id: Number(feature.properties.id),
                nazwa: feature.properties.nazwa,
                typ: feature.properties.typ,
                status: feature.properties.status,
                wynik: feature.properties.wynik,
            },
            geometry: {
                type: "Point",
                coordinates: [
                    Number(feature.geometry.coordinates[0]),
                    Number(feature.geometry.coordinates[1]),
                ],
            },
        }

        // update the selected point source
        const selectedPointSource = map.getSource("selected-point") as
            | maplibregl.GeoJSONSource
            | undefined
        if (selectedPointSource) {
            selectedPointSource.setData({
                type: "FeatureCollection",
                features: [selectedFeature],
            })
            selectedSchoolId = Number(feature.properties.id)
        }

        // Fetch full school details and emit event
        const schoolFullDetails = await $api<SzkolaPublicWithRelations>(
            `/schools/${feature.properties.id}`,
        )

        if (schoolFullDetails) {
            emit("point-clicked", schoolFullDetails)
        }
    }

    const handleClusterClick = async (
        map: maplibregl.Map,
        e: MapMouseLayerEvent,
    ) => {
        const features = map.queryRenderedFeatures(e.point, {
            layers: ["clusters"],
        })
        const firstFeature = features[0]
        if (
            !firstFeature ||
            !firstFeature.properties?.cluster_id ||
            firstFeature.geometry.type !== "Point"
        )
            return

        const clusterId = firstFeature.properties.cluster_id
        const source = map.getSource(
            MAP_CONFIG.sourceId,
        ) as maplibregl.GeoJSONSource
        const zoom = await source.getClusterExpansionZoom(clusterId)
        map.easeTo({
            center: (firstFeature.geometry as Point).coordinates as [
                number,
                number,
            ],
            zoom,
            duration: 150,
        })
    }

    // Update bbox in URL
    const updateQueryCenterZoomDebounced = useDebounceFn(
        async (x: number, y: number, zoom: number, map: maplibregl.Map) => {
            // if user moved outside of Poland bounds, reset to default center
            if (!inPoland(x, y)) {
                map.easeTo({
                    center: MAP_CONFIG.polandCenter,
                })
                return
            }
            // only handle naviagtion to map page
            // sometimes debounced function is called after leaving the page
            if (window.location.pathname !== "/map") return
            await navigateTo(
                {
                    query: {
                        ...route.query,
                        x: x.toFixed(6),
                        y: y.toFixed(6),
                        z: zoom.toFixed(2),
                    },
                },
                { replace: true },
            )
        },
        300,
    )

    return {
        setupMapEventHandlers,
        hoveredSchool,
    }
}
