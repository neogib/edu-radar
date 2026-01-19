<script setup lang="ts">
import { filterConfigs } from "~/constants/filters"
import type { FiltersResponse } from "~/types/schools"
import { SELECTION_KEYS, type ActiveSelections } from "~/types/filters"

// all filter options from api
const { data: filterOptions } = useApi<FiltersResponse>("/filters/")

// get filters from route.query
const { filters } = useSchoolFiltersFromRoute()

// Search state
const searchQuery = ref("") // later maybe add to filters

// min, max score
const min_score = ref<number | undefined>(filters.value.min_score)
const max_score = ref<number | undefined>(filters.value.max_score)

// Filter panel visibility
const isFilterPanelOpen = ref(false)

const activeSelections = reactive<ActiveSelections>({
    type: filters.value.type ?? [],
    status: filters.value.status ?? [],
    category: filters.value.category ?? [],
    vocational_training: filters.value.vocational_training ?? [],
})

// Get available items (not already selected) for a filter
const getAvailableItems = (
    optionsKey: keyof NonNullable<typeof filterOptions.value>,
    key: keyof ActiveSelections,
    currentIndex: number,
) => {
    const allItems = filterOptions.value?.[optionsKey] ?? []
    const items = allItems.map((option) => ({
        label: option.nazwa,
        value: option.id,
    }))
    console.log(
        `Getting available items for ${key} at index ${currentIndex}, selectedValues: ${
            activeSelections[key]
        }`,
    )
    const selectedValues = activeSelections[key]
    // Keep items not selected, OR the current selection at this index
    return items.filter(
        (item) =>
            !selectedValues.includes(item.value) ||
            selectedValues[currentIndex] === item.value,
    )
}

// Normalize selections by removing invalid (-1) entries that you can't send to the backend
const normalize = (v: number[]) => v.filter((n) => n > 0)

const normalizeSelections = () => {
    for (const key of SELECTION_KEYS) {
        activeSelections[key] = normalize(activeSelections[key])
    }
}

// Check if we can add more selections (has valid selection AND more options available)
const canAddMore = (
    optionsKey: keyof FiltersResponse,
    key: keyof ActiveSelections,
) => {
    const userSelections = activeSelections[key]

    // 1. hard fail on invalid values (there is already select box not filled)
    if (userSelections.some((v) => v < 0)) {
        return false
    }

    // 2. no selections → can add
    if (userSelections.length === 0) {
        return true
    }

    const totalOptions = filterOptions.value?.[optionsKey]?.length ?? 0

    const validCount = normalize(userSelections).length

    return validCount > 0 && validCount < totalOptions
}

// Count total active filters
const activeFilterCount = computed(() => {
    let count = 0
    for (const key of SELECTION_KEYS) {
        count += normalize(activeSelections[key]).length
    }
    if (min_score.value) count++
    if (max_score.value && max_score.value !== 100) count++
    return count
})

const hasActiveFilters = computed(() => activeFilterCount.value > 0)

// Handle search/filters submit
const route = useRoute()
const handleSearch = async () => {
    // normalize before navigating to avoid sending invalid values
    normalizeSelections()
    isFilterPanelOpen.value = false
    await navigateTo({
        query: {
            bbox: route.query.bbox || undefined,
            search: searchQuery.value || undefined,
            type:
                activeSelections.type.length > 0
                    ? activeSelections.type
                    : undefined,
            status:
                activeSelections.status.length > 0
                    ? activeSelections.status
                    : undefined,
            category:
                activeSelections.category.length > 0
                    ? activeSelections.category
                    : undefined,
            vocational_training:
                activeSelections.vocational_training.length > 0
                    ? activeSelections.vocational_training
                    : undefined,
            min_score: min_score.value || undefined,
            max_score: max_score.value !== 100 ? max_score.value : undefined,
        },
    })
}

// toggle filter panel
const handleFiltersToggle = () => {
    isFilterPanelOpen.value = !isFilterPanelOpen.value
    normalizeSelections()
}

// Clear all filters
const handleClearFilters = () => {
    searchQuery.value = ""
    activeSelections.type = []
    activeSelections.status = []
    activeSelections.category = []
    activeSelections.vocational_training = []
    min_score.value = undefined
    max_score.value = undefined
}
</script>

