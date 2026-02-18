import type { PercentileColor, RankingScope } from "~/types/ranking"

export const getScopeLabel = (
    scope: RankingScope,
    countyName: string,
    voivodeshipName: string,
): string => {
    if (scope === "KRAJ") return "Cała Polska"
    if (scope === "WOJEWODZTWO")
        return `Województwo ${voivodeshipName.toLowerCase()}`
    return `Powiat ${countyName}`
}

export const getPercentileColor = (percentyl: number): PercentileColor => {
    if (percentyl <= 3) {
        return {
            textClass: "text-amber-700 dark:text-amber-300",
            barClass: "bg-amber-500 dark:bg-amber-400",
        }
    }

    if (percentyl <= 10) {
        return {
            textClass: "text-emerald-700 dark:text-emerald-300",
            barClass: "bg-emerald-600 dark:bg-emerald-400",
        }
    }

    if (percentyl <= 25) {
        return {
            textClass: "text-sky-700 dark:text-sky-300",
            barClass: "bg-sky-600 dark:bg-sky-400",
        }
    }

    return {
        textClass: "text-indigo-700 dark:text-indigo-300",
        barClass: "bg-indigo-500 dark:bg-indigo-400",
    }
}

export const formatPercentyl = (percentyl: number): string =>
    `${Number(percentyl.toFixed(1))}`
