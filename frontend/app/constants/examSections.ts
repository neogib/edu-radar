import {
    E8_PRIORITY_SUBJECTS,
    EM_PRIORITY_SUBJECTS,
} from "~/constants/subjects"
import type { ExamSectionKey } from "~/types/subjects"
import { normalizeSubjectName } from "~/utils/normalizeSubjects"

export const EXAM_SECTION_TITLES: Record<ExamSectionKey, string> = {
    e8: "Wyniki z egzaminu ósmoklasisty",
    em: "Wyniki z egzaminu maturalnego",
}

export const EXAM_SUBJECT_PRIORITY_ORDER: Record<
    ExamSectionKey,
    Map<string, number>
> = {
    em: new Map(
        EM_PRIORITY_SUBJECTS.map((subject, index) => [
            normalizeSubjectName(subject),
            index,
        ]),
    ),
    e8: new Map(
        E8_PRIORITY_SUBJECTS.map((subject, index) => [
            normalizeSubjectName(subject),
            index,
        ]),
    ),
}

export const EXAM_TREND_CHART_CATEGORIES = {
    weighted: {
        name: "Wynik",
        color: "#2563eb",
    },
}

export const EXAM_TREND_MARKER_CONFIG: MarkerConfig = {
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
