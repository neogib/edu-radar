<script setup lang="ts">
import { useMap } from "@indoorequal/vue-maplibre-gl"
import type {
    LayerSpecification,
    MapSourceDataEvent,
    StyleSpecification,
} from "maplibre-gl"
import { MAP_CONFIG, ICONS } from "~/constants/mapConfig"
import type { SzkolaPublicWithRelations } from "~/types/schools"

useHistoryState()
const route = useRoute()
const colorMode = useColorMode()
const [x, y, z] = [
    Number(route.query.x),
    Number(route.query.y),
    Number(route.query.z),
]
const emit = defineEmits<{
    "point-clicked": [school: SzkolaPublicWithRelations | null]
}>()

const popupCoordinates: Ref<[number, number] | undefined> = ref(undefined)
const { setupMapEventHandlers, hoveredSchool } = useMapInteractions(
    emit,
    popupCoordinates,
)
const initialMapStyle =
    colorMode.value === "dark" ? MAP_CONFIG.darkStyle : MAP_CONFIG.lightStyle
const mapInstance = useMap(MAP_CONFIG.mapKey)

const statusIcon = computed(() => {
    if (!hoveredSchool.value) return "i-mdi-shield-check"
    if (hoveredSchool.value.status === "publiczna") return "i-mdi-earth"
    if (hoveredSchool.value.status === "niepubliczna")
        return "i-material-symbols-public-off"
    return "i-mdi-shield-check"
})

const isSchoolLayer = (layer: LayerSpecification): boolean =>
    "source" in layer &&
    typeof layer.source === "string" &&
    layer.source === MAP_CONFIG.sourceId

const getMergedStyle = (
    previousStyle: StyleSpecification | undefined,
    nextStyle: StyleSpecification,
): StyleSpecification => {
    if (!previousStyle) {
        return nextStyle
    }

    const schoolsSource = previousStyle.sources?.[MAP_CONFIG.sourceId]
    if (!schoolsSource) {
        return nextStyle
    }

    const existingLayerIds = new Set(nextStyle.layers.map((layer) => layer.id))
    const schoolLayers = previousStyle.layers.filter(
        (layer): layer is LayerSpecification =>
            isSchoolLayer(layer) && !existingLayerIds.has(layer.id),
    )

    // Render school layers on top of basemap labels so names do not overlap clusters.
    const insertIndex = nextStyle.layers.length

    return {
        ...nextStyle,
        sources: {
            ...nextStyle.sources,
            [MAP_CONFIG.sourceId]: schoolsSource,
        },
        layers: [
            ...nextStyle.layers.slice(0, insertIndex),
            ...schoolLayers,
            ...nextStyle.layers.slice(insertIndex),
        ],
    }
}

const isSchoolsSourceReady = (map: maplibregl.Map): boolean =>
    Boolean(
        map.getSource(MAP_CONFIG.sourceId) &&
        map.isSourceLoaded(MAP_CONFIG.sourceId),
    )

const waitForSchoolsSource = (map: maplibregl.Map): Promise<void> =>
    new Promise((resolve) => {
        if (isSchoolsSourceReady(map)) {
            resolve()
            return
        }

        const onSourceData = (e: MapSourceDataEvent) => {
            if (e.sourceId !== MAP_CONFIG.sourceId) return
            if (!e.isSourceLoaded) return

            map.off("sourcedata", onSourceData)
            resolve()
        }

        map.on("sourcedata", onSourceData)
    })

const registerStyleImageMissingHandler = (map: maplibregl.Map): void => {
    const pending = new Set<string>()

    map.on("styleimagemissing", async (e) => {
        if (!(e.id in ICONS)) return
        if (map.hasImage(e.id)) return
        if (pending.has(e.id)) return

        pending.add(e.id)
        try {
            const image = await map.loadImage(ICONS[e.id as keyof typeof ICONS])
            if (!map.hasImage(e.id)) {
                map.addImage(e.id, image.data, { sdf: true })
            }
        } finally {
            pending.delete(e.id)
        }
    })
}

const onMapLoaded = async (event: { map: maplibregl.Map }) => {
    const map = event.map
    setupMapEventHandlers(map)
    registerStyleImageMissingHandler(map)
    await waitForSchoolsSource(map)
}

watch(
    () => colorMode.value,
    (mode, previousMode) => {
        if (mode === previousMode) return
        if (!mapInstance.isLoaded) return

        const nextStyle =
            mode === "dark" ? MAP_CONFIG.darkStyle : MAP_CONFIG.lightStyle
        const map = mapInstance.map as maplibregl.Map

        map.setStyle(nextStyle, {
            diff: true,
            transformStyle: (previousStyle, nextStyleSpec) =>
                getMergedStyle(previousStyle, nextStyleSpec),
        })
    },
)
</script>

<template>
    <MglMap
        :map-key="MAP_CONFIG.mapKey"
        :map-style="initialMapStyle"
        :center="[x, y]"
        :zoom="z"
        :fade-duration="0"
        :min-zoom="MAP_CONFIG.minZoom"
        :max-zoom="MAP_CONFIG.maxZoom"
        @map:load="onMapLoaded">
        <MglNavigationControl position="bottom-right" />
        <MglFullscreenControl position="bottom-right" />
        <MglGeolocateControl
            position="bottom-right"
            :position-options="{ enableHighAccuracy: true }"
            :track-user-location="true" />

        <MglImage
            v-for="(url, id) in ICONS"
            :id="id"
            :key="id"
            :url="url"
            :options="{ sdf: true }" />

        <MglPopup
            v-if="hoveredSchool"
            :close-button="false"
            :close-on-click="false"
            :offset="20"
            :coordinates="popupCoordinates">
            <div
                class="min-w-55 max-w-70 overflow-hidden rounded-xl border border-default bg-default shadow-2xl">
                <!-- Status -->
                <div
                    class="bg-linear-to-r from-blue-500 to-indigo-600 dark:from-blue-600 dark:to-violet-700 px-2 py-1.5">
                    <div class="flex items-center gap-2">
                        <UIcon
                            :name="statusIcon"
                            class="text-white text-lg shrink-0" />
                        <span class="text-xs text-white font-medium">
                            {{ hoveredSchool.status }}
                        </span>
                    </div>
                </div>

                <!-- School Name -->
                <div class="bg-default px-2 py-2">
                    <h4 class="font-semibold text-highlighted text-xs">
                        {{ hoveredSchool.nazwa }}
                    </h4>
                </div>

                <!-- School Type -->
                <div
                    class="bg-muted px-2 py-1.5 border-t border-default dark:bg-elevated">
                    <div class="flex items-center gap-2">
                        <UIcon
                            name="i-mdi-school"
                            class="text-muted text-lg shrink-0" />
                        <span class="text-xs text-default font-medium">
                            {{ hoveredSchool.typ }}
                        </span>
                    </div>
                </div>
            </div>
        </MglPopup>

        <MapSchoolLayers />
    </MglMap>
</template>
