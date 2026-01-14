<script setup lang="ts">
import { MAP_CONFIG, ICON_URLS } from "~/constants/mapConfig"
import type { SzkolaPublicWithRelations } from "~/types/schools"

const emit = defineEmits<{
    "point-clicked": [school: SzkolaPublicWithRelations]
}>()

const { bbox, updateBbox } = useBoundingBox()
const popupCoordinates: Ref<[number, number] | undefined> = ref(undefined)
const { setupMapEventHandlers, hoveredSchool } = useMapInteractions(
    emit,
    updateBbox,
    popupCoordinates,
)

console.log(`bbox: ${bbox}`)

const onMapLoaded = (event: { map: maplibregl.Map }) => {
    setupMapEventHandlers(event.map)
    updateBbox(event.map.getBounds())
}
</script>

<template>
    <MglMap
        :map-style="MAP_CONFIG.style"
        :max-bounds="MAP_CONFIG.polandBounds"
        :bounds="[
            [bbox.minLon, bbox.minLat],
            [bbox.maxLon, bbox.maxLat],
        ]"
        height="100vh"
        @map:load="onMapLoaded">
        <MglNavigationControl />

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
                    {{ JSON.parse(hoveredSchool.status_publicznoprawny).nazwa }}
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
                        {{ JSON.parse(hoveredSchool.typ).nazwa }}
                    </span>
                </div>
            </div>
        </MglPopup>

        <MapSchoolLayers />
    </MglMap>
</template>
