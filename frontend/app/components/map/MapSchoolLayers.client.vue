<script setup lang="ts">
import {
    CLUSTER_LAYER_STYLE,
    POINT_LAYER_STYLE,
} from "~/constants/mapLayerStyles"
import { MAP_CONFIG } from "~/constants/mapConfig"

const route = useRoute()
let initialBbox = useInitialBbox()
const { schoolsGeoJSONFeatures } = useSchools()
const { filters } = useSchoolFilters()
const { bboxController } = useControllers()

const schoolsSource = shallowRef<GeoJSON.FeatureCollection>({
    type: "FeatureCollection",
    features: [],
})

// set to default bbox if default map view is used
const shouldUseDefaultBbox = () =>
    !initialBbox.value &&
    Number(route.query.x) === MAP_CONFIG.defaultCenter[0] &&
    Number(route.query.y) === MAP_CONFIG.defaultCenter[1] &&
    Number(route.query.z) === MAP_CONFIG.defaultZoom

const loadSchools = async () => {
    // load initial schools only when initialBbox exists
    if (!initialBbox.value) return

    // abort previous bbox request and create a new controller
    bboxController.value?.abort()
    bboxController.value = new AbortController()

    const schools = await schoolsGeoJSONFeatures({
        query: {
            ...filters.value,
            ...initialBbox.value!,
        },
        signal: bboxController.value.signal,
    })
    schoolsSource.value = {
        type: "FeatureCollection",
        features: schools,
    }
}

if (shouldUseDefaultBbox()) {
    initialBbox.value = MAP_CONFIG.defaultBbox
}
await loadSchools()
</script>

<template>
    <!-- Default Source -->
    <MglGeoJsonSource
        :source-id="MAP_CONFIG.sourceId"
        :data="schoolsSource"
        :cluster="true"
        :cluster-max-zoom="14"
        :promote-id="'id'"
        :cluster-properties="{
            sum: [
                '+',
                ['case', ['!=', ['get', 'wynik'], null], ['get', 'wynik'], 0],
            ],
            nonNullCount: ['+', ['case', ['!=', ['get', 'wynik'], null], 1, 0]],
        }">
        <MglSymbolLayer
            layer-id="unclustered-points"
            :source="MAP_CONFIG.sourceId"
            :filter="['!', ['has', 'point_count']]"
            :paint="POINT_LAYER_STYLE.paint"
            :layout="{
                ...POINT_LAYER_STYLE.layout,
            }" />

        <MglCircleLayer
            layer-id="clusters"
            :source="MAP_CONFIG.sourceId"
            :filter="['has', 'cluster']"
            :paint="CLUSTER_LAYER_STYLE.paint" />

        <MglSymbolLayer
            layer-id="cluster-count"
            :source="MAP_CONFIG.sourceId"
            :filter="['has', 'cluster']"
            :layout="{
                ...CLUSTER_LAYER_STYLE.layout,
            }" />
    </MglGeoJsonSource>
</template>
