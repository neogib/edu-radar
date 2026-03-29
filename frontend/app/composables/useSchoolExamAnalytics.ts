import type { TableColumn } from "@nuxt/ui"
import type {
    DetailedResultsTableRow,
    TopSubjectChartPoint,
    YearRow,
} from "~/types/schoolDetails"
import type {
    WynikE8PublicWithPrzedmiot,
    WynikEMPublicWithPrzedmiot,
} from "~/types/schools"
import type { ExamSectionKey } from "~/types/subjects"
import {
    compactSubjectLabel,
    formatNumber,
    formatPercent,
} from "~/utils/schoolDetailsFormat"

const DEFAULT_VISIBLE_ROWS = 14

interface UseSchoolExamAnalyticsOptions {
    wynikiE8: () => WynikE8PublicWithPrzedmiot[]
    wynikiEm: () => WynikEMPublicWithPrzedmiot[]
}

export const useSchoolExamAnalytics = (
    options: UseSchoolExamAnalyticsOptions,
) => {
    const { examSections, hasExamResults } = useExamSections({
        wynikiE8: options.wynikiE8,
        wynikiEm: options.wynikiEm,
    })

    const examTypeOptions = computed<
        Array<{ label: string; value: ExamSectionKey }>
    >(() => {
        const result: Array<{ label: string; value: ExamSectionKey }> = []

        if (options.wynikiE8().length) {
            result.push({
                label: "Egzamin ósmoklasisty",
                value: "e8",
            })
        }

        if (options.wynikiEm().length) {
            result.push({
                label: "Matura",
                value: "em",
            })
        }

        return result
    })

    const selectedExamKey = ref<ExamSectionKey>("e8")

    watch(
        examTypeOptions,
        (items) => {
            const values = items.map((item) => item.value)
            if (!values.length) return

            if (!values.includes(selectedExamKey.value) && values[0]) {
                selectedExamKey.value = values[0]
            }
        },
        { immediate: true },
    )

    const selectedExamSection = computed(() =>
        examSections.value.find(
            (section) => section.key === selectedExamKey.value,
        ),
    )

    const yearOptions = computed<Array<{ label: string; value: number }>>(
        () => {
            const years = [...(selectedExamSection.value?.years ?? [])].sort(
                (a, b) => b - a,
            )

            return years.map((year) => ({
                label: String(year),
                value: year,
            }))
        },
    )

    const selectedYear = ref(0)

    watch(
        yearOptions,
        (items) => {
            const values = items.map((item) => item.value)
            if (!values.length) return

            if (!values.includes(selectedYear.value) && values[0]) {
                selectedYear.value = values[0]
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
            score: row.score,
            participants: formatNumber(row.participants, 0),
            passRate: formatPercent(row.passRate),
            laureates: formatNumber(row.laureates, 0),
        })),
    )

    const detailedResultsColumns = computed<
        TableColumn<DetailedResultsTableRow>[]
    >(() => {
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
    })

    const topSubjectChartData = computed<TopSubjectChartPoint[]>(() =>
        [...selectedYearRows.value]
            .filter(
                (row): row is YearRow & { score: number } => row.score !== null,
            )
            .sort((a, b) => b.score - a.score)
            .slice(0, 10)
            .map((row) => ({
                subject: compactSubjectLabel(row.subject),
                score: Number(row.score.toFixed(2)),
            })),
    )

    const trendXFormatter = (tick: number): string =>
        `${selectedExamSection.value?.weightedData[tick]?.year ?? ""}`

    const topSubjectXFormatter = (tick: number): string =>
        topSubjectChartData.value[tick]?.subject ?? ""

    const topSubjectCategories = {
        score: {
            name: "Wynik",
            color: "var(--ui-primary)",
        },
    }

    return {
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
    }
}
