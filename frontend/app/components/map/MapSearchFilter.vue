<script setup lang="ts">
import { filterConfigs } from "~/constants/filters"
import type { ActiveSelections } from "~/types/filters"
import type { FiltersResponse } from "~/types/schools"

// all filter options from api
const { data: filterOptions } = useApi<FiltersResponse>("/filters/")

// Search state
const searchQuery = ref("")

// min, max score
const min_score = ref<number | null>(null)
const max_score = ref<number | null>(null)

// Filter panel visibility
const isFilterPanelOpen = ref(false)

const activeSelections = reactive<ActiveSelections>({
    type: [],
    status: [],
    category: [],
    vocational_training: [],
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

    const validCount = userSelections.filter((v) => v > 0).length

    return validCount > 0 && validCount < totalOptions
}

// Count total active filters
const activeFilterCount = computed(() => {
    let count = 0
    for (const key of Object.keys(
        activeSelections,
    ) as (keyof ActiveSelections)[]) {
        count += activeSelections[key].filter((v) => v > 0).length
    }
    if (min_score.value !== null && min_score.value !== 0) count++
    if (max_score.value !== null && max_score.value !== 100) count++
    return count
})

const hasActiveFilters = computed(() => activeFilterCount.value > 0)

// Handle search/filters submit
const route = useRoute()
const handleSearch = async () => {
    const types_id = activeSelections.type.filter((v) => v > 0)
    const statuses_id = activeSelections.status.filter((v) => v > 0)
    const categories_id = activeSelections.category.filter((v) => v > 0)
    const vocational_trainings_id = activeSelections.vocational_training.filter(
        (v) => v > 0,
    )
    await navigateTo({
        query: {
            bbox: route.query.bbox || undefined,
            search: searchQuery.value || undefined,
            type: types_id.length > 0 ? types_id : undefined,
            status: statuses_id.length > 0 ? statuses_id : undefined,
            category: categories_id.length > 0 ? categories_id : undefined,
            vocational_training:
                vocational_trainings_id.length > 0
                    ? vocational_trainings_id
                    : undefined,
            min_score: min_score.value ?? undefined,
            max_score: max_score.value ?? undefined,
        },
    })
}

// Clear all filters
const handleClearFilters = () => {
    searchQuery.value = ""
    activeSelections.type = []
    activeSelections.status = []
    activeSelections.category = []
    activeSelections.vocational_training = []
    min_score.value = null
    max_score.value = null
}
</script>

<template>
    <div
        class="absolute top-20 left-2 z-10 flex flex-col gap-2 max-w-[calc(100vw-2rem)]">
        <!-- Search Bar -->
        <div class="flex gap-2 items-center">
            <form
                class="flex-1 min-w-60 max-w-100"
                @submit.prevent="handleSearch">
                <UInput
                    v-model="searchQuery"
                    icon="i-mdi-magnify"
                    placeholder="Szukaj szkoły..."
                    size="lg"
                    :ui="{ root: 'w-full' }" />
            </form>

            <!-- Filter Toggle Button -->
            <UButton
                :icon="isFilterPanelOpen ? 'i-mdi-filter-off' : 'i-mdi-filter'"
                :color="hasActiveFilters ? 'primary' : 'neutral'"
                :variant="hasActiveFilters ? 'solid' : 'outline'"
                size="lg"
                @click="isFilterPanelOpen = !isFilterPanelOpen">
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
                class="backdrop-blur-md bg-white/95 rounded-xl shadow-2xl border border-white/20 p-4 max-w-full overflow-x-auto">
                <!-- Filter Options -->
                <div v-if="filterOptions == undefined">
                    <p>Waiting for filter options...</p>
                </div>
                <div class="flex flex-col gap-4" v-else>
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
                                    value-key="value"
                                    :placeholder="config.placeholder"
                                    :search-input="{
                                        placeholder: 'Szukaj...',
                                        icon: 'i-mdi-magnify',
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
                        class="bg-neutral-50 rounded-lg p-3 flex flex-col gap-2 items-center justify-center">
                        <div
                            class="flex items-center justify-center gap-2 text-sm font-medium text-neutral-700">
                            <UIcon name="i-mdi-star" class="text-amber-500" />
                            <span>Zakres punktów (0-100)</span>
                        </div>
                        <div class="flex items-center gap-3">
                            <div class="flex flex-col gap-1">
                                <label class="text-xs text-neutral-500"
                                    >Min</label
                                >
                                <UInputNumber
                                    v-model="min_score"
                                    :min="0"
                                    :max="100"
                                    placeholder="0"
                                    class="w-30" />
                            </div>
                            <div class="text-neutral-400 pt-4">—</div>
                            <div class="flex flex-col gap-1">
                                <label class="text-xs text-neutral-500"
                                    >Max</label
                                >
                                <UInputNumber
                                    v-model="max_score"
                                    placeholder="100"
                                    :min="0"
                                    :max="100"
                                    class="w-30" />
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
                            @click="handleClearFilters" />
                        <div v-else />

                        <UButton
                            icon="i-mdi-magnify"
                            label="Szukaj"
                            color="primary"
                            @click="handleSearch" />
                    </div>
                </div>
            </div>
        </Transition>
    </div>
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
