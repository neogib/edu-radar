import type { BoundingBox } from "~/types/boundingBox"
import teddyBearIconUrl from "~/assets/images/figures/sdf/teddy-bear.png"
import backpackIconUrl from "~/assets/images/figures/sdf/backpack.png"
import bookIconUrl from "~/assets/images/figures/sdf/book.png"
import gearIconUrl from "~/assets/images/figures/sdf/gear.png"
import schoolIconUrl from "~/assets/images/figures/sdf/school.png"

// constants/mapConfig.ts
export const MAP_CONFIG = {
    style: "/map-styles/style-pl.json",
    polandBounds: [14, 48.95, 24.2, 55] as [number, number, number, number],
    polandCenter: [19.355417, 52.191111] as [number, number],
    defaultBbox: {
        minLng: 20.7639,
        minLat: 52.1189,
        maxLng: 21.3901,
        maxLat: 52.3473,
    } as BoundingBox,
    defaultCenter: [21.008333, 52.232222] as [number, number],
    defaultZoom: 12,
    voivodeshipZoom: 10,
    maxZoom: 19,
    minZoom: 5,
    zoomThreshold: 8,
    mapKey: "mainMap",
    sourceId: "schools",
}

export const SCHOOL_ICONS = {
    Przedszkole: "teddyBear",
    "Szkoła podstawowa": "backpack",
    "Liceum ogólnokształcące": "book",
    Technikum: "gear",
    default: "schoolSymbol",
} as const

export const ICONS = {
    teddyBear: teddyBearIconUrl,
    backpack: backpackIconUrl,
    book: bookIconUrl,
    gear: gearIconUrl,
    schoolSymbol: schoolIconUrl,
} as const
