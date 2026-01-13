import type { SchoolFilterParams } from "./schools"

/**
 * Filter configuration for a single filter group
 * Used to make the filter system scalable
 */
export interface FilterConfig {
    key: keyof SchoolFilterParams
    queryParam: string
    label: string
    placeholder: string
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
