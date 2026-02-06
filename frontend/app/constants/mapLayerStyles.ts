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

export const POINT_LAYER_STYLE = {
    paint: {
        "icon-opacity": [
            "case",
            ["boolean", ["feature-state", "clicked"], false],
            1,
            0.7,
        ] as DataDrivenPropertyValueSpecification<number>,
        "icon-halo-color": "#000000",
        "icon-halo-width": [
            "case",
            ["boolean", ["feature-state", "clicked"], false],
            2,
            0.5,
        ] as DataDrivenPropertyValueSpecification<number>,
        "icon-color": [
            "case",
            ["==", ["get", "wynik"], null],
            "#87CEFA", // blue for null scores
            [
                "interpolate",
                ["linear"],
                ["get", "wynik"],
                0,
                "#FF0000",
                50,
                "#FFFF00",
                100,
                "#00FF00",
            ],
        ] as DataDrivenPropertyValueSpecification<string>,
    },
    layout: {
        "icon-size": 0.5,
        "icon-image": ICON_IMAGES,
        "icon-allow-overlap": true,
    },
}

export const CLUSTER_LAYER_STYLE = {
    paint: {
        "circle-opacity": [
            "case",
            ["boolean", ["feature-state", "hover"], false],
            1,
            0.7,
        ] as DataDrivenPropertyValueSpecification<number>,
        "circle-stroke-width": 1,
        "circle-stroke-opacity": 0.75,
        "circle-color": [
            "case",
            ["==", ["get", "nonNullCount"], 0],
            "#87CEFA", // blue for null scores
            [
                "interpolate",
                ["linear"],
                ["/", ["get", "sum"], ["get", "nonNullCount"]],
                0,
                "#FF0000", // red at 0
                50,
                "#FFFF00", // yellow at 50
                100,
                "#00FF00", // green at 100
            ],
        ] as DataDrivenPropertyValueSpecification<string>,
        "circle-radius": [
            "case",
            ["boolean", ["feature-state", "hover"], false],
            ["*", ["step", ["get", "point_count"], 20, 100, 30, 750, 40], 1.1],
            ["step", ["get", "point_count"], 20, 100, 30, 750, 40],
        ] as DataDrivenPropertyValueSpecification<number>,
    },
    layout: {
        "text-field":
            "{point_count_abbreviated}" as PropertyValueSpecification<string>,
        "text-font": ["Noto Sans Regular"] as PropertyValueSpecification<
            string[]
        >,
        "text-size": 12 as PropertyValueSpecification<number>,
    },
}
