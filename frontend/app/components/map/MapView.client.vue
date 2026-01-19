<script setup lang="ts">
import type { LngLatBoundsLike } from "maplibre-gl"
import type { SzkolaPublicShort } from "~/types/schools"
import { MAP_CONFIG, ICON_URLS } from "~/constants/mapConfig"
import type { SzkolaPublicWithRelations } from "~/types/schools"
import MaplibreGeocoder from "@maplibre/maplibre-gl-geocoder"
// import "@maplibre/maplibre-gl-geocoder/dist/maplibre-gl-geocoder.css"
import maplibregl from "maplibre-gl"

const route = useRoute()
const emit = defineEmits<{
    "point-clicked": [school: SzkolaPublicWithRelations]
}>()

const { parseBbox } = useBoundingBox()
const popupCoordinates: Ref<[number, number] | undefined> = ref(undefined)
const { setupMapEventHandlers, hoveredSchool, updateQueryBboxParam } =
    useMapInteractions(emit, popupCoordinates)

const bbox = parseBbox((route.query.bbox as string) ?? undefined)

const bounds: LngLatBoundsLike | undefined = !route.query.bbox
    ? undefined
    : [bbox.minLon, bbox.minLat, bbox.maxLon, bbox.maxLat]

const { filters } = useSchoolFiltersFromRoute()

const onMapLoaded = (event: { map: maplibregl.Map }) => {
    const map = event.map
    setupMapEventHandlers(map)
    updateQueryBboxParam(map.getBounds())
    const geocoder = new MaplibreGeocoder(
        {
            forwardGeocode: async (config) => {
                console.log("Geocoding query:", config.query)
                const text = config.query
                if (!text || text.length < 2) return { features: [] }

                const { $api } = useNuxtApp()
                const searchSchools = await $api<SzkolaPublicShort[]>(
                    "/schools",
                    {
                        query: {
                            ...filters.value,
                            q: text,
                            limit: 20,
                        },
                    },
                )

                return {
                    features: searchSchools.map((s) => ({
                        type: "Feature",
                        geometry: {
                            type: "Point",
                            coordinates: [
                                s.geolokalizacja_longitude,
                                s.geolokalizacja_latitude,
                            ],
                        },
                        properties: s,
                        place_name: s.nazwa,
                        place_type: ["place"],
                        text: s.nazwa,
                        center: [
                            s.geolokalizacja_longitude,
                            s.geolokalizacja_latitude,
                        ],
                    })),
                }
            },
        },
        {
            maplibregl: maplibregl,
            limit: 10,
            marker: false,
            placeholder: "Szukaj szkół po nazwie...",
            showResultsWhileTyping: true,
            debounceSearch: 500,
        },
    )
    // geocoder.addTo(searchInput.value) // maybe modify stryles for .maplibregl-ctrl-geocoder--input
    map.addControl(geocoder)
}
</script>

<template>
    <MglMap
        :map-style="MAP_CONFIG.style"
        :center="MAP_CONFIG.defaultCenter"
        :zoom="MAP_CONFIG.defaultZoom"
        :bounds="bounds"
        :fade-duration="0"
        :min-zoom="MAP_CONFIG.minZoom"
        :max-zoom="MAP_CONFIG.maxZoom"
        :canvasContextAttributes="{ antialias: true }"
        class="mglmap"
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
