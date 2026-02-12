<script setup lang="ts">
import { MAP_CONFIG } from "~/constants/mapConfig"
import { mainSchoolTypes } from "~/constants/schoolTypes"
import { VOIVODESHIP_NAMES } from "~/constants/voivodeships"
import type { TypSzkolyPublic } from "~/types/schools"

const initialBbox = useInitialBbox()
const { data: schoolTypes } = await useApi<TypSzkolyPublic[]>(
    "/school_types/",
    {
        query: { names: mainSchoolTypes },
    },
)

const getDefaultSchoolTypes = (types: TypSzkolyPublic[]) => {
    return types
        .filter((t: TypSzkolyPublic) =>
            [
                "Szkoła podstawowa",
                "Technikum",
                "Liceum ogólnokształcące",
            ].includes(t.nazwa),
        )
        .map((t: TypSzkolyPublic) => t.id)
}

const selectedSchoolTypes = ref<number[]>(
    schoolTypes.value ? getDefaultSchoolTypes(schoolTypes.value) : [],
)

const handleSubmit = async (selectedVoivodeship: string) => {
    const voivodeshipData = VOIVODESHIP_NAMES[selectedVoivodeship]

    if (!voivodeshipData) {
        console.error("Voivodeship not found:", selectedVoivodeship)
        return
    }

    initialBbox.value = voivodeshipData.coordinates

    // Default school types if none selected
    let types = selectedSchoolTypes.value
    if (types.length === 0 && schoolTypes.value) {
        types = getDefaultSchoolTypes(schoolTypes.value as TypSzkolyPublic[])
    }
    await navigateTo({
        path: "/map",
        query: {
            x: voivodeshipData.center[0],
            y: voivodeshipData.center[1],
            z: MAP_CONFIG.voivodeshipZoom,
            type: types,
        },
    })
}

const hydrated = ref(false)
onMounted(() => {
    hydrated.value = true
})
</script>

<template>
    <div class="grid lg:grid-cols-12 gap-6 items-start">
        <!-- Sidebar: Filters (Takes 4 cols) -->
        <div
            class="lg:col-span-4 rounded-xl border border-default bg-muted shadow-sm p-6">
            <h2 class="font-bold text-xl text-highlighted mb-1">
                Rodzaj szkoły
            </h2>
            <p class="text-sm text-muted mb-5">
                Zaznacz interesujące Cię rodzaje szkół
            </p>

            <div class="flex flex-col gap-3">
                <div v-if="schoolTypes == undefined" class="text-muted">
                    Ładowanie...
                </div>

                <label
                    v-for="type in schoolTypes as TypSzkolyPublic[]"
                    v-else
                    :key="type.id"
                    class="flex items-center p-3 border border-default rounded-lg cursor-pointer transition-colors hover:bg-accented has-checked:border-primary has-checked:bg-primary/15">
                    <!-- Native checkbox with accent color saves tons of CSS -->
                    <input
                        v-model="selectedSchoolTypes"
                        type="checkbox"
                        :value="type.id"
                        :disabled="!hydrated"
                        class="w-5 h-5 accent-primary rounded" />
                    <span class="ml-3 font-medium text-default">{{
                        type.nazwa
                    }}</span>
                </label>
            </div>
            <p class="mt-4 text-xs text-dimmed">
                * Domyślnie: Szkoła podstawowa, Technikum, Liceum
            </p>
        </div>

        <!-- Main: Map (Takes 8 cols) -->
        <div
            class="lg:col-span-8 rounded-xl border border-default bg-muted shadow-sm p-2 md:p-6">
            <h2
                class="font-bold text-xl text-highlighted pl-2 pt-2 md:p-0 md:mb-2">
                Mapa województw
            </h2>
            <p class="text-sm text-toned pl-2 mb-2 md:pl-0 md:mb-4">
                Kliknij województwo, aby przejść na mapę
            </p>
            <VoivodeshipsMap @redirect-to-map="handleSubmit" />
        </div>
    </div>
</template>
