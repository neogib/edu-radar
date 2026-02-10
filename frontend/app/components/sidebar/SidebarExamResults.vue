<script setup lang="ts">
import { EM_PRIORITY_SUBJECTS } from "~/constants/subjects"
import type {
    WynikE8PublicWithPrzedmiot,
    WynikEMPublicWithPrzedmiot,
} from "~/types/schools"

interface Props {
    wynikiE8: WynikE8PublicWithPrzedmiot[]
    wynikiEm: WynikEMPublicWithPrzedmiot[]
}

const { wynikiE8, wynikiEm } = defineProps<Props>()

type WynikPublicWithPrzedmiot =
    | WynikE8PublicWithPrzedmiot
    | WynikEMPublicWithPrzedmiot

type GroupedResults = Record<
    string,
    {
        usesFallback: boolean
        years: Record<
            number,
            {
                wynik: number | null
                liczba_zdajacych: number | null
            }
        >
    }
>

const emPriorityOrder = new Map(
    EM_PRIORITY_SUBJECTS.map((subject, index) => [
        normalizeSubjectName(subject),
        index,
    ]),
)

const buildExamSection = <T extends WynikPublicWithPrzedmiot>(
    key: "e8" | "em",
    title: string,
    results: T[],
) => {
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
            key == "e8"
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

    return {
        key,
        title,
        years: Array.from(yearsSet).sort((a, b) => a - b),
        grouped,
    }
}

const examSections = computed(() => {
    const sections = []

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

const getOrderedSubjects = (section: {
    key: "e8" | "em"
    grouped: GroupedResults
}) => {
    const entries = Object.entries(section.grouped)

    // only prioritize EM subjects, for E8 we can keep the original order
    if (section.key !== "em") {
        return entries
    }

    const prioritized: typeof entries = []
    const rest: typeof entries = []

    for (const entry of entries) {
        const [subject] = entry
        const priorityIndex = emPriorityOrder.get(normalizeSubjectName(subject))

        if (priorityIndex !== undefined) prioritized.push(entry)
        else rest.push(entry)
    }

    prioritized.sort((a, b) => {
        const aPriority = emPriorityOrder.get(normalizeSubjectName(a[0])) ?? 999
        const bPriority = emPriorityOrder.get(normalizeSubjectName(b[0])) ?? 999
        return aPriority - bPriority
    })

    return [...prioritized, ...rest]
}
</script>

<template>
    <!-- Exam Results Section -->
    <div v-if="hasExamResults" class="p-4 border-b">
        <h4 class="text-sm font-medium text-gray-700 mb-3 flex items-center">
            <Icon name="mdi:school" class="w-4 h-4 mr-2 text-green-500" />
            Wyniki z egzaminów
        </h4>

        <div
            v-for="(section, sectionIndex) in examSections"
            :key="section.key"
            class="overflow-x-auto"
            :class="{ 'mb-6': sectionIndex < examSections.length - 1 }">
            <h5 class="text-sm font-semibold text-gray-700 mb-2">
                {{ section.title }}
            </h5>
            <table class="w-full text-sm">
                <thead>
                    <tr class="border-b border-gray-300">
                        <th
                            class="text-left py-2 px-1 font-semibold text-gray-700 max-w-30 w-30">
                            Przedmiot
                        </th>
                        <th
                            v-for="year in section.years"
                            :key="`year-${section.key}-${year}`"
                            class="text-center py-2 px-1 font-semibold text-gray-700">
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
                        class="border-b border-gray-200">
                        <td class="py-3 px-1 text-gray-900">
                            <div
                                class="inline-flex items-center gap-1 font-medium"
                                :title="subject">
                                <span>{{ subject }}</span>
                                <UPopover v-if="subjectData.usesFallback">
                                    <UButton
                                        icon="i-mdi-information-outline"
                                        variant="ghost"
                                        size="xs"
                                        class="text-gray-500 hover:text-gray-700"
                                        aria-label="Informacja o braku mediany" />

                                    <template #content>
                                        <div
                                            class="max-w-64 p-2 text-xs text-gray-700">
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
                                <div class="text-xs text-gray-500">
                                    {{
                                        `#${subjectData.years[year]?.liczba_zdajacych}`
                                    }}
                                </div>
                            </template>
                            <span v-else class="text-gray-300">-</span>
                        </td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>
