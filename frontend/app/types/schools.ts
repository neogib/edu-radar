/**
 * TypeScript types for school-related data models
 * These types correspond to the backend Python models in app.models.schools
 * Types were generated using a openapi-typescript generator
 */
import type { components, paths } from "./api"

type schemas = components["schemas"]

export type SzkolaPublicShort = schemas["SzkolaPublicShort"]
export type SzkolaPublicWithRelations = schemas["SzkolaPublicWithRelations"]
export type TypSzkolyPublic = schemas["TypSzkolyPublic"]
export type StatusPublicznoprawnyPublic = schemas["StatusPublicznoprawnyPublic"]
export type KategoriaUczniowPublic = schemas["KategoriaUczniowPublic"]
export type KsztalcenieZawodowePublic = schemas["KsztalcenieZawodowePublic"]

export type WynikE8PublicWithPrzedmiot = schemas["WynikE8PublicWithPrzedmiot"]
export type WynikEMPublicWithPrzedmiot = schemas["WynikEMPublicWithPrzedmiot"]

export type FiltersResponse = schemas["FiltersResponse"]
export type FiltersOptions =
    | TypSzkolyPublic[]
    | KategoriaUczniowPublic[]
    | StatusPublicznoprawnyPublic[]
    | KsztalcenieZawodowePublic[]

export type SchoolFilterParams =
    paths["/schools/"]["get"]["parameters"]["query"]

export type SchoolFeatureProperties = {
    id: number
    nazwa: string
    typ: string
    status: string
    wynik: number | null
}
export type SchoolFeature = GeoJSON.Feature<
    GeoJSON.Point,
    SchoolFeatureProperties
>
export type WynikPublicWithPrzedmiot =
    | WynikE8PublicWithPrzedmiot
    | WynikEMPublicWithPrzedmiot
