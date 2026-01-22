import type { ActiveSelections, FilterConfig } from "~/types/filters"
import type { FiltersOptions, FiltersResponse } from "~/types/schools"

export const useFilterData = () => {
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
            addingsState: false,
        }
    }

    const { type, status, category, vocational_training } = useSchoolFilters()
    const { data: filterOptions } = useApi<FiltersResponse>("/filters/")

    const filterData: FilterConfig[] = [
        createFilterData(
            "type",
            type,
            "Rodzaj szkoły",
            "Wybierz typ szkoły...",
            filterOptions.value?.school_types || [],
        ),
        createFilterData(
            "status",
            status,
            "Publiczna / niepubliczna",
            "Wybierz status...",
            filterOptions.value?.public_statuses || [],
        ),
        createFilterData(
            "category",
            category,
            "Wiek uczniów",
            "Wybierz kategorię...",
            filterOptions.value?.student_categories || [],
        ),
        createFilterData(
            "vocational_training",
            vocational_training,
            "Kierunki zawodowe",
            "Wybierz zawód...",
            filterOptions.value?.vocational_training || [],
        ),
    ]

    return {
        filterData,
    }
}
