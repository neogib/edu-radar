import triangleIconUrl from "~/assets/images/figures/triangle.png"
import diamondIconUrl from "~/assets/images/figures/diamond.png"
import squareIconUrl from "~/assets/images/figures/square.png"
import starIconUrl from "~/assets/images/figures/star.png"
import hexagonIconUrl from "~/assets/images/figures/hexagon.png"
import type { BoundingBox } from "~/types/boundingBox"

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
    Technikum: "hexagon_sdf",
    "Liceum ogólnokształcące": "diamond_sdf",
    "Szkoła podstawowa": "square_sdf",
    Przedszkole: "triangle_sdf",
    default: "star_sdf",
} as const

export const ICONS = {
    triangle_sdf: triangleIconUrl,
    diamond_sdf: diamondIconUrl,
    square_sdf: squareIconUrl,
    star_sdf: starIconUrl,
    hexagon_sdf: hexagonIconUrl,
} as const
