<script setup lang="ts">
import { LazySidebarMain } from "#components"
import type { SzkolaPublicWithRelations } from "~/types/schools"
definePageMeta({
    middleware: "redirect-map",
    layout: false,
})

useSeoMeta({
    title: "Mapa szkół w Polsce i rankingi",
    description:
        "Interaktywna mapa szkół w Polsce z rankingami, wynikami egzaminów i filtrowaniem.",
})

const selectedSchool = ref<SzkolaPublicWithRelations | null>(null)
const overlay = useOverlay()
const sidebar = overlay.create(LazySidebarMain)

const openSidebar = (school: SzkolaPublicWithRelations) => {
    selectedSchool.value = school

    if (overlay.isOpen(sidebar.id)) {
        sidebar.patch({
            selectedPoint: school,
        })
        return
    }

    const instance = sidebar.open({
        selectedPoint: school,
    })

    void instance.result.finally(() => {
        selectedSchool.value = null
    })
}

// Handle data updates from map interactions
const handlePointClick = (school: SzkolaPublicWithRelations | null) => {
    if (!school) {
        handleSidebarClose()
        return
    }

    openSidebar(school)
}

const handleSidebarClose = () => {
    sidebar.close()
    selectedSchool.value = null
}

onUnmounted(() => {
    sidebar.close()
})
</script>

<template>
    <div class="relative h-dvh w-screen overflow-hidden">
        <h1 class="sr-only">Mapa szkół w Polsce</h1>
        <NavBar overlay />
        <MapLegend />

        <div v-show="!selectedSchool">
            <MapFilters />
        </div>

        <!-- MapView taking full remaining space -->
        <MapView @point-clicked="handlePointClick" />
    </div>
</template>
