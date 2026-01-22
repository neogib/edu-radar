<script setup lang="ts">
import type { FiltersOptions, SzkolaPublicShort } from "~/types/schools"
import { useMap } from "@indoorequal/vue-maplibre-gl"
import { watchDebounced } from "@vueuse/core"

const { map } = useMap("mainMap")

const { filterData } = useFilterData()

// get filters from route.query
const {
    q,
    min_score,
    max_score,
    filters,
    hasActiveFilters,
    totalActiveFilters,
    resetFilters,
} = useSchoolFilters()

// Filter panel visibility
const isFilterPanelOpen = ref(false)

// Get available items (not already selected) for a filter
const getAvailableItems = (
    options: FiltersOptions,
    selectedValues: number[] | undefined,
    currentIndex?: number,
) => {
    const allItems = options ?? []
    const items = allItems.map((option) => ({
        label: option.nazwa,
        value: option.id,
    })) // for select menu component

    if (!selectedValues || selectedValues.length === 0) {
        return items
    }

    // Keep items not selected, OR the current selection at this index
    return items.filter(
        (item) =>
            !selectedValues.includes(item.value) ||
            (currentIndex !== undefined &&
                selectedValues[currentIndex] === item.value),
    )
}

// Check if we can add more selections (more options available)
const canAddMore = (
    optionsKey: FiltersOptions,
    userSelections: number[] | undefined,
) => {
    if (!userSelections || userSelections.length === 0) {
        return true
    }
    const numberOfTotalOptions = optionsKey.length

    return userSelections.length < numberOfTotalOptions
}

// Search state
const searchQuery = ref(filters.value.q || "")
const searchSuggestions = shallowRef<SzkolaPublicShort[]>([])
const searchInputFocused = ref(false)

const handleFocus = () => {
    searchInputFocused.value = true
    isFilterPanelOpen.value = false
}

watchDebounced(searchQuery, (newSearch) => {
    fetchSuggestions(newSearch)
})

const fetchSuggestions = async (query: string) => {
    if (!query || query.length < 2) {
        searchSuggestions.value = []
        return
    }

    try {
        const { fetchSchools } = useSchools()
        searchSuggestions.value = await fetchSchools({
            query: {
                ...filters.value,
                q: query,
            },
        })
    } catch (e) {
        console.error("Error fetching suggestions", e)
        searchSuggestions.value = []
    }
}

// Handle search/filters submit
const handleSearch = async () => {
    isFilterPanelOpen.value = false
    q.value = searchQuery.value.trim() || undefined
    // get new schools for the whole map area
}

const handleSelectSuggestion = (school: SzkolaPublicShort) => {
    searchQuery.value = school.nazwa

    // Fly to school
    if (map) {
        console.log(`Map: ${map}`)
        map.flyTo({
            center: [
                school.geolokalizacja_longitude,
                school.geolokalizacja_latitude,
            ],
            zoom: 16,
        })
    }

    // trigger search with new query
    handleSearch()
}
</script>

