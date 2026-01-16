<script setup lang="ts">
import type { SzkolaPublicWithRelations } from "~/types/schools"
definePageMeta({
    colorMode: "light",
})

// Reactive state for sidebar
const isSidebarOpen = ref(false)
const selectedSchool = ref<SzkolaPublicWithRelations | null>(null)

// Handle data updates from map interactions
const handlePointClick = (school: SzkolaPublicWithRelations) => {
    selectedSchool.value = school
    isSidebarOpen.value = true
}

const handleSidebarClose = () => {
    isSidebarOpen.value = false
    selectedSchool.value = null
}
</script>

<template>
    <div>
        <NavBar class="absolute w-full" />

        <!-- Sidebar -->
        <SidebarMain
            :is-open="isSidebarOpen"
            :selected-point="selectedSchool"
            @close="handleSidebarClose" />
        <MapSearchFilter v-if="!isSidebarOpen" />

        <!-- MapView taking full remaining space with dynamic margin for sidebar -->
        <div :class="['transition-all duration-300']">
            <MapView @point-clicked="handlePointClick" />
        </div>
    </div>
</template>
