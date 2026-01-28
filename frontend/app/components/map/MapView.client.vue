<script setup lang="ts">
import type { MapSourceDataEvent } from "maplibre-gl"
import { useSchoolGeoJSONSource } from "~/composables/useSchoolGeoJSONSource"
import { MAP_CONFIG, ICON_URLS } from "~/constants/mapConfig"
import type { SzkolaPublicWithRelations } from "~/types/schools"

useHistoryState()
const route = useRoute()
const [x, y, z] = [
    Number(route.query.x),
    Number(route.query.y),
    Number(route.query.z),
]
const emit = defineEmits<{
    "point-clicked": [school: SzkolaPublicWithRelations]
}>()

const popupCoordinates: Ref<[number, number] | undefined> = ref(undefined)
const { setupMapEventHandlers, hoveredSchool } = useMapInteractions(
    emit,
    popupCoordinates,
)

// for map data loading
const initialBbox = useInitialBbox()
const { isUnderZoomThreshold } = useMapState()
const { startFiltersWatcher, loadSchoolsFromBbox, loadSchoolsStreaming } =
    useSchoolGeoJSONSource()

const onMapLoaded = async (event: { map: maplibregl.Map }) => {
    const map = event.map
    setupMapEventHandlers(map)
    startFiltersWatcher()

    // wait for source to be ready
    // sourcedata event will be fired when schools source loads
    map.once("sourcedata", async (e: MapSourceDataEvent) => {
        if (e.sourceId === MAP_CONFIG.sourceId) {
            await initializeWithSource(map)
        }
    })
}

const initializeWithSource = async (map: maplibregl.Map) => {
    if (initialBbox.value) {
        // when there is an initial bbox, on map load we need to only get schools outside this bbox becaues schools inside bbox are already loaded
        await loadSchoolsStreaming(initialBbox.value)
        return
    }
    if (isUnderZoomThreshold.value) {
        // if under zoom threshold, just load all schools via streaming
        // no need to load by bbox first
        await loadSchoolsStreaming()
        return
    }

    // no initial bbox, load schools for current map bounds when zoom is greater than threshold
    await loadSchoolsFromBbox()

    // then load schools outside current bounds via streaming
    const bbox = getBoundingBoxFromBounds(map.getBounds())
    await loadSchoolsStreaming(bbox)
}
</script>

<template>
    <MglMap
        :map-key="MAP_CONFIG.mapKey"
        :map-style="MAP_CONFIG.style"
        :center="[x, y]"
        :zoom="z"
        :fade-duration="0"
        :min-zoom="MAP_CONFIG.minZoom"
        :max-zoom="MAP_CONFIG.maxZoom"
        @map:load="onMapLoaded">
        <MglNavigationControl position="bottom-right" />
        <MglFullscreenControl position="bottom-right" />
        <MglGeolocateControl
            position="bottom-right"
            :positionOptions="{ enableHighAccuracy: true }"
            :trackUserLocation="true" />

        <MglImage
            v-for="iconUrl in ICON_URLS"
            :id="`${iconUrl.split('/').pop()?.split('.').shift()}_sdf`"
            :key="iconUrl"
            :url="iconUrl"
            :options="{ sdf: true }" />

        <MglPopup
            v-if="hoveredSchool"
            :close-button="false"
            :close-on-click="false"
            :coordinates="popupCoordinates">
            <!-- Status Publicznoprawny - Top -->
            <div
                class="bg-linear-to-r rounded-lg from-blue-50 to-indigo-50 px-2 py-1 border-b border-gray-100">
                <span class="px-2 py-1 text-xs text-blue-800">
                    {{ hoveredSchool.status }}
                </span>
            </div>

            <!-- School Name - Middle -->
            <div class="px-2 py-2">
                <h4
                    class="font-semibold text-xs text-gray-900 leading-tight mb-2">
                    {{ hoveredSchool.nazwa }}
                </h4>

                <!-- School Type - Bottom -->
                <div
                    class="bg-gray-50 rounded-lg px-2 py-2 border border-gray-100">
                    <span class="text-xs text-gray-900 font-semibold">
                        {{ hoveredSchool.typ }}
                    </span>
                </div>
            </div>
        </MglPopup>

        <MapSchoolLayers />
    </MglMap>
</template>
