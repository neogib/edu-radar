import type { SzkolaPublicShort } from "~/types/schools"

export const transformSchoolsToFeatures = (
    schools: SzkolaPublicShort[],
): GeoJSON.Feature<GeoJSON.Point>[] => {
    return schools.map((school) => ({
        type: "Feature",
        properties: {
            id: school.id,
            nazwa: school.nazwa,
            typ: school.typ.nazwa,
            status: school.status_publicznoprawny.nazwa,
            score: school.score ? Number(school.score.toFixed(2)) : null,
        },
        geometry: {
            type: "Point",
            coordinates: [
                parseFloat(school.geolokalizacja_longitude.toFixed(6)),
                parseFloat(school.geolokalizacja_latitude.toFixed(6)),
            ],
        },
    }))
}
