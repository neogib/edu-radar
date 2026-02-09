<script setup lang="ts">
import type { SzkolaPublicWithRelations } from "~/types/schools"
definePageMeta({
    colorMode: "light",
    middleware: "redirect-map",
})

// Reactive state for sidebar
const isSidebarOpen = ref(false)
const selectedSchool = ref<SzkolaPublicWithRelations | null>(null)

// Handle data updates from map interactions
const handlePointClick = (school: SzkolaPublicWithRelations | null) => {
    if (!school) {
        handleSidebarClose()
        return
    }

    selectedSchool.value = school
    isSidebarOpen.value = true
}

const handleSidebarClose = () => {
    isSidebarOpen.value = false
    selectedSchool.value = null
}

const initialBbox = useInitialBbox()
const { bboxController, streamingController } = useControllers()
onUnmounted(() => {
    // Reset initialBbox when leaving map page
    initialBbox.value = undefined
    // abort controllers
    bboxController.value?.abort()
    streamingController.value?.abort()
})
</script>

<template>
    <div class="relative h-dvh w-screen overflow-hidden">
        <NavBar class="absolute w-full" />
        <MapLegend />

        <SidebarMain
            :is-open="isSidebarOpen"
            :selected-point="selectedSchool"
            @close="handleSidebarClose" />

        <div v-show="!isSidebarOpen">
            <MapFiltersBar />
        </div>

        <!-- MapView taking full remaining space -->
        <MapView @point-clicked="handlePointClick" />
    </div>
</template>
