<script setup lang="ts">
import { MAP_CONFIG } from "~/constants/mapConfig"
import { useSchoolFiltersFromRoute } from "~/composables/useSchoolFiltersFromRoute"
import {
    CLUSTER_LAYER_STYLE,
    POINT_LAYER_STYLE,
} from "~/constants/mapLayerStyles"
import type { SchoolFilterParams, SzkolaPublicShort } from "~/types/schools"

const { $api } = useNuxtApp()

// filters computed
const { filters } = useSchoolFiltersFromRoute()
// console.log(`Filters: ${filters.value}`)

// user messages using toast from nuxt-ui
const toast = useToast()

const schools = shallowRef<SzkolaPublicShort[]>([])
const searchSchools = shallowRef<SzkolaPublicShort[]>([])
const { geoJsonSource } = useSchoolGeoJson(schools)
const { geoJsonSource: searchGeoJsonSource } = useSchoolGeoJson(searchSchools)
const { bbox } = useBoundingBox()

const isSearchActive = computed(() => {
    return !!filters.value.q
})

const handleNewFilters = async (schoolFilters: SchoolFilterParams) => {
    toast.clear()
    toast.add({
        title: "Ładowanie danych",
        description: "Pobieranie danych szkół na mapę...",
        icon: "i-line-md-loading-loop",
        color: "info",
        id: "loading-schools-toast",
    })
    const bb = bbox.value
    try {
        // console.log(`Fetching schools for bbox`)
        // const data = await $api<SzkolaPublicShort[]>("/schools", {
        //     query: {
        //         ...schoolFilters,
        //         bbox: `${bb.minLon},${bb.minLat},${bb.maxLon},${bb.maxLat}`,
        //     },
        // })
        //
        // schools.value = data
        //
        // // get schools for the whole map if bbox is smaller than PolandBounds
        // const [minLon, minLat, maxLon, maxLat] = MAP_CONFIG.polandBounds
        //
        // if (
        //     bb.minLat < minLat &&
        //     bb.maxLat > maxLat &&
        //     bb.minLon < minLon &&
        //     bb.maxLon > maxLon
        // ) {
        //     console.log("Bbox is bigger than PolandBounds, skipping...")
        //     return
        // }
        //
        // console.log("Fetching schools for the whole map with new filters...")
        const data = await $api<SzkolaPublicShort[]>("/schools/", {
            query: schoolFilters,
        })
        if (schoolFilters?.q) {
            // Search mode: fetch into searchSchools
            console.log("Fetching schools for search query...", schoolFilters.q)
            searchSchools.value = data
            // Clear main schools? Optional, but we toggle visibility anyway.
        } else {
            // Default mode: fetch into schools (whole map or bbox)
            // console.log("Fetching schools for the whole map with new filters...")
            schools.value = data
            searchSchools.value = []
        }
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
let lastKey = ""
watch(
    filters,
    (schoolFilters) => {
        const key = JSON.stringify(schoolFilters)
        if (key === lastKey) return
        lastKey = key
        console.log("Query changed!")
        handleNewFilters(schoolFilters)
    },
    { immediate: true },
)
</script>

<template>
    <!-- Default Source -->
    <MglGeoJsonSource
        source-id="schools-source"
        :data="geoJsonSource"
        :cluster="true"
        :cluster-max-zoom="14"
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
            :layout="{
                ...POINT_LAYER_STYLE.layout,
                visibility: isSearchActive ? 'none' : 'visible',
            }" />

        <MglCircleLayer
            layer-id="clusters"
            source="schools-source"
            :filter="['has', 'cluster']"
            :paint="CLUSTER_LAYER_STYLE.paint"
            :layout="{ visibility: isSearchActive ? 'none' : 'visible' }" />

        <MglSymbolLayer
            layer-id="cluster-count"
            source="schools-source"
            :filter="['has', 'cluster']"
            :layout="{
                ...CLUSTER_LAYER_STYLE.layout,
                visibility: isSearchActive ? 'none' : 'visible',
            }" />
    </MglGeoJsonSource>

    <MglGeoJsonSource
        source-id="search-schools-source"
        :data="searchGeoJsonSource">
        <MglSymbolLayer
            layer-id="search-unclustered-points"
            source="search-schools-source"
            :filter="['!', ['has', 'point_count']]"
            :paint="POINT_LAYER_STYLE.paint"
            :layout="{
                ...POINT_LAYER_STYLE.layout,
                visibility: isSearchActive ? 'visible' : 'none',
            }" />
    </MglGeoJsonSource>
</template>
