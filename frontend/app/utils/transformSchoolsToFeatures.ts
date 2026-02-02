import type { SchoolFeature, SzkolaPublicShort } from "~/types/schools"

export const transformSchoolsToFeatures = (
    schools: SzkolaPublicShort[],
): SchoolFeature[] => {
    return schools.map((school) => ({
        type: "Feature",
        properties: {
            id: school.id,
            nazwa: school.nazwa,
            typ: school.typ,
            status: school.status,
            wynik: school.wynik ? Number(school.wynik.toFixed(2)) : null,
        },
        geometry: {
            type: "Point",
            coordinates: [
                parseFloat(school.longitude.toFixed(6)),
                parseFloat(school.latitude.toFixed(6)),
            ],
        },
    }))
}
