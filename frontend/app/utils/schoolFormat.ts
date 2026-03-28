import type { SzkolaPublicWithRelations } from "~/types/schools"

type SchoolAddressInput = Pick<
    SzkolaPublicWithRelations,
    "ulica" | "numerBudynku" | "numerLokalu" | "kodPocztowy" | "miejscowosc"
>

const DEFAULT_FALLBACK = "brak danych"

export const formatSchoolDate = (
    value: string | null | undefined,
    fallback = DEFAULT_FALLBACK,
): string => {
    if (!value) return fallback

    const date = new Date(value)
    if (Number.isNaN(date.getTime())) return fallback

    return date.toLocaleDateString("pl-PL", {
        year: "numeric",
        month: "2-digit",
        day: "2-digit",
    })
}

export const formatSchoolAddressLines = (
    school: SchoolAddressInput,
): string[] => {
    const firstLine = [
        school.ulica?.nazwa,
        school.numerBudynku,
        school.numerLokalu ? `lok. ${school.numerLokalu}` : null,
    ]
        .filter(Boolean)
        .join(" ")

    const secondLine = [school.kodPocztowy, school.miejscowosc.nazwa]
        .filter(Boolean)
        .join(" ")

    return [firstLine, secondLine].filter(Boolean)
}

export const formatSchoolAddress = (
    school: SchoolAddressInput,
    fallback = DEFAULT_FALLBACK,
): string => {
    const lines = formatSchoolAddressLines(school)
    return lines.join(", ") || fallback
}
