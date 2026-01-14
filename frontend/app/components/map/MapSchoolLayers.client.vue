<script setup lang="ts">
import { useSchoolFiltersFromRoute } from "~/composables/useSchoolFiltersFromRoute"
import {
    CLUSTER_LAYER_STYLE,
    POINT_LAYER_STYLE,
} from "~/constants/mapLayerStyles"
import type { SchoolFilterParams, SzkolaPublicShort } from "~/types/schools"

const mapCache = useMapCacheStore() // cache for schools points
const { parseBbox } = useBoundingBox()
const { $api } = useNuxtApp()

// filters computed
const { filters } = useSchoolFiltersFromRoute()
console.log(`Filters: ${filters.value}`)

// user messages using toast from nuxt-ui
const toast = useToast()

let schools = ref<SzkolaPublicShort[]>([])
const { geoJsonSource } = useSchoolGeoJson(schools)

const handleNewFilters = async (schoolFilters: SchoolFilterParams) => {
    // parse bbox from query to check if it's valid
    const bbox = parseBbox(
        schoolFilters ? (schoolFilters.bbox as string) : null,
    )

    // Check cache with current filters
    const cachedSchools = mapCache.getSchoolsFromCache(bbox, schoolFilters)

    if (cachedSchools) {
        console.log(
            "MapSchoolLayers.vue - Map cache covers the bounding box with filters. Using cached data.",
        )
        schools.value = cachedSchools
        return
    }

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
            query: schoolFilters,
        })

        schools.value = data

        // Update Cache
        mapCache.addQuery(bbox, schoolFilters, data)
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
    filters,
    (schoolFilters) => {
        console.log("Query changed!")
        if (schoolFilters) handleNewFilters(schoolFilters)
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
