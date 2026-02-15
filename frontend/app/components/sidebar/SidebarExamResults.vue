<script setup lang="ts">
import {
    E8_PRIORITY_SUBJECTS,
    EM_PRIORITY_SUBJECTS,
    SUBJECT_WEIGHTS,
    WEIGHTED_SUBJECTS,
} from "~/constants/subjects"
import type {
    WynikE8PublicWithPrzedmiot,
    WynikEMPublicWithPrzedmiot,
    WynikPublicWithPrzedmiot,
} from "~/types/schools"
import type {
    ExamSection,
    ExamSectionKey,
    GroupedResults,
    WeightedPoint,
} from "~/types/subjects"

interface Props {
    wynikiE8: WynikE8PublicWithPrzedmiot[]
    wynikiEm: WynikEMPublicWithPrzedmiot[]
}

const { wynikiE8, wynikiEm } = defineProps<Props>()

const emPriorityOrder = new Map(
    EM_PRIORITY_SUBJECTS.map((subject, index) => [
        normalizeSubjectName(subject),
        index,
    ]),
)

const e8PriorityOrder = new Map(
    E8_PRIORITY_SUBJECTS.map((subject, index) => [
        normalizeSubjectName(subject),
        index,
    ]),
)

const getWeightedData = <T extends WynikPublicWithPrzedmiot>(
    key: ExamSectionKey,
    results: T[],
    years: number[],
): WeightedPoint[] => {
    if (!results.length || !years.length) return []

    const byYear = new Map<number, Map<string, number>>()

    for (const result of results) {
        if (result.mediana === null || result.mediana === undefined) continue

        const subject = normalizeSubjectName(result.przedmiot.nazwa)
        if (!byYear.has(result.rok)) {
            byYear.set(result.rok, new Map())
        }

        byYear.get(result.rok)?.set(subject, result.mediana)
    }

    const points: WeightedPoint[] = []
    const weightedSubjects = WEIGHTED_SUBJECTS[key]

    for (const year of years) {
        const yearMap = byYear.get(year)
        if (!yearMap) continue

        const math = yearMap.get(weightedSubjects.math)
        const polish = yearMap.get(weightedSubjects.polish)
        const english = yearMap.get(weightedSubjects.english)

        if (math === undefined || polish === undefined || english === undefined)
            continue

        points.push({
            year,
            weighted:
                math * SUBJECT_WEIGHTS.math +
                polish * SUBJECT_WEIGHTS.polish +
                english * SUBJECT_WEIGHTS.english,
        })
    }

    return points
}

const buildExamSection = <T extends WynikPublicWithPrzedmiot>(
    key: ExamSectionKey,
    title: string,
    results: T[],
): ExamSection => {
    const yearsSet = new Set<number>()
    const grouped: GroupedResults = {}

    for (const result of results) {
        yearsSet.add(result.rok)
        const subjectName = result.przedmiot.nazwa

        if (!grouped[subjectName]) {
            grouped[subjectName] = {
                usesFallback: false,
                years: {},
            }
        }

        const median = result.mediana ?? null
        const fallback =
            key === "e8"
                ? (result as WynikE8PublicWithPrzedmiot).wynik_sredni
                : (result as WynikEMPublicWithPrzedmiot).sredni_wynik
        const wynik = median ?? fallback

        if (median === null && fallback !== null) {
            grouped[subjectName].usesFallback = true
        }

        grouped[subjectName].years[result.rok] = {
            wynik,
            liczba_zdajacych: result.liczba_zdajacych,
        }
    }

    const years = Array.from(yearsSet).sort((a, b) => a - b)

    return {
        key,
        title,
        years,
        grouped,
        weightedData: getWeightedData(key, results, years),
    }
}

const examSections = computed(() => {
    const sections: ExamSection[] = []

    if (wynikiE8.length) {
        sections.push(
            buildExamSection("e8", "Wyniki z egzaminu ósmoklasisty", wynikiE8),
        )
    }

    if (wynikiEm.length) {
        sections.push(
            buildExamSection("em", "Wyniki z egzaminu maturalnego", wynikiEm),
        )
    }

    return sections
})

const hasExamResults = computed(() => examSections.value.length > 0)

const getOrderedSubjects = (section: ExamSection) => {
    const entries = Object.entries(section.grouped)

    const priorityOrder =
        section.key === "em" ? emPriorityOrder : e8PriorityOrder

    const prioritized: typeof entries = []
    const rest: typeof entries = []

    for (const entry of entries) {
        const [subject] = entry
        const priorityIndex = priorityOrder.get(normalizeSubjectName(subject))

        if (priorityIndex !== undefined) prioritized.push(entry)
        else rest.push(entry)
    }

    prioritized.sort((a, b) => {
        const aPriority = priorityOrder.get(normalizeSubjectName(a[0])) ?? 999
        const bPriority = priorityOrder.get(normalizeSubjectName(b[0])) ?? 999
        return aPriority - bPriority
    })

    return [...prioritized, ...rest]
}

const chartCategories = {
    weighted: {
        name: "Wynik",
        color: "#2563eb",
    },
}

const weightedMarkerConfig: MarkerConfig = {
    id: "weighted-chart",
    config: {
        weighted: {
            type: "circle",
            size: 8,
            color: "#2563eb",
            strokeColor: "#2563eb",
            strokeWidth: 2,
        },
    },
}
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
                    :categories="chartCategories"
                    :height="180"
                    :x-formatter="
                        (tick: number): string =>
                            `${section.weightedData[tick]?.year ?? ''}`
                    "
                    :x-num-ticks="section.weightedData.length"
                    :y-num-ticks="3"
                    :marker-config="weightedMarkerConfig"
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
                        v-for="[subject, subjectData] in getOrderedSubjects(
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
                            class="text-center py-3 px-1">
                            <template v-if="subjectData.years[year]">
                                <div
                                    class="text-2xl font-bold mb-1"
                                    :style="{
                                        color: getScoreColor(
                                            subjectData.years[year]?.wynik,
                                        ),
                                    }">
                                    {{
                                        Math.round(
                                            subjectData.years[year]?.wynik ?? 0,
                                        )
                                    }}
                                </div>
                                <div
                                    class="inline-flex items-center gap-1 text-xs text-muted">
                                    <UIcon
                                        name="i-lucide-users"
                                        class="size-3" />
                                    {{
                                        `${subjectData.years[year]?.liczba_zdajacych}`
                                    }}
                                </div>
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
