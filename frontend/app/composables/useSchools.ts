import type { SchoolFilterParams, SzkolaPublicShort } from "~/types/schools"

type FetchSchoolsOptions = {
    query?: SchoolFilterParams
    signal?: AbortSignal
}

export const useSchools = () => {
    const { $api } = useNuxtApp()

    const fetchSchools = async (options?: FetchSchoolsOptions) => {
        const data = await $api<SzkolaPublicShort[]>(
            "/schools/",
            options,
        ).catch((error) => {
            if (error instanceof Error && error.name === "FetchError") {
                console.log("Fetch schools aborted by signal in useSchools.ts")
                return [] as SzkolaPublicShort[]
            }
            console.error("Error fetching schools:", error)
            throw error
        })
        return data
    }

    const schoolsGeoJSONFeatures = async (options?: FetchSchoolsOptions) => {
        const schools = await fetchSchools(options)
        return transformSchoolsToFeatures(schools)
    }

    const fetchSchoolShort = async (schoolId: number) =>
        $api<SzkolaPublicShort>(`/schools/${schoolId}/short`)

    return { fetchSchools, schoolsGeoJSONFeatures, fetchSchoolShort }
}
