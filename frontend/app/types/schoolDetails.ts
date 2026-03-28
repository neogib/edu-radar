export interface YearRow {
    id: string
    subject: string
    score: number | null
    usesFallback: boolean
    participants: number | null
    passRate: number | null
    laureates: number | null
}

export interface TopSubjectChartPoint {
    subject: string
    score: number
}

export interface DetailedResultsTableRow {
    id: string
    subject: string
    usesFallback: boolean
    score: number | null
    participants: string
    passRate: string
    laureates: string
}
