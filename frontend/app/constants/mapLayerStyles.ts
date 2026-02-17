import { SCHOOL_ICONS } from "./mapConfig"
import type {
    DataDrivenPropertyValueSpecification,
    PropertyValueSpecification,
} from "maplibre-gl"

const ICON_IMAGES = [
    "case",
    ["==", ["get", "typ"], "Technikum"],
    SCHOOL_ICONS.Technikum,
    ["==", ["get", "typ"], "Liceum ogólnokształcące"],
    SCHOOL_ICONS["Liceum ogólnokształcące"],
    ["==", ["get", "typ"], "Szkoła podstawowa"],
    SCHOOL_ICONS["Szkoła podstawowa"],
    ["==", ["get", "typ"], "Przedszkole"],
    SCHOOL_ICONS["Przedszkole"],
    SCHOOL_ICONS.default,
] as DataDrivenPropertyValueSpecification<string>

const LIGHT_STROKE_HALO_COLOR = "#0f172a"
const DARK_STROKE_HALO_COLOR = "#f8fafc"

const getPointLayerPaint = (isDarkMode: boolean) => ({
    paint: {
        "icon-opacity": [
            "case",
            ["boolean", ["feature-state", "clicked"], false],
            1,
            0.7,
        ] as DataDrivenPropertyValueSpecification<number>,
        "icon-halo-color": (isDarkMode
            ? DARK_STROKE_HALO_COLOR
            : LIGHT_STROKE_HALO_COLOR) as PropertyValueSpecification<string>,
        "icon-halo-width": [
            "case",
            ["boolean", ["feature-state", "clicked"], false],
            2,
            1,
        ] as DataDrivenPropertyValueSpecification<number>,
        "icon-color": [
            "case",
            ["==", ["get", "wynik"], null],
            NULL_SCORE_COLOR,
            createScoreColorInterpolation(["get", "wynik"]),
        ] as DataDrivenPropertyValueSpecification<string>,
    },
})

const POINT_LAYER_LAYOUT = {
    "icon-size": 0.5,
    "icon-image": ICON_IMAGES,
    "icon-allow-overlap": true,
    "icon-ignore-placement": true,
}

const getClusterLayerPaint = (isDarkMode: boolean) => ({
    paint: {
        "circle-opacity": [
            "case",
            ["boolean", ["feature-state", "hover"], false],
            1,
            0.7,
        ] as DataDrivenPropertyValueSpecification<number>,
        "circle-stroke-width": 1,
        "circle-stroke-opacity": 0.75,
        "circle-stroke-color": (isDarkMode
            ? DARK_STROKE_HALO_COLOR
            : LIGHT_STROKE_HALO_COLOR) as PropertyValueSpecification<string>,
        "circle-color": [
            "case",
            ["==", ["get", "nonNullCount"], 0],
            NULL_SCORE_COLOR,
            createScoreColorInterpolation([
                "/",
                ["get", "sum"],
                ["get", "nonNullCount"],
            ]),
        ] as DataDrivenPropertyValueSpecification<string>,
        "circle-radius": [
            "case",
            ["boolean", ["feature-state", "hover"], false],
            ["*", ["step", ["get", "point_count"], 20, 100, 30, 750, 40], 1.1],
            ["step", ["get", "point_count"], 20, 100, 30, 750, 40],
        ] as DataDrivenPropertyValueSpecification<number>,
    },
})

const CLUSTER_LAYER_LAYOUT = {
    "text-field":
        "{point_count_abbreviated}" as PropertyValueSpecification<string>,
    "text-font": ["Noto Sans Regular"] as PropertyValueSpecification<string[]>,
    "text-size": 12 as PropertyValueSpecification<number>,
    "text-allow-overlap": true,
    "text-ignore-placement": true,
}

export const getPointLayerStyle = (isDarkMode: boolean) => ({
    paint: getPointLayerPaint(isDarkMode).paint,
    layout: POINT_LAYER_LAYOUT,
})

export const getClusterLayerStyle = (isDarkMode: boolean) => ({
    paint: getClusterLayerPaint(isDarkMode).paint,
    layout: CLUSTER_LAYER_LAYOUT,
})
