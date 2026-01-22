import { SELECTION_KEYS, type FiltersParamsWihtoutBbox } from "~/types/filters"
import { useRouteQuery } from "@vueuse/router"

// normalize array to filter values lower than 1
const normalizeArray = (arr: number[] | undefined): string[] | undefined => {
    if (!arr || arr.length === 0) return undefined
    const normalized = arr.filter((n) => n > 0).map(String)
    return normalized.length > 0 ? normalized : undefined
}

// Helper for array filters (like type, status, category)
const createArrayFilter = (key: string) => {
    return useRouteQuery<string[] | undefined, number[] | undefined>(
        key,
        undefined,
        {
            transform: {
                get: (value) => parseArrayOfIds(value),
                set: (value) => normalizeArray(value),
            },
        },
    )
}

// Helper for number filters (like scores)
const useNumberFilter = (key: string) => {
    return useRouteQuery<number | undefined>(key, undefined)
}

export const useSchoolFilters = () => {
    // Array filters
    const type = createArrayFilter("type")
    const status = createArrayFilter("status")
    const category = createArrayFilter("category")
    const vocational_training = createArrayFilter("vocational_training")

    // Number filters
    const min_score = useNumberFilter("min_score")
    const max_score = useNumberFilter("max_score")

    // Search query z minLength = 2
    const q = useRouteQuery<string | undefined>("q", undefined, {
        transform: {
            set: (value) => {
                if (!value || value.trim().length < 2) return undefined
                return value.trim()
            },
        },
    })

    // all in one just for reading
    const filters = computed<FiltersParamsWihtoutBbox>(() => ({
        type: type.value,
        status: status.value,
        category: category.value,
        vocational_training: vocational_training.value,
        min_score: min_score.value,
        max_score: max_score.value,
        q: q.value,
    }))

    // Count total active filters excluding search query
    const totalActiveFilters = computed(() => {
        let count = 0
        // iterate over SELECTION_KEYS which represent array filters
        for (const key of SELECTION_KEYS) {
            count += filters.value[key]?.length ?? 0
        }
        // Check number filters
        if (filters.value.min_score !== undefined) count++
        if (filters.value.max_score !== undefined) count++
        return count
    })

    const hasActiveFilters = computed(() => totalActiveFilters.value > 0)

    const resetFilters = () => {
        type.value = undefined
        status.value = undefined
        category.value = undefined
        vocational_training.value = undefined
        min_score.value = undefined
        max_score.value = undefined
        q.value = undefined
    }

    return {
        type,
        status,
        category,
        vocational_training,
        min_score,
        max_score,
        q,

        // Computed
        filters,
        hasActiveFilters,
        totalActiveFilters,

        // Actions
        resetFilters,
    }
}
