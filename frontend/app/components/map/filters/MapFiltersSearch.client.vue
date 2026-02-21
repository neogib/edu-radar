<script setup lang="ts">
import { useMap } from "@indoorequal/vue-maplibre-gl"
import { watchDebounced } from "@vueuse/core"
import { MAP_CONFIG } from "~/constants/mapConfig"
import { PHOTON_CONFIG } from "~/constants/photon"
import type {
    MapSearchSuggestion,
    PhotonSearchSuggestion,
} from "~/types/mapSearch"
import type { SzkolaPublicShortWithMiejscowosc } from "~/types/schools"

const emit = defineEmits<{
    close: []
    filterPanelClosed: []
    focusChange: [focused: boolean]
}>()

const mapInstance = useMap(MAP_CONFIG.mapKey)
const { $api } = useNuxtApp()

const { q, filters, setSearchQuery } = useSchoolFilters()
const { fetchPhotonSuggestions } = usePhotonGeocoding()

// Search state
const searchQuery = ref(q.value || "")
const isSearchFocused = ref(false)
const isSearchExpanded = ref(!!q.value)
const searchSuggestions = shallowRef<MapSearchSuggestion[]>([])
const searchInput = useTemplateRef("searchInput")
const highlightedIndex = ref(-1)
const suggestionsListRef = useTemplateRef("suggestionsList")
const preserveSearchInputOnQClear = ref(false)
let currentSuggestionRequestId = 0

watch(q, (newQ) => {
    if (!newQ && preserveSearchInputOnQClear.value) {
        preserveSearchInputOnQClear.value = false
        return
    }

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

const setSearchFocused = (focused: boolean) => {
    isSearchFocused.value = focused
    emit("focusChange", focused)
}

const collapseSearch = () => {
    // Only collapse if search is empty
    if (searchQuery.value.trim().length === 0) {
        isSearchExpanded.value = false
        setSearchFocused(false)
    }
}

const handleSearchButtonClick = async () => {
    if (!isSearchExpanded.value) {
        expandSearch()
    } else {
        // when search is expanded, submit query
        await submitQuery()
        emit("close")
    }
}

const handleFocus = () => {
    setSearchFocused(true)

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
        void fetchSuggestions(newSearch)
    },
    { debounce: 300, immediate: true },
)

const fetchSuggestions = async (query: string) => {
    const requestId = ++currentSuggestionRequestId

    if (!query || query.length < 2) {
        searchSuggestions.value = []
        highlightedIndex.value = -1
        return
    }

    try {
        const schools = await $api<SzkolaPublicShortWithMiejscowosc[]>(
            "/schools/live",
            {
                query: {
                    ...filters.value,
                    q: query,
                    limit: PHOTON_CONFIG.schoolSuggestionLimit,
                },
            },
        )

        if (requestId !== currentSuggestionRequestId) {
            return
        }

        let photonSuggestions: PhotonSearchSuggestion[] = []
        if (schools.length < PHOTON_CONFIG.fallbackThreshold) {
            photonSuggestions = await fetchPhotonSuggestions(query)
        }

        if (requestId !== currentSuggestionRequestId) {
            return
        }

        searchSuggestions.value = [
            ...schools.map((school) => ({
                kind: "school" as const,
                key: `school-${school.id}`,
                school,
            })),
            ...photonSuggestions,
        ]
        highlightedIndex.value = -1
    } catch (e) {
        console.error("Error fetching suggestions", e)
        searchSuggestions.value = []
        highlightedIndex.value = -1
    }
}

const submitQuery = async () => {
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
            icon: "i-mdi-info",
        })
        return
    }

    // trigger search with new query
    await setSearchQuery(trimmedQuery)
}

const handleSelectSuggestion = async (suggestion: MapSearchSuggestion) => {
    if (suggestion.kind === "school") {
        const school = suggestion.school
        // trigger search with new query
        q.value = school.nazwa
        searchQuery.value = school.nazwa

        setSearchFocused(false)
        highlightedIndex.value = -1

        // Fly to school
        const map = mapInstance.map as maplibregl.Map
        map.flyTo({
            center: [school.longitude, school.latitude],
            zoom: PHOTON_CONFIG.schoolFlyToZoom,
        })
        moveFocusToMap()
        return
    }

    setSearchFocused(false)
    highlightedIndex.value = -1

    const map = mapInstance.map as maplibregl.Map
    map.flyTo({
        center: suggestion.coordinates,
        zoom: PHOTON_CONFIG.photonFlyToZoom,
    })
    moveFocusToMap()

    if (q.value) {
        preserveSearchInputOnQClear.value = true
        await setSearchQuery(undefined)
    }

    emit("close")
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
        const selected = searchSuggestions.value[highlightedIndex.value]
        if (selected) {
            void handleSelectSuggestion(selected)
        }
    } else if (e.key === "Escape") {
        setSearchFocused(false)
        highlightedIndex.value = -1
    }
}

const blur = () => {
    setSearchFocused(false)
}

const moveFocusToMap = () => {
    searchInput.value?.inputRef?.blur?.()

    const map = mapInstance.map as maplibregl.Map | undefined
    const canvas = map?.getCanvas()
    if (!canvas) return

    // Ensure canvas is keyboard-focusable before focusing it.
    if (!canvas.hasAttribute("tabindex")) {
        canvas.setAttribute("tabindex", "0")
    }

    canvas.focus({ preventScroll: true })
}

defineExpose({
    collapseSearch,
    blur,
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
                v-for="(suggestion, index) in searchSuggestions"
                :key="suggestion.key"
                :class="[
                    'px-3 py-2 cursor-pointer flex flex-col gap-0.5 transition-colors',
                    highlightedIndex === index
                        ? 'bg-primary/10'
                        : 'hover:bg-elevated',
                ]"
                @click="void handleSelectSuggestion(suggestion)"
                @mouseenter="highlightedIndex = index">
                <template v-if="suggestion.kind === 'school'">
                    <span class="text-sm font-medium text-highlighted">{{
                        suggestion.school.nazwa
                    }}</span>
                    <div class="flex gap-2 items-center text-xs text-muted">
                        <span>{{ suggestion.school.status }}</span>
                        <span>•</span>
                        <span>{{ suggestion.school.miejscowosc }}</span>
                    </div>
                </template>
                <template v-else>
                    <span class="text-sm font-medium text-highlighted">{{
                        suggestion.label
                    }}</span>
                    <div class="flex gap-2 items-center text-xs text-muted">
                        <UIcon name="i-mdi-map-marker" class="size-3.5" />
                        <span>{{ suggestion.subtitle }}</span>
                    </div>
                </template>
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
