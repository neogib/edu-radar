<script setup lang="ts">
import type { MapSourceDataEvent } from "maplibre-gl"
import { useSchoolGeoJSONSource } from "~/composables/useSchoolGeoJSONSource"
import { MAP_CONFIG, ICONS } from "~/constants/mapConfig"
import type { SzkolaPublicWithRelations } from "~/types/schools"

useHistoryState()
const route = useRoute()
const colorMode = useColorMode()
const [x, y, z] = [
    Number(route.query.x),
    Number(route.query.y),
    Number(route.query.z),
]
const emit = defineEmits<{
    "point-clicked": [school: SzkolaPublicWithRelations | null]
}>()

const popupCoordinates: Ref<[number, number] | undefined> = ref(undefined)
const { setupMapEventHandlers, hoveredSchool } = useMapInteractions(
    emit,
    popupCoordinates,
)
const mapStyle = computed(() =>
    colorMode.value === "dark" ? MAP_CONFIG.darkStyle : MAP_CONFIG.lightStyle,
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

    // wait for source to be ready and fully loaded
    const onSourceData = async (e: MapSourceDataEvent) => {
        if (e.sourceId !== MAP_CONFIG.sourceId) return
        if (!e.isSourceLoaded) return

        map.off("sourcedata", onSourceData)
        console.log("Schools source is ready")
        await initializeWithSource(map)
    }

    if (
        map.getSource(MAP_CONFIG.sourceId) &&
        map.isSourceLoaded(MAP_CONFIG.sourceId)
    ) {
        await initializeWithSource(map)
    } else {
        map.on("sourcedata", onSourceData)
    }
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
        :map-style="mapStyle"
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
            :position-options="{ enableHighAccuracy: true }"
            :track-user-location="true" />

        <MglImage
            v-for="(url, id) in ICONS"
            :id="id"
            :key="id"
            :url="url"
            :options="{ sdf: true }" />

        <MglPopup
            v-if="hoveredSchool"
            :close-button="false"
            :close-on-click="false"
            :offset="20"
            :coordinates="popupCoordinates">
            <div
                class="min-w-55 max-w-70 overflow-hidden rounded-xl border border-default bg-default shadow-2xl">
                <!-- Status -->
                <div
                    class="bg-linear-to-r from-blue-500 to-indigo-600 dark:from-blue-600 dark:to-violet-700 px-2 py-1.5">
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
                <div class="bg-default px-2 py-2">
                    <h4 class="font-semibold text-highlighted text-xs">
                        {{ hoveredSchool.nazwa }}
                    </h4>
                </div>

                <!-- School Type -->
                <div
                    class="bg-muted px-2 py-1.5 border-t border-default dark:bg-elevated">
                    <div class="flex items-center gap-2">
                        <UIcon
                            name="i-mdi-school"
                            class="text-muted text-lg shrink-0" />
                        <span class="text-xs text-default font-medium">
                            {{ hoveredSchool.typ }}
                        </span>
                    </div>
                </div>
            </div>
        </MglPopup>

        <MapSchoolLayers />
    </MglMap>
</template>
