<script setup lang="ts">
import type { FiltersOptions, SzkolaPublicShort } from "~/types/schools"
import { useMap } from "@indoorequal/vue-maplibre-gl"
import { useDebounceFn, watchDebounced } from "@vueuse/core"
import type { Map } from "maplibre-gl"

const mapInstance = useMap("mainMap")

const { filterData } = await useFilterData()

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

const { debouncedLoadRemainingSchools } = useSchoolGeoJSONSource()
const { fetchSchools } = useSchools()

// Filter panel visibility
const isFilterPanelOpen = ref(false)
const filterKeyChanged = ref(false)

// Search state
const searchQuery = ref(filters.value.q || "")
const searchSuggestions = shallowRef<SzkolaPublicShort[]>([])
const searchInputFocused = ref(false)
const searchInput = useTemplateRef("searchInput")

defineShortcuts({
    "/": () => {
        searchInput.value?.inputRef?.focus()
    },
})

watch(totalActiveFilters, () => {
    filterKeyChanged.value = true
})

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

// Check if we can add more selections (more options still available)
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

    // panel closed, set addingState to false for all filters
    filterData.forEach((filter) => {
        filter.addingState = false
    })

    handlePanelSubmit()
}

const handleFocus = () => {
    searchInputFocused.value = true

    // if filters were opened, close them
    isFilterPanelOpen.value = false
}

const clearSearchQuery = () => {
    searchQuery.value = ""
    if (q.value) {
        q.value = ""
    }

    // load rest of schools
    debouncedLoadRemainingSchools()
}

const submitQuery = () => {
    // trigger search with new query
    q.value = searchQuery.value.trim()

    // note the change
    filterKeyChanged.value = true
}

watchDebounced(
    searchQuery,
    (newSearch) => {
        fetchSuggestions(newSearch)
    },
    { debounce: 300, immediate: true },
)

const fetchSuggestions = async (query: string) => {
    if (!query || query.length < 2) {
        searchSuggestions.value = []
        return
    }

    try {
        // when fetching suggestions, don't include other filters, because it can be confusing for users
        searchSuggestions.value = await fetchSchools({
            query: {
                ...filters.value,
                q: searchQuery.value,
                limit: 50, // options are in dropdown, so limit to reasonable number
            },
        })
    } catch (e) {
        console.error("Error fetching suggestions", e)
        searchSuggestions.value = []
    }
}

const handleSelectSuggestion = (school: SzkolaPublicShort) => {
    // trigger search with new query
    q.value = school.nazwa
    searchQuery.value = school.nazwa

    searchInputFocused.value = false

    // if schools was not within bounds, we need one more request
    debouncedLoadRemainingSchools()

    // Fly to school
    const map = mapInstance.map as Map
    map.flyTo({
        center: [
            school.geolokalizacja_longitude,
            school.geolokalizacja_latitude,
        ],
        zoom: 16,
    })
}

const handlePanelSubmit = () => {
    // trigger search if filters changed
    if (!filterKeyChanged.value) {
        return
    }
    filterKeyChanged.value = false

    debouncedLoadRemainingSchools()
}
</script>

