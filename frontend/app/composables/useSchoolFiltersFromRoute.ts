import type { FiltersParamsWihtoutBbox } from "~/types/filters"

export const useSchoolFiltersFromRoute = () => {
    const route = useRoute()
    const filters = useState<FiltersParamsWihtoutBbox>("filters", () => {
        console.log("Inicjalizacja filtrów z URL...") // Zobaczysz to tylko raz
        return {
            type: parseArrayOfIds(route.query.type),
            status: parseArrayOfIds(route.query.status),
            category: parseArrayOfIds(route.query.category),
            vocational_training: parseArrayOfIds(
                route.query.vocational_training,
            ),
            min_score: parseNumber(route.query.min_score),
            max_score: parseNumber(route.query.max_score),
            q: parseQueryString(route.query.search || route.query.q),
        }
    })

    const updateFilter = (newfilters: FiltersParamsWihtoutBbox) => {
        filters.value = newfilters
        // get new schools on the map
        syncToUrl()
    }

    const syncToUrl = async () => {
        await navigateTo({ query: { ...route.query, ...filters.value } })
    }

    const resetFilters = () => {
        filters.value = {}
        // get new schools on the map
        syncToUrl()
    }

    return {
        filters,
        updateFilter,
        resetFilters,
    }
}
