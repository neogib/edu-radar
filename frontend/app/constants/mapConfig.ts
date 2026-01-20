import triangleIconUrl from "~/assets/images/figures/triangle.png"
import diamondIconUrl from "~/assets/images/figures/diamond.png"
import squareIconUrl from "~/assets/images/figures/square.png"
import starIconUrl from "~/assets/images/figures/star.png"
import hexagonIconUrl from "~/assets/images/figures/hexagon.png"

// constants/mapConfig.ts
export const MAP_CONFIG = {
    style: "https://tiles.openfreemap.org/styles/liberty",
    polandBounds: [14, 48.95, 24.2, 55] as [number, number, number, number],
    polandCenter: [19.355417, 52.191111] as [number, number],
    defaultBbox: {
        minLon: 20.7639,
        minLat: 52.1189,
        maxLon: 21.3901,
        maxLat: 52.3473,
    },
    defaultCenter: [21.008333, 52.232222] as [number, number],
    defaultZoom: 12,
    maxZoom: 19,
    minZoom: 5,
}

export const SCHOOL_ICONS = {
    Technikum: "hexagon_sdf",
    "Liceum ogólnokształcące": "diamond_sdf",
    "Szkoła podstawowa": "square_sdf",
    Przedszkole: "triangle_sdf",
    default: "star_sdf",
}

export const ICON_URLS = [
    triangleIconUrl,
    diamondIconUrl,
    squareIconUrl,
    starIconUrl,
    hexagonIconUrl,
]
