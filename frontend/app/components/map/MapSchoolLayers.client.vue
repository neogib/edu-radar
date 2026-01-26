<script setup lang="ts">
import {
    CLUSTER_LAYER_STYLE,
    POINT_LAYER_STYLE,
} from "~/constants/mapLayerStyles"
import type { SchoolFilterParams, SzkolaPublicShort } from "~/types/schools"
import { useMap } from "@indoorequal/vue-maplibre-gl"
import { VOIVODESHIP_NAMES } from "~/constants/voivodeships"
import { MAP_CONFIG } from "~/constants/mapConfig"
import type { BoundingBox } from "~/types/boundingBox"

// filters shared state initialized from route query params
// const { filters } = useSchoolFilters()

// const schools = shallowRef<SzkolaPublicShort[]>([])
// const searchSchools = shallowRef<SzkolaPublicShort[]>([])
// const { calculateBounds } = useMapBounds()

// const isSearchActive = computed(() => {
//     return !!filters.value.q
// })

// Auto-fit bounds when GeoJSON data changes
// const autoFitBounds = async (geoJson: any) => {
//     const bounds = calculateBounds(geoJson)
//     if (bounds) {
//         const map = useMap("mainMap").map
//         map?.fitBounds(bounds, {
//             padding: 50,
//             maxZoom: 14,
//             animate: true,
//         })
//     }
// }

// Watch for changes in search results and fit bounds
// watch(
//     searchGeoJsonSource,
//     (newGeoJson) => {
//         if (isSearchActive.value && newGeoJson?.features?.length) {
//             autoFitBounds(newGeoJson)
//         }
//     },
//     { deep: true },
// )

const route = useRoute()

let initialBbox = useInitialBbox()

// set to default bbox if default map view is used
// we can't always set bbox because map is not yet loaded
if (
    initialBbox.value == null &&
    Number(route.query.x) === MAP_CONFIG.defaultCenter[0] && // default center already has 6 decimal places
    Number(route.query.y) === MAP_CONFIG.defaultCenter[1] &&
    Number(route.query.z) === MAP_CONFIG.defaultZoom
) {
    initialBbox.value = MAP_CONFIG.defaultBbox
}
const { loadSchoolsFromBbox, schoolsSource } = useSchoolGeoJSONSource()
console.log("Initial bbox:", initialBbox.value)
await loadSchoolsFromBbox(initialBbox.value)
console.log(`number of schools loaded: ${schoolsSource.value.features.length}`)
</script>

<template>
    <!-- Default Source -->
    <MglGeoJsonSource
        source-id="schools"
        :data="schoolsSource"
        :cluster="true"
        :cluster-max-zoom="14"
        :promote-id="'id'"
        :cluster-properties="{
            sum: [
                '+',
                ['case', ['!=', ['get', 'score'], null], ['get', 'score'], 0],
            ],
            nonNullCount: ['+', ['case', ['!=', ['get', 'score'], null], 1, 0]],
        }">
        <MglSymbolLayer
            layer-id="unclustered-points"
            source="schools"
            :filter="['!', ['has', 'point_count']]"
            :paint="POINT_LAYER_STYLE.paint"
            :layout="{
                ...POINT_LAYER_STYLE.layout,
            }" />

        <MglCircleLayer
            layer-id="clusters"
            source="schools"
            :filter="['has', 'cluster']"
            :paint="CLUSTER_LAYER_STYLE.paint" />

        <MglSymbolLayer
            layer-id="cluster-count"
            source="schools"
            :filter="['has', 'cluster']"
            :layout="{
                ...CLUSTER_LAYER_STYLE.layout,
            }" />
    </MglGeoJsonSource>
</template>
