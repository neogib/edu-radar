import type { ExamSectionKey, WeightedSubjectNames } from "~/types/subjects"

export const EM_PRIORITY_SUBJECTS = [
    "matematyka poziom podstawowy",
    "język angielski poziom podstawowy",
    "język polski poziom podstawowy",
    "matematyka poziom rozszerzony",
    "język angielski poziom rozszerzony",
    "język polski poziom rozszerzony",
    "język angielski ustny",
    "język polski ustny",
] as const

export const WEIGHTED_SUBJECTS: Record<ExamSectionKey, WeightedSubjectNames> = {
    e8: {
        math: normalizeSubjectName("matematyka"),
        polish: normalizeSubjectName("język polski"),
        english: normalizeSubjectName("język angielski"),
    },
    em: {
        math: normalizeSubjectName("matematyka poziom podstawowy"),
        polish: normalizeSubjectName("język polski poziom podstawowy"),
        english: normalizeSubjectName("język angielski poziom podstawowy"),
    },
}

export const SUBJECT_WEIGHTS = {
    math: 0.5,
    polish: 0.25,
    english: 0.25,
} as const
