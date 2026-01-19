import type { FilterConfig } from "~/types/filters"
import type { FiltersResponse } from "~/types/schools"

// Filter configuration - now includes the API response key
export const filterConfigs: (FilterConfig & {
    optionsKey: keyof FiltersResponse
})[] = [
    {
        key: "type",
        queryParam: "type",
        label: "Rodzaj szkoły",
        placeholder: "Wybierz typ szkoły...",
        optionsKey: "school_types",
    },
    {
        key: "status",
        queryParam: "status",
        label: "Publiczna / niepubliczna",
        placeholder: "Wybierz status...",
        optionsKey: "public_statuses",
    },
    {
        key: "category",
        queryParam: "category",
        label: "Wiek uczniów",
        placeholder: "Wybierz kategorię...",
        optionsKey: "student_categories",
    },
    {
        key: "vocational_training",
        queryParam: "vocational_training",
        label: "Kierunki zawodowe",
        placeholder: "Wybierz zawód...",
        optionsKey: "vocational_training",
    },
]