<template>
    <div class="absolute top-20 left-2 z-20 flex flex-col gap-2 max-w-[95%]">
        <!-- Search Bar -->
        <div class="flex gap-2 items-center">
            <form
                class="flex-1 min-w-60 max-w-100 relative"
                @submit.prevent="handleSearch">
                <UInput
                    v-model="searchQuery"
                    icon="i-mdi-magnify"
                    placeholder="Szukaj szkoły..."
                    size="md"
                    :ui="{ root: 'w-full' }"
                    minlength="2"
                    @focus="handleFocus"
                    @blur="searchInputFocused = false" />

                <!-- Search Suggestions Dropdown -->
                <div
                    v-if="
                        searchInputFocused &&
                        searchSuggestions.length > 0 &&
                        !isFilterPanelOpen
                    "
                    class="absolute top-full mt-1 w-full bg-white rounded-lg shadow-xl border border-gray-100 max-h-60 overflow-y-auto z-50 py-1">
                    <div
                        v-for="school in searchSuggestions"
                        :key="school.id"
                        class="px-3 py-2 hover:bg-gray-50 cursor-pointer flex flex-col gap-0.5"
                        @click="handleSelectSuggestion(school)">
                        <span class="text-sm font-medium text-gray-900">{{
                            school.nazwa
                        }}</span>
                        <div
                            class="flex gap-2 items-center text-xs text-gray-500">
                            <span>{{
                                school.status_publicznoprawny.nazwa
                            }}</span>
                            <span>•</span>
                            <span>{{ school.typ.nazwa }}</span>
                        </div>
                    </div>
                </div>
            </form>

            <!-- Filter Toggle Button -->
            <UButton
                :icon="isFilterPanelOpen ? 'i-mdi-filter-off' : 'i-mdi-filter'"
                :color="hasActiveFilters ? 'primary' : 'neutral'"
                :variant="hasActiveFilters ? 'solid' : 'outline'"
                size="md"
                @click="isFilterPanelOpen = !isFilterPanelOpen">
                <template v-if="totalActiveFilters > 0">
                    <UBadge color="error" class="ml-1">
                        {{ totalActiveFilters }}
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
                <div class="flex flex-col gap-2">
                    <!-- Dynamic Filter Selects -->
                    <div class="flex flex-wrap gap-4">
                        <div
                            v-for="config in filterData"
                            :key="config.key"
                            class="flex flex-col gap-2 min-w-50 flex-1 max-w-70">
                            <label class="text-xs font-medium text-neutral-600">
                                {{ config.label }}
                            </label>

                            <!-- Existing selections -->
                            <div
                                v-for="(selection, index) in config.queryParam
                                    .value ?? []"
                                :key="`${config.key}-${index}`"
                                class="flex gap-2 items-center">
                                <USelectMenu
                                    :virtualize="{
                                        estimateSize: 48, // estimated height per item
                                        overscan: 12, // items to render outside viewport
                                    }"
                                    :model-value="selection"
                                    :items="
                                        getAvailableItems(
                                            config.options,
                                            config.queryParam.value,
                                            index,
                                        )
                                    "
                                    value-key="value"
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
                                            ((
                                                config.queryParam
                                                    .value as number[]
                                            )[index] = // config.queryparam can't be undefined when this selctmenu shows up
                                                val)
                                    " />
                                <UButton
                                    icon="i-mdi-close"
                                    color="error"
                                    variant="ghost"
                                    size="xs"
                                    @click="
                                        (
                                            config.queryParam.value as number[]
                                        ).splice(index, 1)
                                    " />
                            </div>

                            <div
                                v-if="config.addingsState"
                                class="flex gap-2 items-center">
                                <USelectMenu
                                    :model-value="undefined"
                                    :items="
                                        getAvailableItems(
                                            config.options,
                                            config.queryParam.value,
                                        )
                                    "
                                    value-key="value"
                                    placeholder="Wybierz z listy..."
                                    searchable
                                    default-open
                                    class="flex-1 w-96"
                                    @update:model-value="
                                        (val) => {
                                            config.queryParam.value =
                                                config.queryParam.value ?? []
                                            config.queryParam.value.push(val)
                                            config.addingsState = false
                                        }
                                    " />
                                <UButton
                                    icon="i-mdi-close"
                                    color="neutral"
                                    variant="ghost"
                                    size="xs"
                                    @click="config.addingsState = false" />
                            </div>
                            <!-- Add button -->
                            <UButton
                                v-if="
                                    !config.addingsState &&
                                    canAddMore(
                                        config.options,
                                        config.queryParam.value,
                                    )
                                "
                                icon="i-mdi-plus"
                                :label="
                                    config.queryParam.value?.length === 0
                                        ? config.placeholder
                                        : 'Dodaj kolejny'
                                "
                                color="neutral"
                                variant="ghost"
                                size="sm"
                                class="w-full"
                                @click="config.addingsState = true" />
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
                            @click="resetFilters" />
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
