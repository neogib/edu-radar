import type { SzkolaPublicShort } from "~/types/schools"

/**
 * Composable to update school features on the map using streaming data.
 * MapLibre has an internal queue for updateData on source, but flooding it can cause the "missing points" visual glitch if the worker gets overwhelmed or if the main thread locks up.
 * This composable implements a buffering and batching mechanism to feed data to the map source in manageable chunks.
 */
export const useSchoolsFeaturesUpdater = () => {
    // inside useSchoolGeoJSONSource.ts or where updateSchoolsFeatures is defined

    const updateSchoolsFeatures = async (
        urlQueryParams: URLSearchParams,
        map: maplibregl.Map, // pass map, not source, so we can ensure source exists
        sourceId: string,
    ) => {
        // wait until source is actually created
        const source = await useMapSource(map, sourceId)
        const { streamFetch } = useStreamFetch()

        // setup a Buffer and a Processing Flag
        let featureBuffer: any[] = []
        let isMapUpdating = false

        // the "worker" function that feeds the map
        const processBuffer = async () => {
            // if already updating or nothing to update, stop.
            if (isMapUpdating || featureBuffer.length === 0) return

            isMapUpdating = true

            // Take EVERYTHING currently in the buffer
            // This is auto-batching. If the stream is fast, this array is huge.
            // If the stream is slow, this array is small.
            const featuresBatch = [...featureBuffer]
            featureBuffer = [] // Clear global buffer immediately

            try {
                // await here so not to send the next batch until this one renders.
                await source.updateData({ add: featuresBatch }, true)
            } catch (e) {
                console.error("Error updating map data", e)
            } finally {
                isMapUpdating = false
                // check if more data arrived while map was updating
                if (featureBuffer.length > 0) {
                    processBuffer()
                }
            }
        }

        // 4. Start the Stream
        // We do NOT await processBuffer inside here. We just push and trigger.
        await streamFetch<SzkolaPublicShort[]>(
            `/schools/stream?${urlQueryParams.toString()}`,
            {
                onChunk: (chunk) => {
                    const features = transformSchoolsToFeatures(chunk)

                    // Add to buffer
                    featureBuffer.push(...features)

                    // Trigger processing
                    processBuffer()
                },
            },
        )

        // check to ensure nothing is left behind
        if (featureBuffer.length > 0) {
            processBuffer()
        }
    }
    return updateSchoolsFeatures
}
