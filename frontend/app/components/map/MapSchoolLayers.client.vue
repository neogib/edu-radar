<script setup lang="ts">
import type { LocationQuery } from "vue-router"
import {
    CLUSTER_LAYER_STYLE,
    POINT_LAYER_STYLE,
} from "~/constants/mapLayerStyles"
import type { BoundingBox } from "~/types/boundingBox"
import type { SzkolaPublicShort } from "~/types/schools"

const route = useRoute()
const mapCache = useMapCacheStore() // cache for schools points
const { parseBbox } = useBoundingBox()
const { $api } = useNuxtApp()

// user messages using toast from nuxt-ui
const toast = useToast()

let schools = ref<SzkolaPublicShort[]>([])
const { geoJsonSource } = useSchoolGeoJson(schools)

const handleQueryChange = async (newQuery: LocationQuery) => {
    // no need to fetch data if cache already covers the bbox
    // if (mapCache.isCovered(newBbox)) {
    //     console.log(
    //         "MapSchoolLayers.vue - Map cache already covers the bounding box. No data fetch needed.",
    //     )
    //     schools.value = mapCache.getCachedSchools(bbox.value)
    //     return
    // }

    // if the user on its own updates query we should first remove elements that are not in SchoolFilterParams

    // parse bbox from query to check if it's valid
    const bbox = parseBbox(newQuery ? (newQuery.bbox as string) : null)

    toast.clear()
    toast.add({
        title: "Ładowanie danych",
        description: "Pobieranie danych szkół na mapę...",
        icon: "i-line-md-loading-loop",
        color: "info",
        id: "loading-schools-toast",
    })

    console.log(
        "MapSchoolLayers.vue - Map cache does not cover the bounding box. Fetching new data.",
    )
    try {
        const data = await $api<SzkolaPublicShort[]>("/schools", {
            query: {
                ...route.query,
                bbox: `${bbox.minLon},${bbox.minLat},${bbox.maxLon},${bbox.maxLat}`,
            },
        })

        schools.value = data

        // Update Cache
        // mapCache.addSchools(data)
        // mapCache.addFetchedArea(newQuery)
    } catch (err) {
        toast.add({
            title: "Błąd ładowania danych",
            description:
                "Wystąpił błąd podczas pobierania danych szkół na mapę.",
            icon: "i-line-md-alert-circle",
            color: "error",
            id: "error-schools-toast",
        })
    } finally {
        toast.remove("loading-schools-toast")
    }
}
watch(
    () => route.query,
    (newQuery) => {
        console.log("Query changed!")
        handleQueryChange(newQuery)
    },
    { immediate: true },
)
</script>

<template>
    <MglGeoJsonSource
        source-id="schools-source"
        :data="geoJsonSource"
        :cluster="true"
        :cluster-properties="{
            sum: [
                '+',
                ['case', ['!=', ['get', 'score'], null], ['get', 'score'], 0],
            ],
            nonNullCount: ['+', ['case', ['!=', ['get', 'score'], null], 1, 0]],
        }">
        <MglSymbolLayer
            layer-id="unclustered-points"
            source="schools-source"
            :filter="['!', ['has', 'point_count']]"
            :paint="POINT_LAYER_STYLE.paint"
            :layout="POINT_LAYER_STYLE.layout" />

        <MglCircleLayer
            layer-id="clusters"
            source="schools-source"
            :filter="['has', 'cluster']"
            :paint="CLUSTER_LAYER_STYLE.paint" />

        <MglSymbolLayer
            layer-id="cluster-count"
            source="schools-source"
            :filter="['has', 'cluster']"
            :layout="CLUSTER_LAYER_STYLE.layout" />
    </MglGeoJsonSource>
</template>
