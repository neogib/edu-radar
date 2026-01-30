import type { ActiveSelections, FilterConfig } from "~/types/filters"
import type { FiltersOptions, FiltersResponse } from "~/types/schools"
import { mainSchoolTypes } from "~/constants/schoolTypes"

export const useFilterData = async () => {
    const { $api } = useNuxtApp()
    const { type, status, category, career } = useSchoolFilters()

    // Use $api instead of useApi to ensure data is fetched and available directly
    // This avoids potential issues with useFetch/useApi reactivity when used inside an async composable
    const filterOptions = await $api<FiltersResponse>("/filters/")

    // Reorder school_types to place priority types first
    const reorderedSchoolTypes = [
        ...filterOptions.school_types.filter((st) =>
            mainSchoolTypes.includes(st.nazwa),
        ),
        ...filterOptions.school_types.filter(
            (st) => !mainSchoolTypes.includes(st.nazwa),
        ),
    ]
    console.log("Reordered School Types:", reorderedSchoolTypes)

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
            reorderedSchoolTypes,
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
