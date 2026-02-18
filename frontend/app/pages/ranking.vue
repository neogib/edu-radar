<script setup lang="ts">
import { UBadge, UTooltip } from "#components"
import type { TableColumn, TableRow } from "@nuxt/ui"
import type {
    RankingWithSchool,
    RankingScope,
    RankingTableRow,
    RankingsFiltersResponse,
    RodzajRankingu,
    RankingDirection,
} from "~/types/ranking"

useSeoMeta({
    title: "Ranking szkół w Polsce - EduRadar",
    description:
        "Analizuj pozycję szkół w rankingach – porównuj miejsca w kraju, województwie lub powiecie.",
    ogTitle: "Ranking szkół w Polsce – EduRadar",
    ogDescription:
        "Analizuj pozycję szkół w rankingach – porównuj miejsca w kraju, województwie lub powiecie.",
    ogImage: "/og-image.png",
    twitterImage: "/og-image.png",
    twitterCard: "summary_large_image",
})

const { data: filtersData, error: filtersError } =
    await useApi<RankingsFiltersResponse>("/rankings/filters")

const {
    yearOptions,
    typeOptions,
    scopeOptions,
    directionOptions,
    voivodeshipOptions,
    countyOptions,
} = useRankingsOptions(filtersData)

const {
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
} = useRankingsData(filtersData.value?.years[0] ?? new Date().getFullYear() - 1)

const formatNumber = (value: number) =>
    new Intl.NumberFormat("pl-PL", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
    }).format(value)

const getPlaceByScope = (
    ranking: RankingWithSchool,
    scope: RankingScope,
): number => {
    if (scope === "WOJEWODZTWO") return ranking.miejsce_wojewodztwo
    if (scope === "POWIAT") return ranking.miejsce_powiat
    return ranking.miejsce_kraj
}

const tableRows = computed<RankingTableRow[]>(() => {
    const rankings = rankingsData.value?.rankings ?? []
    const scope = selectedScope.value
    if (!scope) return []

    return rankings.map((ranking) => ({
        id: ranking.id,
        place: getPlaceByScope(ranking, scope),
        schoolName: ranking.szkola.nazwa,
        city: ranking.szkola.miejscowosc.nazwa,
        status: ranking.szkola.status_publicznoprawny.nazwa,
        score: formatNumber(ranking.wynik),
    }))
})

const hoveredSchoolId = ref<number | null>(null)

const isTooltipOpenForRow = (schoolId: number): boolean =>
    hoveredSchoolId.value === schoolId

const columns: TableColumn<RankingTableRow>[] = [
    {
        accessorKey: "place",
        header: "Miejsce",
        cell: ({ row }) =>
            h(
                UBadge,
                {
                    variant: "soft",
                    color: getPlaceBadgeColor(row.original.place),
                },
                () => String(row.original.place),
            ),
    },
    {
        accessorKey: "schoolName",
        header: "Szkoła",
        meta: {
            class: {
                th: "w-[220px] sm:w-[320px]",
                td: "w-[220px] sm:w-[320px]",
            },
        },
        cell: ({ row }) =>
            h(
                UTooltip,
                {
                    open: isTooltipOpenForRow(row.original.id),
                    content: { side: "top", sideOffset: 6 },
                    delayDuration: 0,
                    ui: {
                        content:
                            "h-auto max-w-[300px] items-start py-2 whitespace-normal",
                    },
                },
                {
                    default: () =>
                        h(
                            "span",
                            {
                                class: "block max-w-[220px] truncate text-left sm:max-w-[320px]",
                            },
                            row.original.schoolName,
                        ),
                    content: () =>
                        h(
                            "p",
                            {
                                class: "w-full whitespace-normal break-words text-sm leading-tight",
                            },
                            row.original.schoolName,
                        ),
                },
            ),
    },
    { accessorKey: "city", header: "Miejscowość" },
    { accessorKey: "status", header: "Status" },
    {
        accessorKey: "score",
        header: "Wynik",
        cell: ({ row }) =>
            h(
                "span",
                { class: "font-medium text-primary" },
                row.original.score,
            ),
    },
]

const getPlaceBadgeColor = (place: number) => {
    if (place <= 3) return "success"
    if (place <= 10) return "info"
    if (place <= 50) return "warning"
    return "neutral"
}

const handleRowHover = (
    _event: Event,
    row: TableRow<RankingTableRow> | null,
) => {
    hoveredSchoolId.value = row?.original.id ?? null
}

const tableMeta = computed(() => ({
    class: {
        tr: (row: TableRow<RankingTableRow>) =>
            isTooltipOpenForRow(row.original.id) ? "bg-primary/5" : "",
    },
}))

const totalItems = computed(() => rankingsData.value?.total ?? 0)
const pageSize = computed(() => rankingsData.value?.pageSize ?? 50)

const handleScopeChange = (scope: RankingScope) => {
    selectedScope.value = scope

    if (scope === "KRAJ") {
        selectedVoivodeshipId.value = undefined
        selectedCountyId.value = undefined
    } else if (scope === "WOJEWODZTWO") {
        selectedCountyId.value = undefined
        selectedVoivodeshipId.value = voivodeshipOptions.value[0]?.value
    } else if (scope === "POWIAT") {
        selectedVoivodeshipId.value = undefined
        selectedCountyId.value = countyOptions.value[0]?.value
    }

    selectedPage.value = 1
}

