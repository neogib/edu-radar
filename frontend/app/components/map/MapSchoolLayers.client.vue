<script setup lang="ts">
import {
    getClusterLayerStyle,
    getPointLayerStyle,
} from "~/constants/mapLayerStyles"
import { MAP_CONFIG } from "~/constants/mapConfig"

const colorMode = useColorMode()
const runtimeConfig = useRuntimeConfig()
const { filters } = useSchoolFilters()

const isDarkMode = computed(() => colorMode.value === "dark")
const pointLayerStyle = computed(() => getPointLayerStyle(isDarkMode.value))
const clusterLayerStyle = computed(() => getClusterLayerStyle(isDarkMode.value))

const buildCsvParam = (
    values: number[] | null | undefined,
): string | undefined => {
    if (!values || values.length === 0) return undefined
    return values.join(",")
}

const martinQueryString = computed(() => {
    const params = new URLSearchParams()

    const type = buildCsvParam(filters.value.type)
    const status = buildCsvParam(filters.value.status)
    const category = buildCsvParam(filters.value.category)
    const career = buildCsvParam(filters.value.career)

    if (type) params.set("type", type)
    if (status) params.set("status", status)
    if (category) params.set("category", category)
    if (career) params.set("career", career)
    if (filters.value.minScore !== undefined) {
        params.set("minScore", String(filters.value.minScore))
    }
    if (filters.value.maxScore !== undefined) {
        params.set("maxScore", String(filters.value.maxScore))
    }
    if (filters.value.q) {
        params.set("q", filters.value.q)
    }

    return params.toString()
})

const martinTiles = computed(() => {
    const endpoint = `${runtimeConfig.public.martinBase}/szkola_clustered/{z}/{x}/{y}`
    const query = martinQueryString.value
    return [query ? `${endpoint}?${query}` : endpoint]
})
</script>

<template>
    <MglVectorSource
        :source-id="MAP_CONFIG.sourceId"
        :tiles="martinTiles"
        :promote-id="'state_id'">
        <MglSymbolLayer
            layer-id="unclustered-points"
            :source="MAP_CONFIG.sourceId"
            :source-layer="MAP_CONFIG.martinSourceLayer"
            :filter="['==', ['get', 'cluster'], false]"
            :paint="pointLayerStyle.paint"
            :layout="pointLayerStyle.layout" />

        <MglCircleLayer
            layer-id="clusters"
            :source="MAP_CONFIG.sourceId"
            :source-layer="MAP_CONFIG.martinSourceLayer"
            :filter="['==', ['get', 'cluster'], true]"
            :paint="clusterLayerStyle.paint" />

        <MglSymbolLayer
            layer-id="cluster-count"
            :source="MAP_CONFIG.sourceId"
            :source-layer="MAP_CONFIG.martinSourceLayer"
            :filter="['==', ['get', 'cluster'], true]"
            :layout="clusterLayerStyle.layout" />
    </MglVectorSource>
</template>
