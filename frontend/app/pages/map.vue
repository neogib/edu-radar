<script setup lang="ts">
import { LazySidebarMain } from "#components"
import type { SzkolaPublicWithRelations } from "~/types/schools"
definePageMeta({
    middleware: "redirect-map",
})

useSeoMeta({
    title: "Mapa szkół w Polsce - Ranking | EduRadar",
    description:
        "Interaktywna mapa szkół w Polsce z rankingami, wynikami egzaminów i filtrowaniem.",
    ogTitle: "Sprawdź ranking swojej szkoły – EduRadar",
    ogDescription:
        "Znajdź najlepsze szkoły w swojej okolicy. Przeszukuj szkoły, porównuj rankingi i sprawdzaj najnowsze wyniki.",
    ogImage: "/og-image.png",
    twitterImage: "/og-image.png",
    twitterCard: "summary_large_image",
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

const initialBbox = useInitialBbox()
const { bboxController, streamingController } = useControllers()
onUnmounted(() => {
    sidebar.close()
    // Reset initialBbox when leaving map page
    initialBbox.value = undefined
    // abort controllers
    bboxController.value?.abort()
    streamingController.value?.abort()
})
</script>

<template>
    <div class="relative h-dvh w-screen overflow-hidden">
        <h1 class="sr-only">Mapa szkół w Polsce</h1>
        <NavBar overlay />
        <MapLegend />

        <div v-show="!selectedSchool">
            <MapFiltersBar />
        </div>

        <!-- MapView taking full remaining space -->
        <MapView @point-clicked="handlePointClick" />
    </div>
</template>
