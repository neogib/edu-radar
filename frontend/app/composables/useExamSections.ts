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
import { normalizeSubjectName } from "~/utils/normalizeSubjects"

interface UseExamSectionsOptions {
    wynikiE8: MaybeRefOrGetter<WynikE8PublicWithPrzedmiot[]>
    wynikiEm: MaybeRefOrGetter<WynikEMPublicWithPrzedmiot[]>
}

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
                ? (result as WynikE8PublicWithPrzedmiot).wynikSredni
                : (result as WynikEMPublicWithPrzedmiot).sredniWynik
        const wynik = median ?? fallback

        if (median === null && fallback !== null) {
            grouped[subjectName].usesFallback = true
        }

        grouped[subjectName].years[result.rok] = {
            wynik,
            liczba_zdajacych: result.liczbaZdajacych,
            zdawalnosc:
                key === "em"
                    ? (result as WynikEMPublicWithPrzedmiot).zdawalnosc
                    : null,
            liczba_laureatow_finalistow:
                key === "em"
                    ? (result as WynikEMPublicWithPrzedmiot)
                          .liczbaLaureatowFinalistow
                    : null,
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

export const useExamSections = (options: UseExamSectionsOptions) => {
    const examSections = computed(() => {
        const sections: ExamSection[] = []

        const wynikiE8 = toValue(options.wynikiE8)
        const wynikiEm = toValue(options.wynikiEm)

        if (wynikiE8.length) {
            sections.push(
                buildExamSection(
                    "e8",
                    "Wyniki z egzaminu ósmoklasisty",
                    wynikiE8,
                ),
            )
        }

        if (wynikiEm.length) {
            sections.push(
                buildExamSection(
                    "em",
                    "Wyniki z egzaminu maturalnego",
                    wynikiEm,
                ),
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
            const priorityIndex = priorityOrder.get(
                normalizeSubjectName(subject),
            )

            if (priorityIndex !== undefined) prioritized.push(entry)
            else rest.push(entry)
        }

        prioritized.sort(([subjectA], [subjectB]) => {
            const aPriority =
                priorityOrder.get(normalizeSubjectName(subjectA)) ?? 999
            const bPriority =
                priorityOrder.get(normalizeSubjectName(subjectB)) ?? 999
            return aPriority - bPriority
        })

        return [...prioritized, ...rest]
    }

    return {
        examSections,
        hasExamResults,
        getOrderedSubjects,
        chartCategories,
        weightedMarkerConfig,
    }
}
