import { SCHOOL_ICONS } from "./mapConfig"
import type {
    DataDrivenPropertyValueSpecification,
    PropertyValueSpecification,
} from "maplibre-gl"

export const POINT_LAYER_STYLE = {
    paint: {
        "icon-opacity": 0.75,
        "icon-halo-color": "#000000", // black border
        "icon-halo-width": 1, // szerokość w px
        "icon-color": [
            "case",
            ["==", ["get", "score"], null],
            "#87CEFA", // blue for null scores
            [
                "interpolate",
                ["linear"],
                ["get", "score"],
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
        "icon-image": [
            "case",
            ["==", ["get", "typ"], "Technikum"],
            SCHOOL_ICONS.Technikum,
            ["==", ["get", "typ"], "Liceum ogólnokształcące"],
            SCHOOL_ICONS["Liceum ogólnokształcące"],
            ["==", ["get", "typ"], "Szkoła podstawowa"],
            SCHOOL_ICONS["Szkoła podstawowa"],
            ["==", ["get", "typ"], "Przedszkole"],
            SCHOOL_ICONS["Przedszkole"],
            // Default fallback for any other school types
            SCHOOL_ICONS.default,
        ] as DataDrivenPropertyValueSpecification<string>,
        "icon-allow-overlap": true,
    },
}

export const CLUSTER_LAYER_STYLE = {
    paint: {
        "circle-opacity": 0.75,
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
            "step",
            ["get", "point_count"],
            20,
            100,
            30,
            750,
            40,
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
