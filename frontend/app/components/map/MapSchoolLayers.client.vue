<script setup lang="ts">
import { useSchoolFiltersFromRoute } from "~/composables/useSchoolFiltersFromRoute"
import {
    CLUSTER_LAYER_STYLE,
    POINT_LAYER_STYLE,
} from "~/constants/mapLayerStyles"
import type { SchoolFilterParams, SzkolaPublicShort } from "~/types/schools"

const { $api } = useNuxtApp()

// filters computed
const { filters } = useSchoolFiltersFromRoute()
console.log(`Filters: ${filters.value}`)

// user messages using toast from nuxt-ui
const toast = useToast()

let schools = ref<SzkolaPublicShort[]>([])
const { geoJsonSource } = useSchoolGeoJson(schools)
const { bbox } = useBoundingBox()

const handleNewFilters = async (schoolFilters: SchoolFilterParams) => {
    toast.clear()
    toast.add({
        title: "Ładowanie danych",
        description: "Pobieranie danych szkół na mapę...",
        icon: "i-line-md-loading-loop",
        color: "info",
        id: "loading-schools-toast",
    })
    try {
        console.log(`Fetching schools for bbox`)
        const data = await $api<SzkolaPublicShort[]>("/schools", {
            query: {
                ...schoolFilters,
                bbox: `${bbox.value.minLon},${bbox.value.minLat},${bbox.value.maxLon},${bbox.value.maxLat}`,
            },
        })

        schools.value = data
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

    // get schools for the whole map
    console.log("Fetching schools for the whole map with new filters...")
    const data = await $api<SzkolaPublicShort[]>("/schools", {
        query: schoolFilters,
    })
    schools.value = data
}
let lastKey = ""
watch(filters, (schoolFilters) => {
    const key = JSON.stringify(schoolFilters)
    if (key === lastKey) return
    lastKey = key
    console.log("Query changed!")
    handleNewFilters(schoolFilters)
})
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
