<script setup lang="ts">
import { useExamSections } from "~/composables/useExamSections"
import {
    EXAM_TREND_CHART_CATEGORIES,
    EXAM_TREND_MARKER_CONFIG,
} from "~/constants/examSections"
import type {
    WynikE8PublicWithPrzedmiot,
    WynikEMPublicWithPrzedmiot,
} from "~/types/schools"

interface Props {
    wynikiE8: WynikE8PublicWithPrzedmiot[]
    wynikiEm: WynikEMPublicWithPrzedmiot[]
}

const { wynikiE8, wynikiEm } = defineProps<Props>()

const { examSections, hasExamResults } = useExamSections({
    wynikiE8: () => wynikiE8,
    wynikiEm: () => wynikiEm,
})
</script>

<template>
    <!-- Exam Results Section -->
    <div v-if="hasExamResults" class="p-4 border-b border-default">
        <h4 class="text-sm font-medium text-default mb-3 flex items-center">
            <UIcon name="i-mdi-school" class="w-4 h-4 mr-2 text-green-500" />
            Wyniki z egzaminów
            <UPopover>
                <UButton
                    icon="i-mdi-information-outline"
                    variant="ghost"
                    size="xs"
                    class="ml-1 text-muted hover:text-default"
                    aria-label="Informacja o medianie i średniej" />

                <template #content>
                    <div class="max-w-64 bg-elevated p-2 text-xs text-default">
                        Domyślnie pokazujemy medianę z wyników dla przedmiotu.
                        Jeśli mediana nie jest dostępna, pokazujemy średnią
                        wyników z egzaminów.
                    </div>
                </template>
            </UPopover>
        </h4>

        <div
            v-for="(section, sectionIndex) in examSections"
            :key="section.key"
            class="overflow-x-auto"
            :class="{ 'mb-6': sectionIndex < examSections.length - 1 }">
            <h5 class="text-sm font-semibold text-default mb-2">
                {{ section.title }}
            </h5>

            <div
                v-if="section.weightedData.length"
                class="weighted-chart-markers mb-4 rounded-lg border border-default bg-default p-2">
                <LineChart
                    :data="section.weightedData"
                    :categories="EXAM_TREND_CHART_CATEGORIES"
                    :height="180"
                    :x-formatter="
                        (tick: number): string =>
                            `${section.weightedData[tick]?.year ?? ''}`
                    "
                    :x-num-ticks="section.weightedData.length"
                    :y-num-ticks="3"
                    :marker-config="EXAM_TREND_MARKER_CONFIG"
                    :hide-legend="true"
                    :line-width="3"
                    :y-grid-line="true"
                    y-label="Wynik" />
            </div>
            <p v-else class="mb-4 text-xs text-muted">
                Brak kompletnych danych mediany do obliczenia trendu.
            </p>

            <table class="w-full text-sm">
                <thead>
                    <tr class="border-b border-default">
                        <th
                            class="text-left py-2 px-1 font-semibold text-default max-w-30 w-30">
                            Przedmiot
                        </th>
                        <th
                            v-for="year in section.years"
                            :key="`year-${section.key}-${year}`"
                            class="text-center py-2 px-1 font-semibold text-default">
                            {{ year }}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr
                        v-for="[subject, subjectData] in getOrderedExamSubjects(
                            section,
                        )"
                        :key="`${section.key}-${subject}`"
                        class="border-b border-default">
                        <td class="py-3 px-1 text-highlighted">
                            <div
                                class="inline-flex items-center gap-1 font-medium"
                                :title="subject">
                                <span>{{ subject }}</span>
                                <UPopover v-if="subjectData.usesFallback">
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
                        </td>
                        <td
                            v-for="year in section.years"
                            :key="`${section.key}-${subject}-${year}`"
                            class="align-top text-center py-3 px-1">
                            <template v-if="subjectData.years[year]">
                                <UPopover
                                    :content="{
                                        side: 'top',
                                        align: 'center',
                                        sideOffset: 6,
                                    }">
                                    <button
                                        type="button"
                                        class="flex h-full w-full flex-col items-center justify-start rounded-md px-1 py-1 transition-colors hover:bg-accented/40 focus-visible:outline-2 focus-visible:outline-primary">
                                        <div
                                            class="text-2xl font-bold"
                                            :style="{
                                                color: getScoreColor(
                                                    subjectData.years[year]
                                                        ?.wynik,
                                                ),
                                            }">
                                            {{
                                                Math.round(
                                                    subjectData.years[year]
                                                        ?.wynik ?? 0,
                                                )
                                            }}
                                        </div>
                                        <div
                                            class="mt-1 flex flex-wrap items-center justify-center gap-x-2 gap-y-1 text-xs text-muted">
                                            <span
                                                class="inline-flex items-center gap-1">
                                                <UIcon
                                                    name="i-lucide-users"
                                                    class="size-3" />
                                                {{
                                                    subjectData.years[year]
                                                        ?.liczba_zdajacych ??
                                                    "brak danych"
                                                }}
                                            </span>
                                            <span
                                                v-if="
                                                    section.key === 'em' &&
                                                    subjectData.years[year]
                                                        ?.zdawalnosc !== null
                                                "
                                                class="inline-flex items-center gap-1">
                                                <UIcon
                                                    name="i-mdi-percent"
                                                    class="size-3" />
                                                {{
                                                    `${Math.round(subjectData.years[year]?.zdawalnosc ?? 0)}%`
                                                }}
                                            </span>
                                            <span
                                                v-if="
                                                    section.key === 'em' &&
                                                    subjectData.years[year]
                                                        ?.liczba_laureatow_finalistow !==
                                                        null
                                                "
                                                class="inline-flex items-center gap-1">
                                                <UIcon
                                                    name="i-mdi-trophy-outline"
                                                    class="size-3" />
                                                {{
                                                    subjectData.years[year]
                                                        ?.liczba_laureatow_finalistow
                                                }}
                                            </span>
                                        </div>
                                    </button>

                                    <template #content>
                                        <div
                                            class="rounded-md bg-elevated px-2 py-1.5 text-[11px] leading-tight text-default">
                                            <p>
                                                {{
                                                    `Liczba zdających: ${subjectData.years[year]?.liczba_zdajacych ?? "brak danych"}`
                                                }}
                                            </p>
                                            <p
                                                v-if="
                                                    section.key === 'em' &&
                                                    subjectData.years[year]
                                                        ?.zdawalnosc !== null
                                                ">
                                                {{
                                                    `Zdawalność: ${Math.round(subjectData.years[year]?.zdawalnosc ?? 0)}%`
                                                }}
                                            </p>
                                            <p
                                                v-if="
                                                    section.key === 'em' &&
                                                    subjectData.years[year]
                                                        ?.liczba_laureatow_finalistow !==
                                                        null
                                                ">
                                                {{
                                                    `Liczba laureatów/finalistów: ${subjectData.years[year]?.liczba_laureatow_finalistow}`
                                                }}
                                            </p>
                                        </div>
                                    </template>
                                </UPopover>
                            </template>
                            <span v-else class="text-dimmed">-</span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>

<style scoped>
.weighted-chart-markers :deep(*[stroke="#2563eb"]) {
    marker: url("#weighted-chart-weighted");
}
</style>
