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
    const selectedYear = usePushRouteQuery<number>("year", defaultYear, {
        transform: Number,
    })
    const selectedType = usePushRouteQuery<RodzajRankingu>("type", "E8")
    const selectedScope = usePushRouteQuery<RankingScope>("scope", "KRAJ")
    const selectedDirection = usePushRouteQuery<RankingDirection>(
        "direction",
        "BEST",
    )
    const selectedVoivodeshipId = usePushRouteQuery<number | undefined>(
        "voivodeshipId",
        undefined,
        {
            transform: (v) => (v !== undefined ? Number(v) : undefined),
        },
    )
    const selectedCountyId = usePushRouteQuery<number | undefined>(
        "countyId",
        undefined,
        {
            transform: (v) => (v !== undefined ? Number(v) : undefined),
        },
    )

    const canFetchRankings = computed(() => {
        if (selectedScope.value === "WOJEWODZTWO") {
            return selectedVoivodeshipId.value !== undefined
        }
        if (selectedScope.value === "POWIAT") {
            return selectedCountyId.value !== undefined
        }
        return true
    })

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
        refresh: fetchRankings,
    } = useApi<RankingsResponse>("/rankings/", {
        lazy: true,
        watch: false,
        query: rankingFilters,
    })

    watch([rankingFilters, canFetchRankings], ([_, canFetch]) => {
        if (!canFetch) return
        void fetchRankings()
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