const hasError = computed(
    () => Boolean(filtersError.value) || Boolean(rankingsError.value),
)

const sortTrailingIcon = computed(() =>
    selectedDirection.value === "WORST"
        ? "i-lucide-arrow-down"
        : "i-lucide-arrow-up",
)
</script>

<template>
    <div class="max-w-7xl mx-auto px-2 sm:px-5 lg:px-8 space-y-4">
        <UPageHeader
            title="Ranking szkół"
            description="Analizuj pozycję szkół w rankingach – porównuj miejsca w kraju, województwie lub powiecie."
            :ui="{
                root: 'mb-1 py-4',
                container: 'py-1 sm:py-2',
            }" />

        <div class="flex flex-wrap items-start gap-3">
            <div class="flex flex-col gap-1">
                <p class="text-xs font-medium text-muted">Rok</p>
                <USelectMenu
                    :ui="{
                        content: 'min-w-[8rem]',
                    }"
                    :model-value="selectedYear"
                    :items="yearOptions"
                    value-key="value"
                    :search-input="{ placeholder: 'Wybierz rok' }"
                    color="primary"
                    @update:model-value="
                        (value: number) => {
                            selectedYear = value
                            selectedPage = 1
                        }
                    " />
            </div>

            <div class="flex flex-col gap-1">
                <p class="text-xs font-medium text-muted">Rodzaj rankingu</p>
                <USelectMenu
                    :ui="{
                        content: 'min-w-[14rem]',
                    }"
                    :model-value="selectedType"
                    :items="typeOptions"
                    value-key="value"
                    :search-input="{ placeholder: 'Wybierz rodzaj rankingu' }"
                    color="info"
                    @update:model-value="
                        (value: RodzajRankingu) => {
                            selectedType = value
                            selectedPage = 1
                        }
                    " />
            </div>

            <div class="flex flex-col gap-1">
                <p class="text-xs font-medium text-muted">Sortowanie</p>
                <USelect
                    :ui="{
                        content: 'min-w-[10rem]',
                    }"
                    :model-value="selectedDirection"
                    :items="directionOptions"
                    value-key="value"
                    :trailing-icon="sortTrailingIcon"
                    @update:model-value="
                        (value: RankingDirection) => {
                            selectedDirection = value
                            selectedPage = 1
                        }
                    " />
            </div>

            <div class="flex flex-col gap-1">
                <p class="text-xs font-medium text-muted">Zakres</p>
                <USelectMenu
                    :ui="{
                        content: 'min-w-[10rem]',
                    }"
                    :model-value="selectedScope"
                    :items="scopeOptions"
                    value-key="value"
                    :search-input="{ placeholder: 'Wybierz zakres' }"
                    color="warning"
                    @update:model-value="
                        (value: RankingScope) => handleScopeChange(value)
                    " />
            </div>

            <div
                v-if="selectedScope === 'WOJEWODZTWO'"
                class="flex flex-col gap-1">
                <p class="text-xs font-medium text-muted">Województwo</p>
                <USelectMenu
                    :ui="{
                        content: 'min-w-[14rem]',
                    }"
                    :model-value="selectedVoivodeshipId"
                    :items="voivodeshipOptions"
                    value-key="value"
                    :search-input="{ placeholder: 'Wybierz Województwo' }"
                    color="primary"
                    @update:model-value="
                        (value: number) => {
                            selectedVoivodeshipId = value
                            selectedPage = 1
                        }
                    " />
            </div>

            <div v-if="selectedScope === 'POWIAT'" class="flex flex-col gap-1">
                <p class="text-xs font-medium text-muted">Powiat</p>
                <USelectMenu
                    :ui="{
                        content: 'min-w-[18rem]',
                    }"
                    :model-value="selectedCountyId"
                    :items="countyOptions"
                    virtualize
                    value-key="value"
                    :search-input="{ placeholder: 'Wybierz powiat' }"
                    color="primary"
                    @update:model-value="
                        (value: number) => {
                            selectedCountyId = value
                            selectedPage = 1
                        }
                    " />
            </div>
        </div>

        <div
            v-if="rankingsStatus === 'pending'"
            class="flex items-center gap-2 text-sm text-primary animate-pulse">
            <UIcon name="i-lucide-loader-circle" class="size-4 animate-spin" />
            <span>Ładowanie danych rankingu...</span>
        </div>

        <UAlert
            v-if="hasError"
            color="error"
            variant="soft"
            title="Nie udało się pobrać rankingów." />

        <UTable
            sticky
            :data="tableRows"
            :columns="columns"
            :meta="tableMeta"
            :on-hover="handleRowHover"
            :loading="rankingsStatus === 'pending'"
            loading-animation="carousel"
            loading-color="primary"
            empty="Brak wyników dla wybranych filtrów."
            class="rounded-lg border border-primary/20 bg-default/70">
        </UTable>

        <div class="flex justify-center">
            <UPagination
                v-model:page="selectedPage"
                :total="totalItems"
                :items-per-page="pageSize"
                :sibling-count="0"
                show-edges
                color="primary"
                active-color="info" />
        </div>
    </div>
</template>
