import type { MedalIcon, RankingScope, RodzajRankingu } from "~/types/ranking"

export const EXAM_TYPE_ORDER: RodzajRankingu[] = ["E8", "EM_LO", "EM_TECH"]

export const EXAM_TYPE_LABELS: Record<RodzajRankingu, string> = {
    E8: "Egzamin ósmoklasisty",
    EM_LO: "Matura – LO",
    EM_TECH: "Matura – Technikum",
}

export const SCOPE_PRIORITY: Record<RankingScope, number> = {
    KRAJ: 0,
    WOJEWODZTWO: 1,
    POWIAT: 2,
}

export const SCOPE_BADGE_CLASSES: Record<RankingScope, string> = {
    KRAJ: "bg-blue-100 text-blue-800 ring-blue-200 dark:bg-blue-500/20 dark:text-blue-200 dark:ring-blue-400/40",
    WOJEWODZTWO:
        "bg-cyan-100 text-cyan-800 ring-cyan-200 dark:bg-cyan-500/20 dark:text-cyan-200 dark:ring-cyan-400/40",
    POWIAT: "bg-orange-100 text-orange-800 ring-orange-200 dark:bg-orange-500/20 dark:text-orange-200 dark:ring-orange-400/40",
}

export const MEDAL_ICON_BY_PLACE: Partial<
    Record<number, Exclude<MedalIcon, null>>
> = {
    1: "noto:1st-place-medal",
    2: "noto:2nd-place-medal",
    3: "noto:3rd-place-medal",
}
