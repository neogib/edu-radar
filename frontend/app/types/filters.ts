import type { FiltersOptions, SchoolFilterParams } from "./schools"

export type FiltersParamsWihtoutBbox = Omit<
    NonNullable<SchoolFilterParams>,
    "min_lng" | "min_lat" | "max_lng" | "max_lat" | "limit"
>
/**
 * Base filter configuration
 */
interface MultiFilterBase {
    key: keyof ActiveSelections
    label: string
    placeholder: string
    options: FiltersOptions
    addingState: boolean
}

/**
 * Filter configuration with Ref for composables (two-way binding)
 */
export interface MultiFilterRef extends MultiFilterBase {
    queryParam: Ref<number[] | undefined>
}

/**
 * Filter configuration with plain values for components
 */
export interface MultiFilter extends MultiFilterBase {
    queryParam: number[] | undefined
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
