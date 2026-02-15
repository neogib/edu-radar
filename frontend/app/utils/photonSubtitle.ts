import type { PhotonFeatureProperties } from "~/types/photon"

export const buildPhotonSubtitle = (properties: PhotonFeatureProperties) => {
    const locationText = [
        properties.city,
        properties.district,
        properties.county,
        properties.state,
        properties.country,
    ]
        .filter(Boolean)
        .join(", ")

    if (locationText.length > 0) {
        return locationText
    }

    return (
        [properties.street, properties.housenumber, properties.postcode]
            .filter(Boolean)
            .join(" ")
            .trim() ||
        properties.osm_value ||
        "Lokalizacja"
    )
}
