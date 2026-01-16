import type { Feature, FeatureCollection, Point } from "geojson"
import type { SzkolaPublicShort } from "~/types/schools"

export const useSchoolGeoJson = (
    schools: Ref<SzkolaPublicShort[] | undefined>,
) => {
    const transformSchoolsToFeatures = (
        schools: SzkolaPublicShort[],
    ): Feature<Point, SzkolaPublicShort>[] => {
        return schools.map((school) => ({
            type: "Feature",
            properties: {
                id: school.id,
                nazwa: school.nazwa,
                typ: school.typ,
                status_publicznoprawny: school.status_publicznoprawny,
                score: school.score ? Number(school.score.toFixed(2)) : null,
            },
            geometry: {
                type: "Point",
                coordinates: [
                    school.geolokalizacja_longitude.toFixed(6),
                    school.geolokalizacja_latitude.toFixed(6),
                ],
            },
        }))
    }

    const geoJsonSource = computed<FeatureCollection<Point, SzkolaPublicShort>>(
        () => {
            const features = schools.value
                ? transformSchoolsToFeatures(schools.value)
                : []

            return {
                type: "FeatureCollection",
                features,
            }
        },
    )

    return { geoJsonSource }
}
