import type { SzkolaPublicShort } from "~/types/schools"

export const useSchools = () => {
    const { $api } = useNuxtApp()

    const fetchSchools = async (options?: any) => {
        const data = await $api<SzkolaPublicShort[]>("/schools/", options)
        return data
    }

    const schoolsGeoJSONFeatures = async (options?: any) => {
        const schools = await fetchSchools(options)
        return transformSchoolsToFeatures(schools)
    }

    return { fetchSchools, schoolsGeoJSONFeatures }
}
