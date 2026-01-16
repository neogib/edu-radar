<script setup lang="ts">
import { ref } from "vue"
import { VOIVODESHIPS_PATHS } from "~/constants/voivodeships"

const emit = defineEmits(["path-click"])

const selectedVoivodeship = ref<string | null>(null)

// Define a function to handle clicks on the path elements
function handlePathClick(event: MouseEvent) {
    const target = event.target as SVGPathElement
    const pathId = target.id // Extract the `id` of the clicked path element

    // Toggle selection: deselect if clicking the same one
    selectedVoivodeship.value =
        selectedVoivodeship.value === pathId ? null : pathId

    // Emit the 'path-click' event with the path ID
    emit("path-click", pathId)
}
</script>

<template>
    <div class="flex justify-center h-auto w-full max-w-5xl mx-auto md:p-6">
        <svg
            id="svg2"
            viewBox="0 0 500 500"
            xmlns:svg="http://www.w3.org/2000/svg"
            xmlns="http://www.w3.org/2000/svg"
            version="1.0">
            <defs id="defs5" />
            <path
                v-for="path in VOIVODESHIPS_PATHS"
                :key="path.id"
                :id="path.id"
                :d="path.d"
                :class="[
                    'voivodeship',
                    { active: selectedVoivodeship === path.id },
                ]"
                @click="handlePathClick" />
        </svg>
    </div>
</template>

<style scoped>
@reference "tailwindcss";

.voivodeship {
    @apply cursor-pointer fill-[#94add6] hover:fill-[#5c7caa] hover:drop-shadow-xl hover:stroke-amber-300 hover:scale-[1.03] transition duration-300 ease-in-out stroke-2 stroke-transparent origin-center;
    transform-box: fill-box;
}

.voivodeship.active {
    @apply fill-[#3b4a76]  drop-shadow-xl;
}
</style>
