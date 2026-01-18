<script setup lang="ts">
import type {
    WynikE8PublicWithPrzedmiot,
    WynikEMPublicWithPrzedmiot,
} from "~/types/schools"

interface Props {
    wynikiE8: WynikE8PublicWithPrzedmiot[]
    wynikiEm: WynikEMPublicWithPrzedmiot[]
}

const props = defineProps<Props>()

const { getColor } = useScoreColor()

const groupResultsBySubject = (
    results: WynikE8PublicWithPrzedmiot[] | WynikEMPublicWithPrzedmiot[],
) => {
    const grouped: Record<
        string,
        Record<number, WynikE8PublicWithPrzedmiot | WynikEMPublicWithPrzedmiot>
    > = {}
    const years = new Set<number>()

    results.forEach((result) => {
        const subjectName = result.przedmiot.nazwa
        years.add(result.rok)

        if (!grouped[subjectName]) {
            grouped[subjectName] = {}
        }
        grouped[subjectName][result.rok] = result
    })

    return { grouped, years: Array.from(years).sort() }
}

const e8Data = computed(() => groupResultsBySubject(props.wynikiE8))
const emData = computed(() => groupResultsBySubject(props.wynikiEm))
</script>
<template>
    <!-- Exam Results Section -->
    <div v-if="wynikiE8.length || wynikiEm.length" class="p-4 border-b">
        <h4 class="exam-title">
            <Icon name="mdi:school" class="exam-icon text-green-500" />
            Wyniki z egzaminów
        </h4>

        <!-- E8 Results Table -->
        <div v-if="wynikiE8?.length" class="overflow-x-auto mb-6">
            <table class="w-full text-sm">
                <thead>
                    <tr class="border-b border-gray-300">
                        <th
                            class="text-left py-2 px-1 font-semibold text-gray-700 max-w-30 w-30">
                            Przedmiot
                        </th>
                        <th
                            v-for="year in e8Data.years"
                            :key="`year-${year}`"
                            class="text-center py-2 px-1 font-semibold text-gray-700">
                            {{ year }}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr
                        v-for="(yearData, subject) in e8Data.grouped"
                        :key="`e8-${subject}`"
                        class="border-b border-gray-200">
                        <td class="py-3 px-1 text-gray-900">
                            <div class="font-medium" :title="subject">
                                {{ subject }}
                            </div>
                        </td>
                        <td
                            v-for="year in e8Data.years"
                            :key="`e8-${subject}-${year}`"
                            class="text-center py-3 px-1">
                            <template v-if="yearData[year]">
                                <div
                                    class="text-2xl font-bold mb-1"
                                    :style="{
                                        color: getColor(
                                            (
                                                yearData[
                                                    year
                                                ] as WynikE8PublicWithPrzedmiot
                                            ).wynik_sredni || 0,
                                        ),
                                    }">
                                    {{
                                        Math.round(
                                            (
                                                yearData[
                                                    year
                                                ] as WynikE8PublicWithPrzedmiot
                                            ).wynik_sredni || 0,
                                        )
                                    }}
                                </div>
                                <div class="text-xs text-gray-500">
                                    {{
                                        yearData[year].liczba_zdajacych
                                            ? `#${yearData[year].liczba_zdajacych}`
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

        <!-- Matura Results Table -->
        <div v-if="wynikiEm?.length" class="overflow-x-auto">
            <table class="w-full text-sm">
                <thead>
                    <tr class="border-b border-gray-300">
                        <th
                            class="text-left py-2 px-1 font-semibold text-gray-700 max-w-30 w-30">
                            Przedmiot
                        </th>
                        <th
                            v-for="year in emData.years"
                            :key="`year-${year}`"
                            class="text-center py-2 px-1 font-semibold text-gray-700">
                            {{ year }}
                        </th>
                    </tr>
                </thead>
                <tbody>
                    <tr
                        v-for="(yearData, subject) in emData.grouped"
                        :key="`em-${subject}`"
                        class="border-b border-gray-200">
                        <td class="py-3 px-1 text-gray-900">
                            <div class="font-medium" :title="subject">
                                {{ subject }}
                            </div>
                        </td>
                        <td
                            v-for="year in emData.years"
                            :key="`em-${subject}-${year}`"
                            class="text-center py-3 px-1">
                            <template v-if="yearData[year]">
                                <div
                                    class="text-2xl font-bold mb-1"
                                    :style="{
                                        color: getColor(
                                            (
                                                yearData[
                                                    year
                                                ] as WynikEMPublicWithPrzedmiot
                                            ).sredni_wynik || 0,
                                        ),
                                    }">
                                    {{
                                        Math.round(
                                            (
                                                yearData[
                                                    year
                                                ] as WynikEMPublicWithPrzedmiot
                                            ).sredni_wynik || 0,
                                        )
                                    }}
                                </div>
                                <div class="text-xs text-gray-500">
                                    {{
                                        yearData[year].liczba_zdajacych
                                            ? `#${yearData[year].liczba_zdajacych}`
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
</style>
