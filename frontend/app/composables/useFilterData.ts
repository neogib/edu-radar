import type { ActiveSelections, FilterConfig } from "~/types/filters"
import type { FiltersOptions, FiltersResponse } from "~/types/schools"

export const useFilterData = async () => {
    const { $api } = useNuxtApp()
    const { type, status, category, career } = useSchoolFilters()

    // Use $api instead of useApi to ensure data is fetched and available directly
    // This avoids potential issues with useFetch/useApi reactivity when used inside an async composable
    const filterOptions = await $api<FiltersResponse>("/filters/")

    const createFilterData = (
        key: keyof ActiveSelections,
        queryParam: Ref<number[] | undefined>,
        label: string,
        placeholder: string,
        options: FiltersOptions,
    ): FilterConfig => {
        return {
            key,
            queryParam,
            label,
            placeholder,
            options,
            addingState: false,
        }
    }

    const filterData = reactive<FilterConfig[]>([
        createFilterData(
            "type",
            type,
            "Rodzaj szkoły",
            "Wybierz typ szkoły...",
            filterOptions.school_types || [],
        ),
        createFilterData(
            "status",
            status,
            "Publiczna / niepubliczna",
            "Wybierz status...",
            filterOptions.public_statuses || [],
        ),
        createFilterData(
            "category",
            category,
            "Wiek uczniów",
            "Wybierz kategorię...",
            filterOptions.student_categories || [],
        ),
        createFilterData(
            "career",
            career,
            "Kierunki zawodowe",
            "Wybierz zawód...",
            filterOptions.vocational_training || [],
        ),
    ])

    return {
        filterData,
    }
}
