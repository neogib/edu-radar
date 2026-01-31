<script setup lang="ts">
import { useMap } from "@indoorequal/vue-maplibre-gl"
import { type Map } from "maplibre-gl"
import { MAP_CONFIG } from "~/constants/mapConfig"

const mapInstance = useMap(MAP_CONFIG.mapKey)

const { filterData } = await useFilterData()
const { isUnderZoomThreshold } = useMapState()

// get filters from route.query
const { filters, hasActiveFilters, totalActiveFilters } = useSchoolFilters()

const { debouncedLoadRemainingSchools } = useSchoolGeoJSONSource()

// Filter panel visibility
const isFilterPanelOpen = ref(false)
const filterKeyChanged = ref(false)

// Search state
const searchQuery = ref(filters.value.q || "")
const searchInputFocused = ref(false)
const isSearchExpanded = ref(false)

const collapseSearch = () => {
    // Only collapse if search is empty
    if (searchQuery.value.trim().length === 0) {
        isSearchExpanded.value = false
        searchInputFocused.value = false
    }
}

watch(totalActiveFilters, () => {
    filterKeyChanged.value = true
})

const handlePanelToggle = () => {
    isFilterPanelOpen.value = !isFilterPanelOpen.value

    // set search focus to false to hide suggestions
    searchInputFocused.value = false

    if (isFilterPanelOpen.value) {
        return
    }

    handlePanelClose()
}

const handlePanelClose = () => {
    isFilterPanelOpen.value = false
    searchInputFocused.value = false
    collapseSearch()

    // panel closed, set addingState to false for all filters
    filterData.forEach((filter) => {
        filter.addingState = false
    })

    handlePanelSubmit()
}

const handlePanelSubmit = () => {
    // trigger search if filters changed
    if (!filterKeyChanged.value) {
        return
    }
    filterKeyChanged.value = false

    debouncedLoadRemainingSchools()

    // logic to zoom out if no features in current view
    // if zoom already under threshold, no need to zoom out
    if (isUnderZoomThreshold.value) {
        return
    }

    const map = mapInstance.map as Map
    // if there are already features in current map view, no need to ease
    if (map.querySourceFeatures(MAP_CONFIG.sourceId).length > 1) {
        return
    }

    // ease to zoom, but don't zoom out below (current zoom - 3) levels
    const currentZoom = map.getZoom()
    const targetZoom = Math.max(currentZoom - 3, MAP_CONFIG.zoomThreshold)
    map.easeTo({ zoom: targetZoom })
}
</script>

<template>
    <div class="absolute top-20 left-2 z-20 flex flex-col gap-2 max-w-[95%]">
        <!-- Search Bar -->
        <div class="flex gap-2 items-center">
            <MapFiltersSearch
                v-model:searchQuery="searchQuery"
                v-model:searchInputFocused="searchInputFocused"
                v-model:isSearchExpanded="isSearchExpanded"
                @panel-close="handlePanelClose"
                @filter-key-changed="filterKeyChanged = true"
                @filter-panel-closed="isFilterPanelOpen = false" />
            <!-- Filter Toggle Button -->
            <UButton
                :icon="isFilterPanelOpen ? 'i-mdi-filter-off' : 'i-mdi-filter'"
                :color="hasActiveFilters ? 'info' : 'neutral'"
                :variant="hasActiveFilters ? 'solid' : 'outline'"
                size="md"
                @click.stop="handlePanelToggle">
                <template v-if="totalActiveFilters > 0">
                    <UBadge color="warning" class="ml-1">
                        {{ totalActiveFilters }}
                    </UBadge>
                </template>
            </UButton>
        </div>

        <!-- Filter Panel -->
        <Transition name="slide-fade">
            <MapFiltersPanel
                v-if="isFilterPanelOpen"
                v-model="filterData"
                @close="handlePanelClose" />
        </Transition>
    </div>
    <!-- Overlay for closing search input/filter panel when clicking outside -->
    <div
        v-if="isFilterPanelOpen || searchInputFocused"
        class="fixed inset-0 bg-black opacity-25 z-10"
        @click="handlePanelClose" />
</template>

<style scoped>
@reference "tailwindcss";

.slide-fade-enter-active {
    @apply transition-all duration-200 ease-out;
}

.slide-fade-leave-active {
    @apply transition-all duration-150 ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
    @apply opacity-0 -translate-y-2.5;
}

form {
    @apply transition-all duration-300 ease-out;
    animation: slideIn 0.3s ease-out forwards;
}

@keyframes slideIn {
    from {
        opacity: 0;
        transform: translateX(-20px);
    }
    to {
        opacity: 1;
        transform: translateX(0);
    }
}
</style>
