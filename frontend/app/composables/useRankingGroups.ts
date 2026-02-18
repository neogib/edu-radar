import {
    EXAM_TYPE_LABELS,
    EXAM_TYPE_ORDER,
    MEDAL_ICON_BY_PLACE,
    SCOPE_BADGE_CLASSES,
    SCOPE_PRIORITY,
} from "~/constants/ranking"
import type {
    RankingGroup,
    RankingPublic,
    RankingRow,
    RodzajRankingu,
} from "~/types/ranking"

interface UseRankingGroupsOptions {
    rankingi: MaybeRefOrGetter<RankingPublic[]>
    countyName: MaybeRefOrGetter<string>
    voivodeshipName: MaybeRefOrGetter<string>
}

export const useRankingGroups = (options: UseRankingGroupsOptions) => {
    const rankingGroups = computed<RankingGroup[]>(() => {
        const rankingi = toValue(options.rankingi)
        if (!rankingi.length) return []

        const countyName = toValue(options.countyName)
        const voivodeshipName = toValue(options.voivodeshipName)

        const latestYear = Math.max(...rankingi.map((ranking) => ranking.rok))
        const newestYearRankings = rankingi.filter(
            (ranking) => ranking.rok === latestYear,
        )

        const rankingByType = new Map<RodzajRankingu, RankingPublic>()
        for (const ranking of newestYearRankings) {
            rankingByType.set(ranking.rodzaj_rankingu, ranking)
        }

        return EXAM_TYPE_ORDER.map((examType): RankingGroup | null => {
            const ranking = rankingByType.get(examType)
            if (!ranking) return null

            const allRows = [
                {
                    scope: "KRAJ" as const,
                    percentyl: ranking.percentyl_kraj,
                    miejsce: ranking.miejsce_kraj,
                    liczbaSzkol: ranking.liczba_szkol_kraj,
                },
                {
                    scope: "WOJEWODZTWO" as const,
                    percentyl: ranking.percentyl_wojewodztwo,
                    miejsce: ranking.miejsce_wojewodztwo,
                    liczbaSzkol: ranking.liczba_szkol_wojewodztwo,
                },
                {
                    scope: "POWIAT" as const,
                    percentyl: ranking.percentyl_powiat,
                    miejsce: ranking.miejsce_powiat,
                    liczbaSzkol: ranking.liczba_szkol_powiat,
                },
            ]

            const rows = allRows
                .filter((row) => row.percentyl <= 50)
                .sort(
                    (a, b) => SCOPE_PRIORITY[a.scope] - SCOPE_PRIORITY[b.scope],
                )
                .map((row): RankingRow => {
                    const colors = getPercentileColor(row.percentyl)

                    return {
                        ...row,
                        scopeLabel: getScopeLabel(
                            row.scope,
                            countyName,
                            voivodeshipName,
                        ),
                        scopeBadgeClass: SCOPE_BADGE_CLASSES[row.scope],
                        medalIcon: MEDAL_ICON_BY_PLACE[row.miejsce] ?? null,
                        textClass: colors.textClass,
                        barClass: colors.barClass,
                    }
                })

            if (!rows.length) return null

            return {
                examType,
                label: EXAM_TYPE_LABELS[examType],
                year: ranking.rok,
                rows,
            }
        }).filter((group): group is RankingGroup => group !== null)
    })

    const hasRankingGroups = computed(() => rankingGroups.value.length > 0)

    return {
        rankingGroups,
        hasRankingGroups,
    }
}