<template>
    <div class="absolute top-20 left-2 z-20 flex flex-col gap-2 max-w-[95%]">
        <!-- Search Bar -->
        <div class="flex gap-2 items-center">
            <form class="relative" @submit.prevent="submitQuery">
                <UInput
                    v-model="searchQuery"
                    ref="searchInput"
                    icon="i-mdi-magnify"
                    placeholder="Szukaj szkoły..."
                    size="md"
                    minlength="2"
                    :ui="{ base: 'pe-13', trailing: 'pe-2' }"
                    @focus="handleFocus">
                    <template #trailing>
                        <UButton
                            v-if="searchQuery?.length"
                            color="neutral"
                            variant="link"
                            size="sm"
                            icon="i-lucide-circle-x"
                            aria-label="Clear input"
                            @click="clearSearchQuery" />
                        <UKbd value="/" />
                    </template>
                </UInput>

                <!-- Search Suggestions Dropdown -->
                <div
                    v-if="searchInputFocused && searchSuggestions.length > 0"
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
                @click="handlePanelToggle">
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
                            v-for="filtersData in filterData"
                            :key="filtersData.key"
                            class="flex flex-col gap-2 min-w-50 flex-1 max-w-75">
                            <label class="text-xs font-medium text-neutral-600">
                                {{ filtersData.label }}
                            </label>

                            <!-- Existing selections -->
                            <div
                                v-for="(
                                    selection, index
                                ) in filtersData.queryParam ?? []"
                                :key="`${filtersData.key}-${index}`"
                                class="flex gap-2 items-center">
                                <USelectMenu
                                    :virtualize="{
                                        estimateSize: 48, // estimated height per item
                                        overscan: 12, // items to render outside viewport
                                    }"
                                    :model-value="selection"
                                    :items="
                                        getAvailableItems(
                                            filtersData.options,
                                            filtersData.queryParam,
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
                                        content: 'min-w-[320px]',
                                        itemLabel: 'whitespace-normal',
                                    }"
                                    class="flex-1 min-w-0"
                                    @update:model-value="
                                        (val: number) => {
                                            const current = [
                                                ...(filtersData.queryParam as number[]),
                                            ]
                                            current[index] = val
                                            filtersData.queryParam = current
                                        }
                                    " />
                                <UButton
                                    icon="i-mdi-close"
                                    color="error"
                                    variant="ghost"
                                    size="xs"
                                    @click="
                                        () => {
                                            const current = [
                                                ...(filtersData.queryParam as number[]),
                                            ]
                                            current.splice(index, 1)
                                            filtersData.queryParam = current
                                        }
                                    " />
                            </div>

                            <div
                                v-if="filtersData.addingState"
                                class="flex gap-2 items-center">
                                <USelectMenu
                                    :virtualize="{
                                        estimateSize: 48, // estimated height per item
                                        overscan: 12, // items to render outside viewport
                                    }"
                                    :items="
                                        getAvailableItems(
                                            filtersData.options,
                                            filtersData.queryParam,
                                        )
                                    "
                                    :search-input="{
                                        placeholder: 'Szukaj...',
                                        icon: 'i-mdi-magnify',
                                        autofocus: false,
                                    }"
                                    size="sm"
                                    :ui="{
                                        content: 'min-w-[320px]',
                                        itemLabel: 'whitespace-normal',
                                    }"
                                    :model-value="undefined"
                                    value-key="value"
                                    placeholder="Wybierz z listy..."
                                    default-open
                                    class="flex-1 min-w-0"
                                    @update:model-value="
                                        (val) => {
                                            const current = [
                                                ...(filtersData.queryParam ??
                                                    []),
                                            ]
                                            current.push(val)
                                            filtersData.queryParam = current
                                            filtersData.addingState = false
                                        }
                                    " />
                                <UButton
                                    icon="i-mdi-close"
                                    color="neutral"
                                    variant="ghost"
                                    size="xs"
                                    @click="filtersData.addingState = false" />
                            </div>
                            <!-- Add button -->
                            <UButton
                                v-if="
                                    !filtersData.addingState &&
                                    canAddMore(
                                        filtersData.options,
                                        filtersData.queryParam,
                                    )
                                "
                                icon="i-mdi-plus"
                                :label="
                                    !filtersData.queryParam ||
                                    filtersData.queryParam.length === 0
                                        ? filtersData.placeholder
                                        : 'Dodaj kolejny'
                                "
                                color="neutral"
                                variant="ghost"
                                size="sm"
                                class="w-full"
                                @click="filtersData.addingState = true" />
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
                            size="sm"
                            @click="resetFilters" />
                        <div v-else />

                        <UButton
                            icon="i-mdi-magnify"
                            size="sm"
                            label="Pokaż wyniki"
                            color="primary"
                            @click="handlePanelClose" />
                    </div>
                </div>
            </div>
        </Transition>
    </div>
    <div
        v-if="isFilterPanelOpen || searchInputFocused"
        class="fixed inset-0 bg-black opacity-25 md:opacity-15 z-10"
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
</style>
