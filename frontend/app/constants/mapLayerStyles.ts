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
            NULL_SCORE_COLOR,
            createScoreColorInterpolation(["get", "wynik"]),
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
    layout: {
        "text-field":
            "{point_count_abbreviated}" as PropertyValueSpecification<string>,
        "text-font": ["Noto Sans Regular"] as PropertyValueSpecification<
            string[]
        >,
        "text-size": 12 as PropertyValueSpecification<number>,
    },
}
