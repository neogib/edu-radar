<script setup lang="ts">
import { UBadge, UTooltip } from "#components"
import type { TableColumn, TableRow } from "@nuxt/ui"
import type { Table as TanstackTable } from "@tanstack/table-core"
import { watchDebounced } from "@vueuse/core"
import { upperFirst } from "scule"
import type {
    RankingWithSchool,
    RankingScope,
    RankingTableRow,
    RankingsFiltersResponse,
    RodzajRankingu,
    RankingDirection,
} from "~/types/ranking"

useSeoMeta({
    title: "Ranking szkół w Polsce",
    description:
        "Analizuj pozycję szkół w rankingach – porównuj miejsca w kraju, województwie lub powiecie.",
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
    statusOptions,
} = useRankingsOptions(filtersData)

const search = ref("")
const debouncedSearch = ref("")

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
    selectedStatusId,
} = useRankingsData(
    filtersData.value?.years[0] ?? new Date().getFullYear() - 1,
    debouncedSearch,
)

const rankingStatusOptions = computed(() => [
    { label: "Wszystkie", value: null },
    ...statusOptions.value,
])

const selectedStatusForUi = computed<number | null>({
    get: () => selectedStatusId.value ?? null,
    set: (value) => {
        selectedStatusId.value = value ?? undefined
        selectedPage.value = 1
    },
})

watchDebounced(
    search,
    (value) => {
        debouncedSearch.value = value.trim()
        selectedPage.value = 1
    },
    { debounce: 300, maxWait: 800 },
)

const formatNumber = (value: number) =>
    new Intl.NumberFormat("pl-PL", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
    }).format(value)

const getPlaceByScope = (
    ranking: RankingWithSchool,
    scope: RankingScope,
): number => {
    if (scope === "WOJEWODZTWO") return ranking.miejsceWojewodztwo
    if (scope === "POWIAT") return ranking.miejscePowiat
    return ranking.miejsceKraj
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
        status: ranking.szkola.statusPublicznoprawny.nazwa,
        score: formatNumber(ranking.wynik),
    }))
})

const hoveredSchoolId = ref<number | null>(null)
const table = useTemplateRef<{ tableApi: TanstackTable<RankingTableRow> }>(
    "table",
)
const columnVisibility = ref<Record<string, boolean>>({})

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

const columnLabels: Record<string, string> = {
    place: "Miejsce",
    schoolName: "Szkoła",
    city: "Miejscowość",
    status: "Status",
    score: "Wynik",
}

const columnVisibilityItems = computed(
    () =>
        (table.value?.tableApi
            .getAllColumns()
            .filter((column) => column.getCanHide())
            .map((column) => ({
                label: columnLabels[column.id] ?? upperFirst(column.id),
                type: "checkbox" as const,
                checked: column.getIsVisible(),
                onUpdateChecked: (checked: boolean) => {
                    table.value?.tableApi
                        .getColumn(column.id)
                        ?.toggleVisibility(checked)
                },
                onSelect: (event: Event) => {
                    event.preventDefault()
                },
            })) ?? []) satisfies Array<{
            label: string
            type: "checkbox"
            checked: boolean
            onUpdateChecked: (checked: boolean) => void
            onSelect: (event: Event) => void
        }>,
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
                <USelect
                    :ui="{
                        content: 'min-w-[8rem]',
                    }"
                    :model-value="selectedYear"
                    :items="yearOptions"
                    value-key="value"
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
                <USelect
                    :ui="{
                        content: 'min-w-[14rem]',
                    }"
                    :model-value="selectedType"
                    :items="typeOptions"
                    value-key="value"
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
                <p class="text-xs font-medium text-muted">Status</p>
                <USelect
                    v-model="selectedStatusForUi"
                    :ui="{
                        content: 'min-w-[14rem]',
                    }"
                    :items="rankingStatusOptions"
                    value-key="value" />
            </div>

            <div class="flex flex-col gap-1">
                <p class="text-xs font-medium text-muted">Zakres</p>
                <USelect
                    :ui="{
                        content: 'min-w-[10rem]',
                    }"
                    :model-value="selectedScope"
                    :items="scopeOptions"
                    value-key="value"
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

        <UAlert
            v-if="hasError"
            color="error"
            variant="soft"
            title="Nie udało się pobrać rankingów." />

        <div
            class="overflow-hidden rounded-lg border border-primary/20 bg-default/70">
            <div
                class="flex flex-col gap-2 border-b border-primary/20 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
                <UInput
                    v-model="search"
                    icon="i-lucide-search"
                    placeholder="Szukaj szkoły..."
                    class="w-full sm:max-w-sm" />

                <UDropdownMenu
                    :items="columnVisibilityItems"
                    :content="{ align: 'end' }">
                    <UButton
                        label="Kolumny"
                        color="neutral"
                        variant="outline"
                        trailing-icon="i-lucide-chevron-down" />
                </UDropdownMenu>
            </div>

            <UTable
                ref="table"
                v-model:column-visibility="columnVisibility"
                sticky
                :data="tableRows"
                :columns="columns"
                :meta="tableMeta"
                :on-hover="handleRowHover"
                :loading="rankingsStatus === 'pending'"
                loading-animation="carousel"
                loading-color="primary"
                empty="Brak wyników dla wybranych filtrów."
                class="bg-transparent" />
        </div>

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
