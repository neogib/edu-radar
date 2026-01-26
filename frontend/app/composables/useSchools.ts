import { transition } from "@vueuse/core"
import type { SzkolaPublicShort } from "~/types/schools"

export const useSchools = () => {
    const { $api } = useNuxtApp()

    const fetchSchools = async (options?: any) => {
        const data = await $api<SzkolaPublicShort[]>(
            "/schools/",
            options,
        ).catch((error) => {
            if (error.name === "FetchError") {
                console.log("Fetch schools aborted by signal in useSchools.ts")
                return [] as SzkolaPublicShort[]
            }
            console.error("Error fetching schools:", error)
            throw error
        })
        return data
    }

    const schoolsGeoJSONFeatures = async (options?: any) => {
        const schools = await fetchSchools(options)
        return transformSchoolsToFeatures(schools)
    }

    return { fetchSchools, schoolsGeoJSONFeatures }
}
