export type PhotonFeatureProperties = {
    name?: string
    city?: string
    state?: string
    country?: string
    district?: string
    county?: string
    street?: string
    housenumber?: string
    postcode?: string
    osm_value?: string
}

export type PhotonFeatureCollection = GeoJSON.FeatureCollection<
    GeoJSON.Point,
    PhotonFeatureProperties
>
