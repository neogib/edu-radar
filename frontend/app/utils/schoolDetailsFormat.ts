export const formatNumber = (
    value: number | null | undefined,
    maximumFractionDigits = 2,
): string => {
    if (value === null || value === undefined) return "-"

    return new Intl.NumberFormat("pl-PL", {
        minimumFractionDigits: 0,
        maximumFractionDigits,
    }).format(value)
}

export const formatPercent = (
    value: number | null | undefined,
    maximumFractionDigits = 2,
): string => {
    if (value === null || value === undefined) return "-"
    return `${formatNumber(value, maximumFractionDigits)}%`
}

export const compactSubjectLabel = (subject: string): string => {
    return subject
        .replace("poziom podstawowy", "podst.")
        .replace("poziom rozszerzony", "rozs.")
        .replace("poziom dwujęzyczny", "dwujęz.")
        .replace("zestaw zadań w języku angielskim", "zestaw ang.")
}
