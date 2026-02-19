import type { SzkolaPublicShortWithMiejscowosc } from "~/types/schools"

export type SchoolSearchSuggestion = {
    kind: "school"
    key: string
    school: SzkolaPublicShortWithMiejscowosc
}

export type PhotonSearchSuggestion = {
    kind: "photon"
    key: string
    label: string
    subtitle: string
    coordinates: [number, number]
}

export type MapSearchSuggestion =
    | SchoolSearchSuggestion
    | PhotonSearchSuggestion
