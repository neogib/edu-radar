<script setup lang="ts">
import { VOIVODESHIPS_PATHS } from "~/constants/voivodeships"

const emit = defineEmits<{
    (e: "redirectToMap", voivodeshipId: string): void
}>()

// Define a function to handle clicks on the path elements of the SVG map
// emit event to parent component when a voivodeship is selected
function handlePathClick(event: Event) {
    const target = event.target as SVGPathElement
    const pathId = target.id // Extract the `id` of the clicked path element

    emit("redirectToMap", pathId)
}
</script>

<template>
    <div
        class="map-container flex justify-center h-auto w-full max-w-5xl mx-auto md:p-6">
        <svg
            id="svg2"
            viewBox="0 0 500 500"
            xmlns:svg="http://www.w3.org/2000/svg"
            xmlns="http://www.w3.org/2000/svg"
            version="1.0">
            <defs id="defs5" />
            <path
                v-for="path in VOIVODESHIPS_PATHS"
                :id="path.id"
                :key="path.id"
                :d="path.d"
                class="voivodeship"
                tabindex="0"
                @click="handlePathClick"
                @keydown.enter.space.prevent="handlePathClick" />
        </svg>
    </div>
</template>

<style scoped>
@reference "tailwindcss";

.voivodeship {
    @apply cursor-pointer transition duration-300 ease-in-out stroke-2 origin-center hover:scale-[1.03] active:scale-[1.03];
    transform-box: fill-box;
    fill: var(--voivodeship-fill);
    stroke: var(--voivodeship-stroke-muted);
    filter: drop-shadow(0 0 0 var(--voivodeship-shadow-hover));
}

.voivodeship:hover {
    fill: var(--voivodeship-fill-hover);
    stroke: var(--voivodeship-stroke);
    filter: drop-shadow(0 0 12px var(--voivodeship-shadow-hover));
}

.voivodeship:active,
.voivodeship:focus-visible {
    fill: var(--voivodeship-fill-active);
    stroke: var(--voivodeship-stroke);
    filter: drop-shadow(0 0 17px var(--voivodeship-shadow-hover));
}
</style>
