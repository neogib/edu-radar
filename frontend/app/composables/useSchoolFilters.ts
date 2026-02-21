import { SELECTION_KEYS, type FiltersParamsWihtoutBbox } from "~/types/filters"
import type { LocationQueryValue } from "vue-router"
import { parseArrayOfIds, parseNumber, parseQueryString } from "~/utils/parsers"

type RouteQueryValue = LocationQueryValue | LocationQueryValue[] | undefined

// normalize array to filter values lower than 1
const normalizeArray = (arr: number[] | undefined): string[] | undefined => {
    if (!arr || arr.length === 0) return undefined
    const normalized = arr.filter((n) => n > 0).map(String)
    return normalized.length > 0 ? normalized : undefined
}

export const useSchoolFilters = () => {
    const route = useRoute()

    const updateQuery = async (updates: Record<string, RouteQueryValue>) => {
        const query = Object.fromEntries(
            Object.entries({ ...route.query, ...updates }).filter(
                ([, value]) => value !== undefined,
            ),
        )

        await navigateTo({ query })
    }

    const createComputedFilter = <T, S extends RouteQueryValue>(
        key: string,
        parser: (v: RouteQueryValue) => T,
        serializer: (v: T) => S,
    ) =>
        computed({
            get: () => parser(route.query[key]),
            set: (v) => {
                void updateQuery({ [key]: serializer(v) })
            },
        })

    // Array filters
    const type = createComputedFilter("type", parseArrayOfIds, normalizeArray)
    const status = createComputedFilter(
        "status",
        parseArrayOfIds,
        normalizeArray,
    )
    const category = createComputedFilter(
        "category",
        parseArrayOfIds,
        normalizeArray,
    )
    const career = createComputedFilter(
        "career",
        parseArrayOfIds,
        normalizeArray,
    )

    // Number filters
    const numberSerializer = (v: number | undefined) =>
        v !== undefined ? String(v) : undefined
    const min_score = createComputedFilter(
        "min_score",
        parseNumber,
        numberSerializer,
    )
    const max_score = createComputedFilter(
        "max_score",
        parseNumber,
        numberSerializer,
    )

    // Search query
    const q = createComputedFilter("q", parseQueryString, (v) =>
        parseQueryString(v),
    )

    // all in one just for reading
    const filters = computed<FiltersParamsWihtoutBbox>(() => ({
        type: type.value,
        status: status.value,
        category: category.value,
        career: career.value,
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

    const filterKey = computed(() => JSON.stringify(filters.value))

    const resetFilters = () => {
        void updateQuery({
            type: undefined,
            status: undefined,
            category: undefined,
            career: undefined,
            min_score: undefined,
            max_score: undefined,
            q: undefined,
        })
    }

    return {
        type,
        status,
        category,
        career,
        min_score,
        max_score,
        q,

        // Computed
        filters,
        filterKey,
        hasActiveFilters,
        totalActiveFilters,

        // Actions
        resetFilters,
    }
}
