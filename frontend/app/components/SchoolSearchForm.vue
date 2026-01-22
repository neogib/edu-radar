<script setup lang="ts">
import { mainSchoolTypes } from "~/constants/schoolTypes"
import { VOIVODESHIP_NAMES } from "~/constants/voivodeships"
import type { TypSzkolyPublic } from "~/types/schools"

const mapIntent = useMapIntent()
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

    mapIntent.value = selectedVoivodeship

    // Default school types if none selected
    let types = selectedSchoolTypes.value
    if (types.length === 0 && schoolTypes.value) {
        types = getDefaultSchoolTypes(schoolTypes.value as TypSzkolyPublic[])
    }
    const coordinates = voivodeshipData.coordinates
    const bbox = `${coordinates.minLon},${coordinates.minLat},${coordinates.maxLon},${coordinates.maxLat}`

    await navigateTo({
        path: "/map",
        query: {
            bbox: bbox,
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
        <div class="lg:col-span-4 bg-white rounded-xl shadow-lg p-6">
            <h2 class="font-bold text-xl text-gray-900 mb-1">Rodzaj szkoły</h2>
            <p class="text-sm text-gray-500 mb-5">
                Zaznacz interesujące Cię typy
            </p>

            <div class="flex flex-col gap-3">
                <div v-if="schoolTypes == undefined" class="text-gray-500">
                    Ładowanie...
                </div>

                <label
                    v-else
                    v-for="type in schoolTypes as TypSzkolyPublic[]"
                    :key="type.id"
                    class="flex items-center p-3 border border-gray-200 rounded-lg cursor-pointer transition hover:bg-gray-50 has-checked:border-indigo-500 has-checked:bg-indigo-50">
                    <!-- Native checkbox with accent color saves tons of CSS -->
                    <input
                        type="checkbox"
                        :value="type.id"
                        :disabled="!hydrated"
                        v-model="selectedSchoolTypes"
                        class="w-5 h-5 accent-indigo-600 rounded" />
                    <span class="ml-3 font-medium text-gray-700">{{
                        type.nazwa
                    }}</span>
                </label>
            </div>
            <p class="mt-4 text-xs text-slate-400">
                * Domyślnie: Szkoła podstawowa, Technikum, Liceum
            </p>
        </div>

        <!-- Main: Map (Takes 8 cols) -->
        <div class="lg:col-span-8 bg-white rounded-xl shadow-lg p-2 md:p-6">
            <h2
                class="font-bold text-xl text-gray-900 pl-2 pt-2 md:p-0 md:mb-2">
                Mapa województw
            </h2>
            <p class="text-sm text-slate-500 pl-2 mb-2 md:pl-0 md:mb-4">
                Kliknij województwo, aby wybrać
            </p>
            <VoivodeshipsMap @redirectToMap="handleSubmit" />
        </div>
    </div>
</template>
