<script setup lang="ts">
const { multiSelectFilters } = await useFilterData()

// get filters from route.query
const { hasActiveFilters, totalActiveFilters } = useSchoolFilters()

// Filter panel visibility
const isPanelOpen = ref(false)
const isSearchFocused = ref(false)

// Search interactions
const searchRef = useTemplateRef("searchRef")

const handlePanelToggle = () => {
    isPanelOpen.value = !isPanelOpen.value

    // set search focus to false to hide suggestions
    searchRef.value?.closeSearch()

    if (!isPanelOpen.value) closeFilters()
}

const closeFilters = () => {
    isPanelOpen.value = false
    isSearchFocused.value = false
    searchRef.value?.closeSearch()

    // panel closed, set addingState to false for all filters
    multiSelectFilters.forEach((filter) => {
        filter.addingState = false
    })
}

const handleSearchFocusChange = (focused: boolean) => {
    isSearchFocused.value = focused
}
</script>

<template>
    <div class="filters-absolute-container">
        <!-- Search Bar -->
        <div class="flex gap-2 items-center">
            <MapFiltersSearch
                ref="searchRef"
                @close="closeFilters"
                @focus-change="handleSearchFocusChange"
                @filter-panel-closed="isPanelOpen = false" />
            <!-- Filter Toggle Button -->
            <UButton
                :icon="isPanelOpen ? 'i-mdi-filter-off' : 'i-mdi-filter'"
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
    </div>
    <!-- Filter Panel -->
    <Transition name="slide-fade">
        <div v-show="isPanelOpen" class="filters-absolute-container mt-12">
            <MapFiltersPanel v-model="multiSelectFilters" />
        </div>
    </Transition>
    <!-- Overlay for closing search input/filter panel when clicking outside -->
    <div
        v-if="isPanelOpen || isSearchFocused"
        class="fixed inset-0 z-10 bg-black/25 dark:bg-black/45"
        @click="closeFilters" />
</template>

<style scoped>
@reference "tailwindcss";

.filters-absolute-container {
    @apply absolute top-20 left-2 z-20 max-w-[95%];
}

.slide-fade-enter-active {
    @apply transition-all duration-300 ease-out;
}

.slide-fade-leave-active {
    @apply transition-all duration-300 ease-in;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
    @apply opacity-0 -translate-y-20;
}
</style>
