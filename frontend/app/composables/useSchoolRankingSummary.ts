import type { RankingScope } from "~/types/ranking"
import type { SzkolaPublicWithRelations } from "~/types/schools"

interface UseSchoolRankingSummaryOptions {
    school: () => SzkolaPublicWithRelations
}

const rankingDonutCategories = {
    better: {
        name: "Lepsza od",
        color: "var(--ui-success)",
    },
    rest: {
        name: "Pozostałe",
        color: "var(--ui-secondary)",
    },
}

export const useSchoolRankingSummary = (
    options: UseSchoolRankingSummaryOptions,
) => {
    const powiat = computed(() => options.school().miejscowosc.gmina.powiat)

    const { rankingGroups, hasRankingGroups } = useRankingGroups({
        rankingi: () => options.school().rankingi ?? [],
        countyName: () => powiat.value.nazwa,
        voivodeshipName: () => powiat.value.wojewodztwo.nazwa,
    })

    const getBetterThanPercent = (percentyl: number): number => {
        return Number(Math.max(0, 100 - percentyl).toFixed(1))
    }

    const getRankingDonutData = (percentyl: number): number[] => {
        const better = getBetterThanPercent(percentyl)
        const rest = Number((100 - better).toFixed(1))
        return [better, rest]
    }

    const getRankingScopeColor = (scope: RankingScope) => {
        if (scope === "KRAJ") return "primary"
        if (scope === "WOJEWODZTWO") return "info"
        return "neutral"
    }

    return {
        hasRankingGroups,
        rankingGroups,
        rankingDonutCategories,
        getBetterThanPercent,
        getRankingDonutData,
        getRankingScopeColor,
    }
}
