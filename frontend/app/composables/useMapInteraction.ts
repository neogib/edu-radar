import type { Point } from "geojson"
import type { LngLat, LngLatBounds } from "maplibre-gl"
import type maplibregl from "maplibre-gl"
import { MAP_CONFIG } from "~/constants/mapConfig"
import type { MapMouseLayerEvent } from "~/types/map"
import type {
    SzkolaPublicWithRelations,
    SzkolaPublicShortFromGeoJsonFeatures,
} from "~/types/schools"

export const useMapInteractions = (
    emit: (event: "point-clicked", school: SzkolaPublicWithRelations) => void,
    popupCoordinates: Ref<[number, number] | undefined>,
) => {
    let currentFeatureCoordinates: string | undefined = undefined
    let debounceTimeout: NodeJS.Timeout | null = null
    const hoveredSchool: Ref<SzkolaPublicShortFromGeoJsonFeatures | null> =
        ref(null)
    const { $api } = useNuxtApp()
    const route = useRoute()

    const { mapZoom, isUnderZoomThreshold } = useMapState()

    const handleMouseMove = (map: maplibregl.Map, e: MapMouseLayerEvent) => {
        const feature_collection = e.features?.[0]
        if (!feature_collection) return

        const pointGeometry = feature_collection.geometry as Point
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
            hoveredSchool.value =
                feature_collection.properties as SzkolaPublicShortFromGeoJsonFeatures

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

    const handleClick = async (e: MapMouseLayerEvent) => {
        const feature_collection = e.features?.[0]
        if (!feature_collection) return

        const schoolFullDetails = await $api<SzkolaPublicWithRelations>(
            `/schools/${feature_collection.properties.id}`,
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
        const source = map.getSource("schools") as maplibregl.GeoJSONSource
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

    const handleMoveEnd = (map: maplibregl.Map) => {
        const { lng, lat } = map.getCenter()
        const zoom = map.getZoom()
        const [minLon, minLat, maxLon, maxLat] = MAP_CONFIG.polandBounds

        // Update local state immediately for snappy UI
        mapZoom.value = zoom

        console.log(`Map zoom: ${zoom}`)

        // if user moved outside of Poland bounds, reset to default center
        if (lng < minLon || lng > maxLon || lat < minLat || lat > maxLat) {
            map.easeTo({
                center: MAP_CONFIG.polandCenter,
            })
            return
        }

        // Clear the previous timeout if it exists
        if (debounceTimeout) {
            clearTimeout(debounceTimeout)
        }

        // Set a new timeout to update the bbox after a delay
        debounceTimeout = setTimeout(() => {
            updateQueryCenterZoom(lng, lat, zoom)
        }, 300) // Wait for 300ms of inactivity before fetching
    }

    const setupMapEventHandlers = (map: maplibregl.Map) => {
        map.on("mousemove", "unclustered-points", (e) =>
            handleMouseMove(map, e),
        )
        map.on("mouseleave", "unclustered-points", () => handleMouseLeave(map))
        map.on("click", "unclustered-points", handleClick)
        map.on("click", "clusters", (e) => handleClusterClick(map, e))
        map.on("mouseenter", "clusters", () => {
            map.getCanvas().style.cursor = "pointer"
        })
        map.on("mouseleave", "clusters", () => {
            map.getCanvas().style.cursor = ""
        })
        map.on("moveend", () => handleMoveEnd(map))
    }

    // Update bbox in URL
    const updateQueryCenterZoom = async (
        x: number,
        y: number,
        zoom: number,
    ) => {
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
    }

    return {
        setupMapEventHandlers,
        hoveredSchool,
        updateQueryBboxParam: updateQueryCenterZoom,
    }
}
