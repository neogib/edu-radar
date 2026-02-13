import type { components } from "~/types/api"

export type RankingPublic = components["schemas"]["RankingPublic"]
export type RodzajRankingu = components["schemas"]["RodzajRankingu"]

export type RankingScope = "kraj" | "wojewodztwo" | "powiat"

export type MedalIcon =
    | "noto:1st-place-medal"
    | "noto:2nd-place-medal"
    | "noto:3rd-place-medal"
    | null

export interface PercentileColor {
    textClass: string
    barClass: string
}

export interface RankingRow {
    scope: RankingScope
    percentyl: number
    miejsce: number
    liczbaSzkol: number
    scopeLabel: string
    scopeBadgeClass: string
    medalIcon: MedalIcon
    textClass: string
    barClass: string
}

export interface RankingGroup {
    examType: RodzajRankingu
    label: string
    year: number
    rows: RankingRow[]
}
