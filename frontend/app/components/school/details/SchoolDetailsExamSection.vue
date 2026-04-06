<script setup lang="ts">
import {
    EXAM_TREND_CHART_CATEGORIES,
    EXAM_TREND_MARKER_CONFIG,
} from "~/constants/examSections"
import type {
    WynikE8PublicWithPrzedmiot,
    WynikEMPublicWithPrzedmiot,
} from "~/types/schools"
import { formatNumber } from "~/utils/schoolDetailsFormat"
import { getScoreColor } from "~/utils/scoreColor"

interface Props {
    wynikiE8: WynikE8PublicWithPrzedmiot[]
    wynikiEm: WynikEMPublicWithPrzedmiot[]
}

const props = defineProps<Props>()

const {
    hasExamResults,
    examTypeOptions,
    selectedExamKey,
    selectedExamSection,
    yearOptions,
    selectedYear,
    selectedYearRows,
    visibleRows,
    hasCollapsedRows,
    showAllRows,
    detailedResultsTableRows,
    detailedResultsColumns,
    topSubjectChartData,
    topSubjectCategories,
    trendXFormatter,
    topSubjectXFormatter,
} = useSchoolExamAnalytics({
    wynikiE8: () => props.wynikiE8,
    wynikiEm: () => props.wynikiEm,
})
</script>

<template>
    <div v-if="hasExamResults" class="space-y-6">
        <UCard :ui="{ body: 'space-y-4' }">
            <template #header>
                <div
                    class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                    <div>
                        <h2 class="text-lg font-semibold text-highlighted">
                            Trend wzrostu
                        </h2>
                        <p class="text-sm text-muted">
                            Wykres ważonego wyniku (matematyka, język polski,
                            język angielski).
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
                    :x-num-ticks="selectedExamSection.weightedData.length"
                    :y-num-ticks="4"
                    :marker-config="EXAM_TREND_MARKER_CONFIG"
                    :hide-legend="true"
                    :line-width="3"
                    :y-grid-line="true"
                    y-label="Wynik" />
            </div>

            <p v-else class="text-sm text-muted">
                Brak kompletnych danych mediany do obliczenia trendu.
            </p>
        </UCard>

        <UCard :ui="{ body: 'space-y-4' }">
            <template #header>
                <div
                    class="flex flex-col gap-3 lg:flex-row lg:items-center lg:justify-between">
                    <h2 class="text-lg font-semibold text-highlighted">
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
                        <h3 class="text-sm font-medium text-highlighted">
                            Które przedmioty poszły najlepiej?
                        </h3>
                    </template>

                    <div
                        v-if="topSubjectChartData.length"
                        class="overflow-x-auto">
                        <div class="min-w-160 sm:min-w-0">
                            <BarChart
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
                        </div>
                    </div>

                    <p v-else class="text-sm text-muted">
                        Brak kompletnych danych wynikowych dla tego roku.
                    </p>
                </UCard>

                <UCard :ui="{ body: 'space-y-3' }">
                    <template #header>
                        <h3 class="text-sm font-medium text-highlighted">
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
                                            selectedExamKey === 'em' &&
                                            row.original.usesFallback
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
                                                Dla wyników z tego przedmiotu
                                                mediana nie była dostępna, więc
                                                pokazana jest średnia.
                                            </div>
                                        </template>
                                    </UPopover>
                                </div>
                            </template>
                            <template #score-cell="{ row }">
                                <span
                                    class="text-lg font-bold"
                                    :style="{
                                        color:
                                            row.original.score !== null
                                                ? getScoreColor(
                                                      row.original.score,
                                                  )
                                                : undefined,
                                    }">
                                    {{ formatNumber(row.original.score) }}
                                </span>
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
</template>

<style scoped>
@reference "tailwindcss";

.weighted-chart-markers :deep(*[stroke="#2563eb"]) {
    marker: url("#weighted-chart-weighted");
}
</style>
