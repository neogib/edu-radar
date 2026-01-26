import type { GeoJSONSource } from "maplibre-gl"
import type { SzkolaPublicShort } from "~/types/schools"

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
        let featureBuffer: any[] = []
        let isMapUpdating = false

        // the "worker" function that feeds the map
        const processBuffer = async () => {
            // if already updating or nothing to update, stop.
            if (isMapUpdating || featureBuffer.length === 0) return

            isMapUpdating = true

            // take everything currently in the buffer
            // this is auto-batching, if the stream is fast, this array is huge
            // if the stream is slow, this array is small.
            const featuresBatch = [...featureBuffer]
            featureBuffer = [] // clear global buffer immediately

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

        // start the Stream
        await streamFetch<SzkolaPublicShort[]>(
            `/schools/stream?${urlQueryParams.toString()}`,
            {
                signal,
                onChunk: (chunk) => {
                    const features = transformSchoolsToFeatures(chunk)

                    featureBuffer.push(...features)

                    // trigger processing evry time new data arrives
                    processBuffer()
                },
            },
        )

        // final flush if not aborted
        if (!signal.aborted && featureBuffer.length > 0) {
            processBuffer()
        }
    }
    return updateSchoolsFeatures
}
