// Voivodeships mapping file
// Export a constant containing mappings of voivodeship keys to their respective names and bounding boxes
// later on we can use nominatim API from openstreetmap to get this data

import type { VoivodeshipData } from "~/types/voivodeships"

/**
 * Mapping of voivodeship keys to their respective data including Polish names and bounding boxes
 * Bounding boxes are in bbox format (min_lng, min_lat, max_lng, max_lat) and are approximate extents
 */
export const VOIVODESHIP_NAMES: Record<string, VoivodeshipData> = {
    dolnoslaskie: {
        name: "Dolnośląskie",
        coordinates: {
            minLon: 14.76,
            minLat: 49.98,
            maxLon: 17.91,
            maxLat: 51.91,
        },
    },
    kujawsko_pomorskie: {
        name: "Kujawsko-pomorskie",
        coordinates: {
            minLon: 17.16,
            minLat: 52.28,
            maxLon: 19.88,
            maxLat: 53.83,
        },
    },
    lubelskie: {
        name: "Lubelskie",
        coordinates: {
            minLon: 21.52,
            minLat: 50.2,
            maxLon: 24.25,
            maxLat: 52.35,
        },
    },
    lubuskie: {
        name: "Lubuskie",
        coordinates: {
            minLon: 14.4,
            minLat: 51.33,
            maxLon: 16.6,
            maxLat: 53.18,
        },
    },
    lodzkie: {
        name: "Łódzkie",
        coordinates: {
            minLon: 17.95,
            minLat: 50.78,
            maxLon: 20.75,
            maxLat: 52.45,
        },
    },
    malopolskie: {
        name: "Małopolskie",
        coordinates: {
            minLon: 18.92,
            minLat: 49.07,
            maxLon: 21.55,
            maxLat: 50.59,
        },
    },
    mazowieckie: {
        name: "Mazowieckie",
        coordinates: {
            minLon: 19.15,
            minLat: 50.95,
            maxLon: 23.25,
            maxLat: 53.55,
        },
    },
    opolskie: {
        name: "Opolskie",
        coordinates: {
            minLon: 16.8461,
            minLat: 49.942,
            maxLon: 18.8073,
            maxLat: 51.2778,
        },
    },
    podkarpackie: {
        name: "Podkarpackie",
        coordinates: {
            minLon: 21.03,
            minLat: 48.95,
            maxLon: 23.66,
            maxLat: 50.9,
        },
    },
    podlaskie: {
        name: "Podlaskie",
        coordinates: {
            minLon: 21.45,
            minLat: 52.17,
            maxLon: 24.1,
            maxLat: 54.5,
        },
    },
    pomorskie: {
        name: "Pomorskie",
        coordinates: {
            minLon: 16.65,
            minLat: 53.4,
            maxLon: 19.75,
            maxLat: 54.92,
        },
    },
    slaskie: {
        name: "Śląskie",
        coordinates: {
            minLon: 17.8872,
            minLat: 49.2956,
            maxLon: 20.0559,
            maxLat: 51.1617,
        },
    },
    swietokrzyskie: {
        name: "Świętokrzyskie",
        coordinates: {
            minLon: 19.6,
            minLat: 50.1,
            maxLon: 22.0,
            maxLat: 51.4,
        },
    },
    "warminsko-mazurskie": {
        name: "Warmińsko-mazurskie",
        coordinates: {
            minLon: 19.05,
            minLat: 53.07,
            maxLon: 22.95,
            maxLat: 54.52,
        },
    },
    wielkopolskie: {
        name: "Wielkopolskie",
        coordinates: {
            minLon: 15.68,
            minLat: 51.05,
            maxLon: 19.19,
            maxLat: 53.7,
        },
    },
    "zachodnio-pomorskie": {
        name: "Zachodniopomorskie",
        coordinates: {
            minLon: 13.95,
            minLat: 52.58,
            maxLon: 17.1,
            maxLat: 54.65,
        },
    },
}
