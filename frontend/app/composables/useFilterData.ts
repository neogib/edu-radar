import type { ActiveSelections, MultiFilterRef } from "~/types/filters"
import type { FiltersOptions, SchoolFiltersResponse } from "~/types/schools"
import { mainSchoolTypes } from "~/constants/schoolTypes"

export const useFilterData = async () => {
    const { $api } = useNuxtApp()
    const { type, status, category, career } = useSchoolFilters()

    // Use $api instead of useApi to ensure data is fetched and available directly
    // This avoids potential issues with useFetch/useApi reactivity when used inside an async composable
    const filterOptions = await $api<SchoolFiltersResponse>("/filters/")

    // Reorder school_types to place priority types first
    const reorderedSchoolTypes = [
        ...filterOptions.schoolTypes.filter((st) =>
            mainSchoolTypes.includes(st.nazwa),
        ),
        ...filterOptions.schoolTypes.filter(
            (st) => !mainSchoolTypes.includes(st.nazwa),
        ),
    ]

    const createMultiSelectFilters = (
        key: keyof ActiveSelections,
        selected: Ref<number[] | undefined>,
        label: string,
        placeholder: string,
        options: FiltersOptions,
    ): MultiFilterRef => {
        return {
            key,
            selected,
            label,
            placeholder,
            options,
            addingState: false,
        }
    }

    const multiSelectFilters = reactive<MultiFilterRef[]>([
        createMultiSelectFilters(
            "type",
            type,
            "Rodzaj szkoły",
            "Wybierz typ szkoły...",
            reorderedSchoolTypes,
        ),
        createMultiSelectFilters(
            "status",
            status,
            "Publiczna / niepubliczna",
            "Wybierz status...",
            filterOptions.publicStatuses || [],
        ),
        createMultiSelectFilters(
            "category",
            category,
            "Wiek uczniów",
            "Wybierz kategorię...",
            filterOptions.studentCategories || [],
        ),
        createMultiSelectFilters(
            "career",
            career,
            "Kierunki zawodowe",
            "Wybierz zawód...",
            filterOptions.vocationalTraining || [],
        ),
    ])

    return {
        multiSelectFilters,
    }
}
