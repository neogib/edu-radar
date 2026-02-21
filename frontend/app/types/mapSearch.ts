import type { SzkolaPublicShort } from "~/types/schools"

export type SchoolSearchSuggestion = {
    kind: "school"
    key: string
    school: SzkolaPublicShort
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
