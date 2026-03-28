<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui"
import { useExamSections } from "~/composables/useExamSections"
import { useRankingGroups } from "~/composables/useRankingGroups"
import {
    EXAM_TREND_CHART_CATEGORIES,
    EXAM_TREND_MARKER_CONFIG,
} from "~/constants/examSections"
import type {
    DetailedResultsTableRow,
    TopSubjectChartPoint,
    YearRow,
} from "~/types/schoolDetails"
import type { SzkolaPublicWithRelations } from "~/types/schools"
import type { ExamSectionKey } from "~/types/subjects"
import {
    compactSubjectLabel,
    formatNumber,
    formatPercent,
} from "~/utils/schoolDetailsFormat"

const DEFAULT_VISIBLE_ROWS = 14

const route = useRoute()
const schoolId = Number.parseInt(String(route.params.id), 10)

if (!Number.isInteger(schoolId) || schoolId <= 0) {
    throw createError({
        statusCode: 404,
        statusMessage: "Nieprawidłowy identyfikator szkoły",
    })
}

const {
    data: schoolData,
    status,
    error,
    refresh,
} = await useApi<SzkolaPublicWithRelations>(`/schools/${schoolId}`, {
    key: `school-details-${schoolId}`,
    lazy: true,
})

const school = computed(() => schoolData.value ?? null)

const isPending = computed(
    () => status.value === "pending" || status.value === "idle",
)
const hasError = computed(() => Boolean(error.value))

useSeoMeta({
    title: () =>
        school.value
            ? `${school.value.nazwa} | EduRadar`
            : `Szkoła #${schoolId} | EduRadar`,
    description: () =>
        school.value
            ? `Szczegółowe dane szkoły ${school.value.nazwa}: wyniki egzaminów, rankingi i metadane.`
            : `Szczegółowe dane szkoły o identyfikatorze ${schoolId}.`,
})

const emResults = computed(() => school.value?.wynikiEm ?? [])
const e8Results = computed(() => school.value?.wynikiE8 ?? [])

const { examSections, hasExamResults } = useExamSections({
    wynikiE8: e8Results,
    wynikiEm: emResults,
})

const examTypeOptions = computed<
    Array<{ label: string; value: ExamSectionKey }>
>(() => {
    const options: Array<{ label: string; value: ExamSectionKey }> = []

    if (e8Results.value.length) {
        options.push({
            label: "Egzamin ósmoklasisty",
            value: "e8",
        })
    }

    if (emResults.value.length) {
        options.push({
            label: "Matura",
            value: "em",
        })
    }

    return options
})

const selectedExamKey = ref<ExamSectionKey>("e8")

watch(
    examTypeOptions,
    (options) => {
        const optionValues = options.map((option) => option.value)
        if (!optionValues.length) return

        if (!optionValues.includes(selectedExamKey.value) && optionValues[0]) {
            selectedExamKey.value = optionValues[0]
        }
    },
    { immediate: true },
)

const selectedExamSection = computed(() =>
    examSections.value.find((section) => section.key === selectedExamKey.value),
)

const yearOptions = computed<Array<{ label: string; value: number }>>(() => {
    const years = [...(selectedExamSection.value?.years ?? [])].sort(
        (a, b) => b - a,
    )

    return years.map((year) => ({
        label: String(year),
        value: year,
    }))
})

const selectedYear = ref(0)

watch(
    yearOptions,
    (options) => {
        const optionValues = options.map((option) => option.value)
        if (!optionValues.length) return

        if (!optionValues.includes(selectedYear.value) && optionValues[0]) {
            selectedYear.value = optionValues[0]
        }
    },
    { immediate: true },
)

const selectedYearRows = computed<YearRow[]>(() => {
    const section = selectedExamSection.value
    if (!section) return []

    const year = selectedYear.value

    return getOrderedExamSubjects(section)
        .map(([subject, subjectData]) => {
            const yearData = subjectData.years[year]
            if (!yearData) return null

            return {
                id: `${section.key}-${subject}-${year}`,
                subject,
                score: yearData.wynik,
                usesFallback: subjectData.usesFallback,
                participants: yearData.liczba_zdajacych,
                passRate: yearData.zdawalnosc ?? null,
                laureates: yearData.liczba_laureatow_finalistow ?? null,
            }
        })
        .filter((row): row is YearRow => row !== null)
})

