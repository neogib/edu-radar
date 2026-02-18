import type {
    RankingDirection,
    RankingScope,
    RankingsParams,
    RankingsResponse,
    RodzajRankingu,
} from "~/types/ranking"

export const useRankingsData = (defaultYear: number) => {
    const selectedPage = usePushRouteQuery<number>("page", 1, {
        transform: Number,
    })
    const selectedYear = usePushRouteQuery<number>("rok", defaultYear, {
        transform: Number,
    })
    const selectedType = usePushRouteQuery<RodzajRankingu>("type", "E8")
    const selectedScope = usePushRouteQuery<RankingScope>("scope", "KRAJ")
    const selectedDirection = usePushRouteQuery<RankingDirection>(
        "direction",
        "BEST",
    )
    const selectedVoivodeshipId = usePushRouteQuery<number | undefined>(
        "voivodeship_id",
        undefined,
        {
            transform: (v) => (v !== undefined ? Number(v) : undefined),
        },
    )
    const selectedCountyId = usePushRouteQuery<number | undefined>(
        "county_id",
        undefined,
        {
            transform: (v) => (v !== undefined ? Number(v) : undefined),
        },
    )

    const rankingFilters = computed<RankingsParams>(() => ({
        page: selectedPage.value,
        year: selectedYear.value,
        type: selectedType.value,
        scope: selectedScope.value,
        direction: selectedDirection.value,
        voivodeshipId: selectedVoivodeshipId.value,
        countyId: selectedCountyId.value,
    }))

    const {
        data: rankingsData,
        status: rankingsStatus,
        error: rankingsError,
    } = useApi<RankingsResponse>("/rankings/", {
        lazy: true,
        query: rankingFilters,
    })

    return {
        rankingsData,
        rankingsStatus,
        rankingsError,
        selectedPage,
        selectedYear,
        selectedType,
        selectedScope,
        selectedDirection,
        selectedVoivodeshipId,
        selectedCountyId,
    }
}
