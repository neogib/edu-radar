<script setup lang="ts">
import { mainSchoolTypes } from "~/constants/schoolTypes"
import { VOIVODESHIP_NAMES } from "~/constants/voivodeships"
import type { TypSzkolyPublic } from "~/types/schools"

const voivodeships_map = ref<HTMLElement | null>(null)
const selectedVoivodeship = ref<string>("")

const selectedSchoolTypes = ref<number[]>([])

const { data: schoolTypes } = useApi<TypSzkolyPublic[]>("/school_types/", {
    query: { names: mainSchoolTypes },
})

const handleSubmit = async () => {
    console.log(`Selected schoolTypes: ${selectedSchoolTypes.value}`)
    const voivodeshipData = VOIVODESHIP_NAMES[selectedVoivodeship.value]
    if (!voivodeshipData) {
        console.error("Voivodeship not found:", selectedVoivodeship.value)
        return
    }

    const coordinates = voivodeshipData.coordinates
    const bbox = `${coordinates.minLon},${coordinates.minLat},${coordinates.maxLon},${coordinates.maxLat}`

    await navigateTo({
        path: "/map",
        query: {
            bbox: bbox,
            type: selectedSchoolTypes.value,
        },
    })
}

const resetForm = () => {
    selectedSchoolTypes.value = []
    selectedVoivodeship.value = ""
}
</script>

<template>
    <div class="grid lg:grid-cols-2 gap-12 items-start">
        <div class="content-card">
            <div class="mb-8">
                <h2 class="text-2xl font-bold text-gray-900 mb-2">
                    Wybierz parametry wyszukiwania
                </h2>
                <p class="text-gray-600">
                    Zacznij od wyboru typu szkoły i województwa na mapie
                </p>
            </div>

            <form class="space-y-4" @submit.prevent="handleSubmit">
                <!-- School Type Selection -->
                <div>
                    <label
                        for="school-type"
                        class="block text-sm font-medium text-gray-700 mb-3">
                        Typ szkoły *
                    </label>
                    <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
                        <div v-if="schoolTypes === undefined">
                            Ładowanie typów szkół...
                        </div>
                        <div
                            v-else
                            v-for="schoolType in schoolTypes as TypSzkolyPublic[]"
                            :key="schoolType.id"
                            class="relative">
                            <input
                                :id="schoolType.id.toString()"
                                v-model="selectedSchoolTypes"
                                :value="schoolType.id"
                                type="checkbox"
                                name="school-type"
                                class="peer sr-only" />
                            <label
                                :for="schoolType.id.toString()"
                                class="block w-full p-4 text-center border-2 border-gray-200 rounded-lg cursor-pointer hover:border-indigo-300 peer-checked:border-indigo-500 peer-checked:bg-indigo-50 peer-checked:text-indigo-700 transition-all duration-200">
                                <span class="font-medium">{{
                                    schoolType.nazwa
                                }}</span>
                            </label>
                        </div>
                    </div>
                </div>

                <!-- Selected Voivodeship Display -->
                <div>
                    <label class="block text-sm font-medium text-gray-700 mb-3">
                        Wybrane województwo *
                    </label>
                    <div
                        class="bg-gray-50 rounded-lg border-2 border-dashed border-gray-300">
                        <div
                            v-if="selectedVoivodeship"
                            class="flex justify-between p-3">
                            <span class="text-lg font-medium text-indigo-600">
                                {{
                                    VOIVODESHIP_NAMES[selectedVoivodeship]?.name
                                }}
                            </span>
                            <button
                                type="button"
                                class="text-red-500 hover:text-red-700 transition-colors"
                                @click="selectedVoivodeship = ''">
                                <Icon name="mdi:close" class="w-6 h-6" />
                            </button>
                        </div>
                        <UButton
                            v-else
                            block
                            class="p-4"
                            variant="soft"
                            color="neutral"
                            icon="i-heroicons-map"
                            @click="
                                voivodeships_map?.scrollIntoView({
                                    behavior: 'smooth',
                                    block: 'center',
                                })
                            ">
                            Wybierz na mapie →
                        </UButton>
                    </div>
                </div>

                <!-- Action Buttons -->
                <div class="flex flex-col sm:flex-row gap-4 pt-2">
                    <button
                        type="submit"
                        :disabled="
                            !selectedSchoolTypes.length || !selectedVoivodeship
                        "
                        class="form-button bg-indigo-600 text-white hover:bg-indigo-700 disabled:bg-gray-300 disabled:cursor-not-allowed duration-200 hover:scale-105 active:scale-95">
                        Szukaj szkół
                    </button>
                    <button
                        type="button"
                        class="form-button text-gray-700 hover:bg-gray-50"
                        @click="resetForm">
                        Wyczyść
                    </button>
                </div>
            </form>
        </div>
        <!-- Map Section -->
        <div ref="voivodeships_map" class="content-card">
            <div class="mb-2">
                <h2 class="text-2xl font-bold text-gray-900 mb-2">
                    Mapa województw
                </h2>
                <p class="text-gray-600">
                    Kliknij na województwo, aby je wybrać
                </p>
            </div>

            <div class="relative">
                <VoivodeshipsMap v-model="selectedVoivodeship" />

                <!-- Map overlay for selected voivodeship -->
                <div
                    v-if="selectedVoivodeship"
                    class="absolute top-0 right-0 bg-indigo-100 text-indigo-800 px-3 py-2 rounded-lg text-sm border border-indigo-200">
                    <p>
                        Wybrano:
                        {{ VOIVODESHIP_NAMES[selectedVoivodeship]?.name }}
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
@reference "tailwindcss";

.form-button {
    @apply px-6 py-3 border border-gray-300  rounded-lg font-medium focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:ring-offset-2 transition-all duration-200;
}
</style>