const showAllRows = ref(false)
watch([selectedExamKey, selectedYear], () => {
    showAllRows.value = false
})

const hasCollapsedRows = computed(
    () => selectedYearRows.value.length > DEFAULT_VISIBLE_ROWS,
)

const visibleRows = computed(() =>
    showAllRows.value
        ? selectedYearRows.value
        : selectedYearRows.value.slice(0, DEFAULT_VISIBLE_ROWS),
)

const detailedResultsTableRows = computed<DetailedResultsTableRow[]>(() =>
    visibleRows.value.map((row) => ({
        id: row.id,
        subject: row.subject,
        usesFallback: row.usesFallback,
        score: formatNumber(row.score),
        participants: formatNumber(row.participants, 0),
        passRate: formatPercent(row.passRate),
        laureates: formatNumber(row.laureates, 0),
    })),
)

const detailedResultsColumns = computed<TableColumn<DetailedResultsTableRow>[]>(
    () => {
        const baseColumns: TableColumn<DetailedResultsTableRow>[] = [
            {
                accessorKey: "subject",
                header: "Przedmiot",
            },
            {
                accessorKey: "score",
                header: "Mediana",
            },
            {
                accessorKey: "participants",
                header: "Liczba zdających",
            },
        ]

        if (selectedExamKey.value === "e8") {
            return baseColumns
        }

        baseColumns.push(
            {
                accessorKey: "passRate",
                header: "Zdawalność",
            },
            {
                accessorKey: "laureates",
                header: "Laureaci/Finaliści",
            },
        )
        return baseColumns
    },
)

const topSubjectChartData = computed<TopSubjectChartPoint[]>(() =>
    [...selectedYearRows.value]
        .filter((row): row is YearRow & { score: number } => row.score !== null)
        .sort((a, b) => b.score - a.score)
        .slice(0, 10)
        .map((row) => ({
            subject: compactSubjectLabel(row.subject),
            score: Number(row.score.toFixed(2)),
        })),
)

const topSubjectCategories = {
    score: {
        name: "Wynik",
        color: "var(--ui-info)",
    },
}

const trendXFormatter = (tick: number): string =>
    `${selectedExamSection.value?.weightedData[tick]?.year ?? ""}`

const topSubjectXFormatter = (tick: number): string =>
    topSubjectChartData.value[tick]?.subject ?? ""

const powiat = computed(() => school.value?.miejscowosc.gmina.powiat ?? null)

const { rankingGroups, hasRankingGroups } = useRankingGroups({
    rankingi: () => school.value?.rankingi ?? [],
    countyName: () => powiat.value?.nazwa ?? "",
    voivodeshipName: () => powiat.value?.wojewodztwo.nazwa ?? "",
})
const hasLeftColumnContent = computed(() => hasExamResults.value)

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

const getBetterThanPercent = (percentyl: number): number => {
    return Number(Math.max(0, 100 - percentyl).toFixed(1))
}

const getRankingDonutData = (percentyl: number): number[] => {
    const better = getBetterThanPercent(percentyl)
    const rest = Number((100 - better).toFixed(1))
    return [better, rest]
}

const getRankingScopeColor = (scope: string) => {
    if (scope === "KRAJ") return "primary"
    if (scope === "WOJEWODZTWO") return "info"
    return "neutral"
}

const locationLabel = computed(() => {
    if (!school.value) return ""

    const location = school.value.miejscowosc
    const county = location.gmina.powiat.nazwa
    const voivodeship = location.gmina.powiat.wojewodztwo.nazwa

    return [location.nazwa, `powiat ${county}`, voivodeship]
        .filter(Boolean)
        .join(" • ")
})
</script>

