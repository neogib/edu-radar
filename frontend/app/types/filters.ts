import type { FiltersOptions, SchoolFilterParams } from "./schools"

export type FiltersParamsWihtoutBbox = Omit<
    NonNullable<SchoolFilterParams>,
    "min_lng" | "min_lat" | "max_lng" | "max_lat" | "limit"
>
/**
 * Filter configuration for a single filter group
 * Used to make the filter system scalable
 */
export interface FilterConfig {
    key: keyof ActiveSelections
    queryParam: Ref<number[] | undefined>
    label: string
    placeholder: string
    options: FiltersOptions
    addingState: boolean
}

/**
 * track active selections for each filter group
 * derived from SchoolFilterParams to ensure synchronization with backend
 */
export type ActiveSelections = {
    [K in keyof NonNullable<SchoolFilterParams> as NonNullable<SchoolFilterParams>[K] extends
        | number[]
        | null
        | undefined
        ? K
        : never]: number[]
}

export const SELECTION_KEYS: (keyof ActiveSelections)[] = [
    "type",
    "status",
    "category",
    "career",
]
