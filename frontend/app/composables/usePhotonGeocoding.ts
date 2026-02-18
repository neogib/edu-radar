import { useMap } from "@indoorequal/vue-maplibre-gl"
import { MAP_CONFIG } from "~/constants/mapConfig"
import { PHOTON_CONFIG } from "~/constants/photon"
import type { PhotonFeatureCollection } from "~/types/photon"
import type { PhotonSearchSuggestion } from "~/types/mapSearch"

export const usePhotonGeocoding = () => {
    const mapInstance = useMap(MAP_CONFIG.mapKey)

    const fetchPhotonSuggestions = async (
        query: string,
    ): Promise<PhotonSearchSuggestion[]> => {
        const map = mapInstance.map as maplibregl.Map | undefined
        const center = map?.getCenter()
        const zoom = map?.getZoom()

        const params = new URLSearchParams({
            q: query,
            limit: String(PHOTON_CONFIG.resultsLimit),
            bbox: MAP_CONFIG.polandBounds.join(","),
        })

        if (center) {
            params.set("lat", String(center.lat))
            params.set("lon", String(center.lng))
            params.set(
                "zoom",
                String(Math.floor(zoom ?? PHOTON_CONFIG.fallbackZoom)),
            )
            params.set(
                "location_bias_scale",
                String(PHOTON_CONFIG.locationBiasScale),
            )
        }

        try {
            const data = await $fetch<PhotonFeatureCollection>(
                `${PHOTON_CONFIG.apiUrl}?${params.toString()}`,
            )

            return data.features
                .map((feature, index) => {
                    const coordinates = feature.geometry?.coordinates
                    if (
                        !Array.isArray(coordinates) ||
                        coordinates.length !== 2 ||
                        typeof coordinates[0] !== "number" ||
                        typeof coordinates[1] !== "number"
                    ) {
                        return null
                    }

                    const properties = feature.properties ?? {}
                    const label =
                        properties.name ||
                        properties.city ||
                        properties.street ||
                        "Nieznana lokalizacja"

                    return {
                        kind: "photon" as const,
                        key: `photon-${coordinates[0]}-${coordinates[1]}-${index}`,
                        label,
                        subtitle: buildPhotonSubtitle(properties),
                        coordinates: [coordinates[0], coordinates[1]] as [
                            number,
                            number,
                        ],
                    }
                })
                .filter((item): item is PhotonSearchSuggestion => item !== null)
        } catch (error) {
            console.error("Error fetching Photon suggestions", error)
            return []
        }
    }

    return { fetchPhotonSuggestions }
}
