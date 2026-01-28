import type { GeoJSONSource } from "maplibre-gl"
import type { SchoolFeature, SzkolaPublicShort } from "~/types/schools"

/**
 * Composable to update school features on the map using streaming data.
 * MapLibre has an internal queue for updateData on source, but flooding it can cause the "missing points" visual glitch if the worker gets overwhelmed or if the main thread locks up.
 * This composable implements a buffering and batching mechanism to feed data to the map source in manageable chunks.
 */
export const useSchoolsFeaturesUpdater = () => {
    const updateSchoolsFeatures = async (
        urlQueryParams: URLSearchParams,
        signal: AbortSignal,
        source: GeoJSONSource,
    ) => {
        const { streamFetch } = useStreamFetch()

        // setup a Buffer and a Processing Flag
        let featureBuffer: SchoolFeature[] = []
        // Use an object to avoid TypeScript narrowing issues
        const processingState = {
            promise: null as Promise<void> | null,
        }

        // the "worker" function that feeds the map
        const processBuffer = async () => {
            // more data may arrive while updating, so loop until empty
            while (featureBuffer.length > 0) {
                // stop processing immediately if aborted
                if (signal.aborted) {
                    featureBuffer = [] // clear memory
                    break
                }

                // take everything currently in the buffer - auto batching
                const featuresBatch = [...featureBuffer]
                featureBuffer = [] // clear global buffer immediately

                try {
                    await source.updateData({ add: featuresBatch }, true)
                    console.log("Updated map with", featuresBatch.length)
                } catch (e) {
                    console.error("Error updating map data", e)
                }
            }
            processingState.promise = null
        }

        // start the Stream
        await streamFetch<SzkolaPublicShort[]>(
            `/schools/stream?${urlQueryParams.toString()}`,
            {
                signal,
                onChunk: (chunk) => {
                    featureBuffer.push(...transformSchoolsToFeatures(chunk))

                    // trigger processing evry time new data arrives
                    processingState.promise ??= processBuffer()
                },
            },
        )

        // wait for any ongoing processing to finish
        if (processingState.promise) {
            await processingState.promise
        }
    }
    return updateSchoolsFeatures
}
