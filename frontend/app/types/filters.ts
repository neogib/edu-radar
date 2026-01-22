import type { FiltersOptions, SchoolFilterParams } from "./schools"

export type FiltersParamsWihtoutBbox = Omit<
    NonNullable<SchoolFilterParams>,
    "bbox"
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
    addingsState: boolean
}

/**
 * track active selections for each filter group
 */
export interface ActiveSelections {
    type: number[]
    status: number[]
    category: number[]
    vocational_training: number[]
}

export const SELECTION_KEYS: (keyof ActiveSelections)[] = [
    "type",
    "status",
    "category",
    "vocational_training",
]