<template>
    <UContainer class="max-w-7xl space-y-6 px-2 py-4 sm:px-5 lg:px-8">
        <div v-if="isPending && !school" class="space-y-6">
            <UCard>
                <template #header>
                    <div class="space-y-2">
                        <USkeleton class="h-10 w-full max-w-2xl" />
                        <USkeleton class="h-4 w-full max-w-xl" />
                    </div>
                </template>

                <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                    <USkeleton class="h-20" />
                    <USkeleton class="h-20" />
                    <USkeleton class="h-20" />
                </div>
            </UCard>

            <div
                class="grid grid-cols-1 gap-6"
                :class="hasLeftColumnContent ? 'lg:grid-cols-12' : ''">
                <div
                    v-if="hasLeftColumnContent"
                    class="min-w-0 space-y-6 lg:col-span-8">
                    <UCard>
                        <USkeleton class="h-56" />
                    </UCard>
                    <UCard>
                        <USkeleton class="h-64" />
                    </UCard>
                    <UCard>
                        <USkeleton class="h-72" />
                    </UCard>
                </div>
                <div
                    class="min-w-0 space-y-6"
                    :class="hasLeftColumnContent ? 'lg:col-span-4' : ''">
                    <UCard>
                        <USkeleton class="h-72" />
                    </UCard>
                    <UCard>
                        <USkeleton class="h-48" />
                    </UCard>
                </div>
            </div>
        </div>

        <div v-else-if="hasError" class="space-y-3">
            <UAlert
                color="error"
                variant="soft"
                title="Nie udało się pobrać danych szkoły"
                description="Spróbuj odświeżyć dane. Jeśli problem się powtarza, sprawdź połączenie z API." />
            <UButton
                color="error"
                variant="soft"
                icon="i-lucide-refresh-cw"
                @click="refresh()">
                Odśwież dane
            </UButton>
        </div>

        <UAlert
            v-else-if="!school"
            color="neutral"
            variant="soft"
            title="Brak danych szkoły"
            description="Nie znaleziono szczegółów dla podanego identyfikatora." />

        <div v-else class="space-y-6">
            <UCard>
                <template #header>
                    <div
                        class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                        <div class="space-y-2">
                            <h1
                                class="text-2xl font-semibold text-highlighted sm:text-3xl">
                                {{ school.nazwa }}
                            </h1>
                            <p class="text-sm text-toned">
                                {{ locationLabel }}
                            </p>
                        </div>

                        <div class="flex flex-wrap gap-2">
                            <UBadge color="primary" variant="soft">
                                {{ school.typ.nazwa }}
                            </UBadge>
                            <UBadge color="info" variant="soft">
                                {{ school.statusPublicznoprawny.nazwa }}
                            </UBadge>
                            <UBadge color="neutral" variant="soft">
                                {{ school.kategoriaUczniow.nazwa }}
                            </UBadge>
                            <UBadge
                                :color="
                                    school.zlikwidowana ? 'error' : 'success'
                                "
                                variant="soft">
                                {{
                                    school.zlikwidowana
                                        ? "Zlikwidowana"
                                        : "Aktywna"
                                }}
                            </UBadge>
                        </div>
                    </div>
                </template>

                <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                    <div
                        class="rounded-lg border border-default bg-default p-4">
                        <p class="text-xs text-muted">Wynik szkoły</p>
                        <p class="mt-1 text-2xl font-semibold text-primary">
                            {{ formatNumber(school.wynik) }}
                        </p>
                    </div>
                    <div
                        class="rounded-lg border border-default bg-default p-4">
                        <p class="text-xs text-muted">Liczba uczniów</p>
                        <p class="mt-1 text-2xl font-semibold text-highlighted">
                            {{ formatNumber(school.liczbaUczniow, 0) }}
                        </p>
                    </div>
                    <div
                        class="rounded-lg border border-default bg-default p-4">
                        <p class="text-xs text-muted">Numer RSPO</p>
                        <p class="mt-1 text-2xl font-semibold text-highlighted">
                            {{ school.numerRspo }}
                        </p>
                    </div>
                </div>
            </UCard>

            <div
                class="grid grid-cols-1 gap-6"
                :class="hasLeftColumnContent ? 'lg:grid-cols-12' : ''">
                <div
                    v-if="hasLeftColumnContent"
                    class="min-w-0 space-y-6 lg:col-span-8">
                    <UCard v-if="hasExamResults" :ui="{ body: 'space-y-4' }">
                        <template #header>
                            <div
                                class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                                <div>
                                    <h2
                                        class="text-lg font-semibold text-highlighted">
                                        Trend wzrostu
                                    </h2>
                                    <p class="text-sm text-muted">
                                        Wykres ważonego wyniku (matematyka,
                                        język polski, język angielski).
                                    </p>
                                </div>
                            </div>
                        </template>

                        <div
                            v-if="selectedExamSection?.weightedData.length"
                            class="weighted-chart-markers rounded-lg border border-default bg-default p-2">
                            <LineChart
                                :data="selectedExamSection.weightedData"
                                :categories="EXAM_TREND_CHART_CATEGORIES"
                                :height="220"
                                :x-formatter="trendXFormatter"
                                :x-num-ticks="
                                    selectedExamSection.weightedData.length
                                "
                                :y-num-ticks="4"
                                :marker-config="EXAM_TREND_MARKER_CONFIG"
                                :hide-legend="true"
                                :line-width="3"
                                :y-grid-line="true"
                                y-label="Wynik" />
                        </div>

                        <p v-else class="text-sm text-muted">
                            Brak kompletnych danych mediany do obliczenia
                            trendu.
                        </p>
                    </UCard>

                    <UCard v-if="hasExamResults" :ui="{ body: 'space-y-4' }">
                        <template #header>
                            <div
                                class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                                <h2
                                    class="text-lg font-semibold text-highlighted">
                                    Wyniki i analityka
                                </h2>

                                <div class="flex flex-col gap-2 sm:flex-row">
                                    <USelect
                                        v-model="selectedExamKey"
                                        :items="examTypeOptions"
                                        value-key="value"
                                        class="w-full sm:w-56" />
                                    <USelect
                                        v-model="selectedYear"
                                        :items="yearOptions"
                                        value-key="value"
                                        class="w-full sm:w-32" />
                                </div>
                            </div>
                        </template>

                        <div class="space-y-4">
                            <UCard :ui="{ body: 'space-y-3' }">
                                <template #header>
                                    <h3
                                        class="text-sm font-medium text-highlighted">
                                        Które przedmioty poszły najlepiej?
                                    </h3>
                                </template>

                                <BarChart
                                    v-if="topSubjectChartData.length"
                                    :data="topSubjectChartData"
                                    :categories="topSubjectCategories"
                                    :y-axis="['score']"
                                    :height="260"
                                    :radius="4"
                                    :x-num-ticks="topSubjectChartData.length"
                                    :x-formatter="topSubjectXFormatter"
                                    :hide-legend="true"
                                    :y-grid-line="true"
                                    y-label="Wynik" />

                                <p v-else class="text-sm text-muted">
                                    Brak kompletnych danych wynikowych dla tego
                                    roku.
                                </p>
                            </UCard>

                            <UCard :ui="{ body: 'space-y-3' }">
                                <template #header>
                                    <h3
                                        class="text-sm font-medium text-highlighted">
                                        Szczegółowe wyniki
                                    </h3>
                                </template>

                                <div
                                    v-if="visibleRows.length"
                                    class="overflow-x-auto rounded-lg border border-default">
                                    <UTable
                                        :data="detailedResultsTableRows"
                                        :columns="detailedResultsColumns">
                                        <template #subject-cell="{ row }">
                                            <div
                                                class="inline-flex items-center gap-1 font-medium"
                                                :title="row.original.subject">
                                                <span>
                                                    {{ row.original.subject }}
                                                </span>
                                                <UPopover
                                                    v-if="
                                                        selectedExamKey ===
                                                            'em' &&
                                                        row.original
                                                            .usesFallback
                                                    ">
                                                    <UButton
                                                        icon="i-mdi-information-outline"
                                                        variant="ghost"
                                                        size="xs"
                                                        class="text-muted hover:text-default"
                                                        aria-label="Informacja o braku mediany" />

                                                    <template #content>
                                                        <div
                                                            class="max-w-64 bg-elevated p-2 text-xs text-default">
                                                            Dla wyników z tego
                                                            przedmiotu mediana
                                                            nie była dostępna,
                                                            więc pokazana jest
                                                            średnia.
                                                        </div>
                                                    </template>
                                                </UPopover>
                                            </div>
                                        </template>
                                    </UTable>
                                </div>

                                <UAlert
                                    v-else
                                    color="neutral"
                                    variant="soft"
                                    title="Brak danych szczegółowych"
                                    description="Dla wybranego filtra nie ma dostępnych rekordów wyników." />

                                <div v-if="hasCollapsedRows" class="pt-1">
                                    <UButton
                                        variant="soft"
                                        color="neutral"
                                        :icon="
                                            showAllRows
                                                ? 'i-lucide-chevron-up'
                                                : 'i-lucide-chevron-down'
                                        "
                                        @click="showAllRows = !showAllRows">
                                        {{
                                            showAllRows
                                                ? "Pokaż mniej"
                                                : `Pokaż wszystkie (${selectedYearRows.length})`
                                        }}
                                    </UButton>
                                </div>
                            </UCard>
                        </div>
                    </UCard>
                </div>

                <div
                    class="min-w-0 space-y-6"
                    :class="hasLeftColumnContent ? 'lg:col-span-4' : ''">
                    <UCard v-if="hasRankingGroups" :ui="{ body: 'space-y-4' }">
                        <template #header>
                            <h2 class="text-lg font-semibold text-highlighted">
                                Ranking
                            </h2>
                        </template>

                        <div class="space-y-4">
                            <div
                                v-for="group in rankingGroups"
                                :key="`${group.examType}-${group.year}`"
                                class="space-y-2">
                                <USeparator
                                    :label="`${group.label} · ${group.year}`" />

                                <UCard
                                    v-for="row in group.rows"
                                    :key="`${group.examType}-${group.year}-${row.scope}`"
                                    :ui="{ body: 'p-3' }">
                                    <div
                                        class="grid grid-cols-1 items-center gap-3 sm:grid-cols-[minmax(0,1fr)_110px]">
                                        <div>
                                            <p
                                                class="font-semibold"
                                                :class="row.textClass">
                                                TOP
                                                {{
                                                    formatPercentyl(
                                                        row.percentyl,
                                                    )
                                                }}%
                                            </p>
                                            <UBadge
                                                class="mt-1"
                                                variant="soft"
                                                :color="
                                                    getRankingScopeColor(
                                                        row.scope,
                                                    )
                                                ">
                                                {{ row.scopeLabel }}
                                            </UBadge>
                                            <p class="mt-1 text-xs text-muted">
                                                #{{ row.miejsce }} /
                                                {{ row.liczbaSzkol }}
                                            </p>
                                            <p
                                                class="mt-1 text-sm font-medium text-highlighted">
                                                Lepsza od
                                                {{
                                                    formatPercentyl(
                                                        getBetterThanPercent(
                                                            row.percentyl,
                                                        ),
                                                    )
                                                }}% szkół
                                            </p>
                                        </div>

                                        <div class="relative">
                                            <DonutChart
                                                :data="
                                                    getRankingDonutData(
                                                        row.percentyl,
                                                    )
                                                "
                                                :categories="
                                                    rankingDonutCategories
                                                "
                                                :height="120"
                                                :radius="0"
                                                :arc-width="16"
                                                :hide-legend="true" />
                                            <div
                                                class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                                                <span
                                                    class="text-[10px] text-muted">
                                                    Lepsza od
                                                </span>
                                                <span
                                                    class="text-lg font-semibold text-success">
                                                    {{
                                                        formatPercentyl(
                                                            getBetterThanPercent(
                                                                row.percentyl,
                                                            ),
                                                        )
                                                    }}%
                                                </span>
                                            </div>
                                        </div>
                                    </div>
                                </UCard>
                            </div>
                        </div>
                    </UCard>

                    <SchoolInfoCard :school="school" />
                </div>
            </div>
        </div>
    </UContainer>
</template>

<style scoped>
@reference "tailwindcss";

.weighted-chart-markers :deep(*[stroke="#2563eb"]) {
    marker: url("#weighted-chart-weighted");
}
</style>
