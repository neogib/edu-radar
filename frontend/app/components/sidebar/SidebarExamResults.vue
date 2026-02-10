<script setup lang="ts">
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
    Record<
        number,
        {
            wynik: number | null
            liczba_zdajacych: number | null
        }
    >
>

const buildExamSection = <T extends WynikPublicWithPrzedmiot>(
    key: "e8" | "em",
    title: string,
    results: T[],
    getScore: (result: T) => number | null,
) => {
    const yearsSet = new Set<number>()
    const grouped: GroupedResults = {}

    for (const result of results) {
        yearsSet.add(result.rok)
        const subjectName = result.przedmiot.nazwa

        if (!grouped[subjectName]) {
            grouped[subjectName] = {}
        }

        grouped[subjectName][result.rok] = {
            wynik: getScore(result),
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
            buildExamSection(
                "e8",
                "Wyniki z egzaminu ósmoklasisty",
                wynikiE8,
                (result) => result.wynik_sredni,
            ),
        )
    }

    if (wynikiEm.length) {
        sections.push(
            buildExamSection(
                "em",
                "Wyniki z egzaminu maturalnego",
                wynikiEm,
                (result) => result.sredni_wynik,
            ),
        )
    }

    return sections
})

const hasExamResults = computed(() => examSections.value.length > 0)

const formatScore = (wynik: number | null) => Math.round(wynik ?? 0)
const scoreColor = (wynik: number | null) => getScoreColor(wynik ?? 0)
</script>
<template>
    <!-- Exam Results Section -->
    <div v-if="hasExamResults" class="p-4 border-b">
        <h4 class="exam-title">
            <Icon name="mdi:school" class="exam-icon text-green-500" />
            Wyniki z egzaminów
        </h4>

        <div
            v-for="(section, sectionIndex) in examSections"
            :key="section.key"
            class="overflow-x-auto"
            :class="{ 'mb-6': sectionIndex < examSections.length - 1 }">
            <h5 class="exam-subtitle">
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
                        v-for="(yearData, subject) in section.grouped"
                        :key="`${section.key}-${subject}`"
                        class="border-b border-gray-200">
                        <td class="py-3 px-1 text-gray-900">
                            <div class="font-medium" :title="subject">
                                {{ subject }}
                            </div>
                        </td>
                        <td
                            v-for="year in section.years"
                            :key="`${section.key}-${subject}-${year}`"
                            class="text-center py-3 px-1">
                            <template v-if="yearData[year]">
                                <div
                                    class="text-2xl font-bold mb-1"
                                    :style="{
                                        color: scoreColor(
                                            yearData[year]?.wynik ?? null,
                                        ),
                                    }">
                                    {{
                                        formatScore(
                                            yearData[year]?.wynik ?? null,
                                        )
                                    }}
                                </div>
                                <div class="text-xs text-gray-500">
                                    {{
                                        yearData[year]?.liczba_zdajacych
                                            ? `#${yearData[year]?.liczba_zdajacych}`
                                            : ""
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

<style scoped>
@reference "tailwindcss";
.exam-title {
    @apply text-sm font-medium text-gray-700 mb-3 flex items-center;
}
.exam-icon {
    @apply w-4 h-4 mr-2;
}
.exam-subtitle {
    @apply text-sm font-semibold text-gray-700 mb-2;
}
</style>
