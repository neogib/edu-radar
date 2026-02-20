<script setup lang="ts">
const { multiSelectFilters } = await useFilterData()

// get filters from route.query
const { hasActiveFilters, totalActiveFilters } = useSchoolFilters()

// Filter panel visibility
const isFilterPanelOpen = ref(false)

// Search interactions
const searchRef = useTemplateRef("searchRef")

const handlePanelToggle = () => {
    isFilterPanelOpen.value = !isFilterPanelOpen.value

    // set search focus to false to hide suggestions
    searchRef.value?.blur()

    if (isFilterPanelOpen.value) {
        searchRef.value?.collapseSearch()
        return
    }

    handlePanelClose()
}

const handlePanelClose = () => {
    isFilterPanelOpen.value = false
    searchRef.value?.blur()
    searchRef.value?.collapseSearch()

    // panel closed, set addingState to false for all filters
    multiSelectFilters.forEach((filter) => {
        filter.addingState = false
    })
}
</script>

<template>
    <div class="absolute top-20 left-2 z-20 flex flex-col gap-2 max-w-[95%]">
        <!-- Search Bar -->
        <div class="flex gap-2 items-center">
            <MapFiltersSearch
                ref="searchRef"
                @panel-close="handlePanelClose"
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
            <div v-show="isFilterPanelOpen">
                <MapFiltersPanel
                    v-model="multiSelectFilters"
                    @close="handlePanelClose" />
            </div>
        </Transition>
    </div>
    <!-- Overlay for closing search input/filter panel when clicking outside -->
    <div
        v-if="isFilterPanelOpen || searchRef?.isSearchFocused"
        class="fixed inset-0 z-10 bg-black/25 dark:bg-black/45"
        @click="handlePanelClose" />
</template>

<style scoped>
@reference "tailwindcss";

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
