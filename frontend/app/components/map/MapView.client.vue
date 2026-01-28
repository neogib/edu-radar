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

const statusIcon = computed(() => {
    if (!hoveredSchool.value) return "i-mdi-shield-check"
    if (hoveredSchool.value.status === "publiczna") return "i-mdi-earth"
    if (hoveredSchool.value.status === "niepubliczna")
        return "i-material-symbols-public-off"
    return "i-mdi-shield-check"
})

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
            :offset="20"
            :coordinates="popupCoordinates">
            <div
                class="min-w-55 max-w-70 overflow-hidden rounded-xl shadow-2xl">
                <!-- Status -->
                <div
                    class="bg-linear-to-r from-blue-500 to-indigo-600 px-2 py-1.5">
                    <div class="flex items-center gap-2">
                        <UIcon
                            :name="statusIcon"
                            class="text-white text-lg shrink-0" />
                        <span class="text-xs text-white font-medium">
                            {{ hoveredSchool.status }}
                        </span>
                    </div>
                </div>

                <!-- School Name -->
                <div class="bg-white px-2 py-2">
                    <h4 class="font-semibold text-gray-900 text-xs">
                        {{ hoveredSchool.nazwa }}
                    </h4>
                </div>

                <!-- School Type -->
                <div class="bg-gray-50 px-2 py-1.5 border-t border-gray-100">
                    <div class="flex items-center gap-2">
                        <UIcon
                            name="i-mdi-school"
                            class="text-gray-500 text-lg shrink-0" />
                        <span class="text-xs text-gray-700 font-medium">
                            {{ hoveredSchool.typ }}
                        </span>
                    </div>
                </div>
            </div>
        </MglPopup>

        <MapSchoolLayers />
    </MglMap>
</template>
