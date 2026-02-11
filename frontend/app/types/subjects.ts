export type ExamSectionKey = "e8" | "em"

type YearData = {
    wynik: number | null
    liczba_zdajacych: number | null
}

export type GroupedResults = Record<
    string,
    {
        usesFallback: boolean
        years: Record<number, YearData>
    }
>

export interface WeightedPoint {
    year: number
    weighted: number
}

export interface ExamSection {
    key: ExamSectionKey
    title: string
    years: number[]
    grouped: GroupedResults
    weightedData: WeightedPoint[]
}

export interface WeightedSubjectNames {
    math: string
    polish: string
    english: string
}