<template>
    <div class="absolute top-20 left-2 z-20 flex flex-col gap-2 max-w-[95%]">
        <!-- Search Bar -->
        <div class="flex gap-2 items-center">
            <!-- <form -->
            <!--     class="flex-1 min-w-60 max-w-100" -->
            <!--     @submit.prevent="handleSearch"> -->
            <!--     <UInput -->
            <!--         v-model="searchQuery" -->
            <!--         icon="i-mdi-magnify" -->
            <!--         placeholder="Szukaj szkoły..." -->
            <!--         size="md" -->
            <!--         :ui="{ root: 'w-full' }" /> -->
            <!-- </form> -->

            <!-- Filter Toggle Button -->
            <UButton
                :icon="isFilterPanelOpen ? 'i-mdi-filter-off' : 'i-mdi-filter'"
                :color="hasActiveFilters ? 'primary' : 'neutral'"
                :variant="hasActiveFilters ? 'solid' : 'outline'"
                size="md"
                @click="handleFiltersToggle">
                <template v-if="activeFilterCount > 0">
                    <UBadge color="error" class="ml-1">
                        {{ activeFilterCount }}
                    </UBadge>
                </template>
            </UButton>
        </div>

        <!-- Filter Panel -->
        <Transition name="slide-fade">
            <div
                v-if="isFilterPanelOpen"
                class="backdrop-blur-md bg-white/95 rounded-xl shadow-2xl border border-white/20 p-3 max-w-full max-h-[70vh] overflow-x-auto overflow-y-auto">
                <!-- Filter Options -->
                <div v-if="filterOptions == undefined">
                    <p>Waiting for filter options...</p>
                </div>
                <div class="flex flex-col gap-2" v-else>
                    <!-- Dynamic Filter Selects -->
                    <div class="flex flex-wrap gap-4">
                        <div
                            v-for="config in filterConfigs"
                            :key="config.key"
                            class="flex flex-col gap-2 min-w-50 flex-1 max-w-70">
                            <label class="text-xs font-medium text-neutral-600">
                                {{ config.label }}
                            </label>

                            <!-- Existing selections -->
                            <div
                                v-for="(selection, index) in activeSelections[
                                    config.key as keyof ActiveSelections
                                ]"
                                :key="`${config.key}-${index}`"
                                class="flex gap-2 items-center">
                                <USelectMenu
                                    :virtualize="{
                                        estimateSize: 48, // estimated height per item
                                        overscan: 12, // items to render outside viewport
                                    }"
                                    :model-value="
                                        selection > 0 ? selection : undefined
                                    "
                                    :items="
                                        getAvailableItems(
                                            config.optionsKey,
                                            config.key as keyof ActiveSelections,
                                            index,
                                        )
                                    "
                                    :default-open="selection > 0 ? false : true"
                                    value-key="value"
                                    :placeholder="config.placeholder"
                                    :search-input="{
                                        placeholder: 'Szukaj...',
                                        icon: 'i-mdi-magnify',
                                        autofocus: false,
                                    }"
                                    size="sm"
                                    :ui="{
                                        content: 'min-w-[300px]',
                                        itemLabel: 'whitespace-normal',
                                        item: 'items-start',
                                    }"
                                    class="flex-1 w-96"
                                    @update:model-value="
                                        (val: number) =>
                                            (activeSelections[
                                                config.key as keyof ActiveSelections
                                            ][index] = val)
                                    " />
                                <UButton
                                    icon="i-mdi-close"
                                    color="error"
                                    variant="ghost"
                                    size="xs"
                                    @click="
                                        activeSelections[
                                            config.key as keyof ActiveSelections
                                        ].splice(index, 1)
                                    " />
                            </div>

                            <!-- Add button -->
                            <UButton
                                v-if="
                                    canAddMore(
                                        config.optionsKey,
                                        config.key as keyof ActiveSelections,
                                    )
                                "
                                icon="i-mdi-plus"
                                :label="
                                    activeSelections[
                                        config.key as keyof ActiveSelections
                                    ].length === 0
                                        ? config.placeholder
                                        : 'Dodaj kolejny'
                                "
                                color="neutral"
                                variant="ghost"
                                size="sm"
                                class="w-full"
                                @click="
                                    activeSelections[
                                        config.key as keyof ActiveSelections
                                    ].push(-1)
                                " />
                        </div>
                    </div>

                    <!-- Score Range Section -->
                    <div
                        class="bg-neutral-50 rounded-lg p-2 flex flex-row flex-wrap gap-x-6 gap-y-2 items-center justify-center">
                        <div class="flex items-center gap-1.5">
                            <UIcon
                                name="i-mdi-star"
                                class="text-amber-500 size-4" />
                            <span class="text-sm font-medium text-neutral-600"
                                >Punkty (0-100)</span
                            >
                        </div>
                        <div class="flex items-center gap-4">
                            <div class="flex items-center gap-1">
                                <span class="text-xs text-neutral-500"
                                    >Min</span
                                >
                                <UInputNumber
                                    v-model="min_score"
                                    :min="0"
                                    :max="100"
                                    size="sm"
                                    placeholder="0"
                                    class="w-25" />
                            </div>
                            <span class="text-neutral-400 text-xs">—</span>
                            <div class="flex items-center gap-1">
                                <span class="text-xs text-neutral-500"
                                    >Max</span
                                >
                                <UInputNumber
                                    v-model="max_score"
                                    placeholder="100"
                                    size="sm"
                                    :min="0"
                                    :max="100"
                                    class="w-25" />
                            </div>
                        </div>
                    </div>

                    <!-- Actions -->
                    <div
                        class="flex justify-between items-center pt-2 border-t border-neutral-200">
                        <UButton
                            v-if="hasActiveFilters"
                            icon="i-mdi-close-circle"
                            label="Wyczyść filtry"
                            color="error"
                            variant="ghost"
                            size="md"
                            @click="handleClearFilters" />
                        <div v-else />

                        <UButton
                            icon="i-mdi-magnify"
                            size="md"
                            label="Szukaj"
                            color="primary"
                            @click="handleSearch" />
                    </div>
                </div>
            </div>
        </Transition>
    </div>
    <div
        v-if="isFilterPanelOpen"
        class="fixed inset-0 bg-black opacity-25 z-10 md:hidden"
        @click="isFilterPanelOpen = false" />
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
</style>
