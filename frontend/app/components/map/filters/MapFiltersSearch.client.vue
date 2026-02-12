<script setup lang="ts">
import { useMap } from "@indoorequal/vue-maplibre-gl"
import { watchDebounced } from "@vueuse/core"
import { MAP_CONFIG } from "~/constants/mapConfig"
import type { SzkolaPublicShort } from "~/types/schools"

const emit = defineEmits<{
    panelClose: []
    filterPanelClosed: []
}>()

const mapInstance = useMap(MAP_CONFIG.mapKey)

const { q, filters } = useSchoolFilters()
const { fetchSchools } = useSchools()
const { debouncedLoadRemainingSchools } = useSchoolGeoJSONSource()

// Search state
const searchQuery = ref(q.value || "")
const isSearchFocused = ref(false)
const isSearchExpanded = ref(!!q.value)
const searchSuggestions = shallowRef<SzkolaPublicShort[]>([])
const searchInput = useTemplateRef("searchInput")
const highlightedIndex = ref(-1)
const suggestionsListRef = useTemplateRef("suggestionsList")

watch(q, (newQ) => {
    if (newQ !== searchQuery.value) {
        searchQuery.value = newQ || ""
    }
    if (newQ && !isSearchExpanded.value) {
        isSearchExpanded.value = true
    }
})

defineShortcuts({
    "/": () => {
        expandSearch()
    },
})

const expandSearch = () => {
    isSearchExpanded.value = true
}

const collapseSearch = () => {
    // Only collapse if search is empty
    if (searchQuery.value.trim().length === 0) {
        isSearchExpanded.value = false
        isSearchFocused.value = false
    }
}

const handleSearchButtonClick = () => {
    if (!isSearchExpanded.value) {
        expandSearch()
    } else {
        // when search is expanded, submit query
        submitQuery()
        emit("panelClose")
    }
}

const handleFocus = () => {
    isSearchFocused.value = true

    // if filters were opened, close them
    emit("filterPanelClosed")
}

const clearSearchQuery = () => {
    searchQuery.value = ""
    searchSuggestions.value = []
    if (q.value) {
        q.value = ""
    }

    // focus input
    searchInput.value?.inputRef?.focus()
}

watchDebounced(
    searchQuery,
    (newSearch: string) => {
        fetchSuggestions(newSearch)
    },
    { debounce: 300, immediate: true },
)

const fetchSuggestions = async (query: string) => {
    if (!query || query.length < 2) {
        searchSuggestions.value = []
        highlightedIndex.value = -1
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
        highlightedIndex.value = -1
    } catch (e) {
        console.error("Error fetching suggestions", e)
        searchSuggestions.value = []
        highlightedIndex.value = -1
    }
}

const submitQuery = () => {
    const trimmedQuery = searchQuery.value.trim()
    // check if query changed
    if (trimmedQuery === q.value || (trimmedQuery.length === 0 && !q.value))
        return

    // Validate length
    if (trimmedQuery.length > 0 && trimmedQuery.length < 2) {
        useToast().add({
            title: "Zapytanie za krótkie",
            description: "Wpisz co najmniej 2 znaki",
            color: "info",
            icon: "i-mdi-alert",
        })
        return
    }

    // trigger search with new query
    q.value = trimmedQuery
}

const handleSelectSuggestion = (school: SzkolaPublicShort) => {
    // trigger search with new query
    q.value = school.nazwa
    searchQuery.value = school.nazwa

    isSearchFocused.value = false
    highlightedIndex.value = -1

    // if schools was not within bounds, we need one more request
    debouncedLoadRemainingSchools()

    // Fly to school
    const map = mapInstance.map as maplibregl.Map
    map.flyTo({
        center: [school.longitude, school.latitude],
        zoom: 16,
    })
}

const scrollToSelected = () => {
    nextTick(() => {
        if (!suggestionsListRef.value || highlightedIndex.value < 0) return

        const selectedElement = suggestionsListRef.value.children[
            highlightedIndex.value
        ] as HTMLElement
        if (selectedElement) {
            selectedElement.scrollIntoView({
                behavior: "smooth",
                block: "nearest",
            })
        }
    })
}

const handleKeyDown = (e: KeyboardEvent) => {
    if (!isSearchFocused.value || searchSuggestions.value.length === 0) {
        return
    }

    if (e.key === "ArrowDown") {
        e.preventDefault()
        highlightedIndex.value =
            (highlightedIndex.value + 1) % searchSuggestions.value.length
        scrollToSelected()
    } else if (e.key === "ArrowUp") {
        e.preventDefault()
        highlightedIndex.value =
            (highlightedIndex.value - 1 + searchSuggestions.value.length) %
            searchSuggestions.value.length
        scrollToSelected()
    } else if (e.key === "Enter" && highlightedIndex.value >= 0) {
        e.preventDefault()
        handleSelectSuggestion(
            searchSuggestions.value[
                highlightedIndex.value
            ] as SzkolaPublicShort,
        )
    } else if (e.key === "Escape") {
        isSearchFocused.value = false
        highlightedIndex.value = -1
    }
}

const blur = () => {
    isSearchFocused.value = false
}

defineExpose({
    collapseSearch,
    blur,
    isSearchFocused,
})
</script>
<template>
    <!-- Search Icon Button (always visible, changes function based on state) -->
    <UButton
        icon="i-mdi-magnify"
        color="neutral"
        variant="outline"
        size="md"
        :aria-label="isSearchExpanded ? 'Submit search' : 'Open search'"
        @click.stop="handleSearchButtonClick" />

    <!-- Search Input (visible when expanded) -->
    <form v-show="isSearchExpanded" class="w-md" @submit.prevent="submitQuery">
        <UInput
            ref="searchInput"
            v-model="searchQuery"
            :autofocus="true"
            placeholder="Szukaj szkoły..."
            size="md"
            minlength="2"
            class="w-full"
            :ui="{ base: 'pe-13', trailing: 'pe-2' }"
            @focus="handleFocus"
            @keydown="handleKeyDown">
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
    </form>

    <!-- Search Suggestions Dropdown (spans full width) -->
    <div
        v-show="isSearchFocused && searchSuggestions.length > 0"
        class="absolute top-full mt-1 z-50 rounded-lg border border-default bg-default py-1 shadow-xl">
        <div ref="suggestionsList" class="max-h-60 overflow-y-auto">
            <div
                v-for="(school, index) in searchSuggestions"
                :key="school.id"
                :class="[
                    'px-3 py-2 cursor-pointer flex flex-col gap-0.5 transition-colors',
                    highlightedIndex === index
                        ? 'bg-primary/10'
                        : 'hover:bg-elevated',
                ]"
                @click="handleSelectSuggestion(school)"
                @mouseenter="highlightedIndex = index">
                <span class="text-sm font-medium text-highlighted">{{
                    school.nazwa
                }}</span>
                <div class="flex gap-2 items-center text-xs text-muted">
                    <span>{{ school.status }}</span>
                    <span>•</span>
                    <span>{{ school.typ }}</span>
                </div>
            </div>
        </div>
        <div
            class="px-3 py-2 bg-default border-t border-default flex items-center gap-3 text-xs text-muted">
            <span class="flex items-center gap-1">
                <UIcon name="i-mdi-arrow-up" class="size-3.5" />
                <UIcon name="i-mdi-arrow-down" class="size-3.5" />
                Nawiguj
            </span>
            <span class="flex items-center gap-1">
                <UIcon name="i-mdi-keyboard-return" class="size-3.5" />
                Wybierz
            </span>
        </div>
    </div>
</template>

<style scoped>
@reference "tailwindcss";

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
