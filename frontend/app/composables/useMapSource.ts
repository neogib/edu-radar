import type { Map, GeoJSONSource } from "maplibre-gl"

export const useMapSource = (
    map: Map,
    sourceId: string,
): Promise<GeoJSONSource> => {
    const existingSource = map.getSource(sourceId)
    if (existingSource) {
        return Promise.resolve(existingSource as GeoJSONSource)
    }

    return new Promise((resolve) => {
        const onSourceData = (e: any) => {
            console.log("Source data event:", e)
            if (e.sourceId === sourceId && map.getSource(sourceId)) {
                map.off("sourcedata", onSourceData)
                resolve(map.getSource(sourceId) as GeoJSONSource)
            }
        }
        map.on("sourcedata", onSourceData)
    })
}
