<script setup lang="ts">
import { SCORE_COLOR_STOPS } from "~/utils/scoreColor"

const gradient = `linear-gradient(to right, ${SCORE_COLOR_STOPS.map(
    ([stop, color]) => `${color} ${stop}%`,
).join(", ")})`
const items = [
    [
        {
            label: "Przedszkole",
            icon: "i-mdi-teddy-bear",
        },
        {
            label: "Szkoła podstawowa",
            icon: "i-mdi-book-open-page-variant",
        },
        {
            label: "Liceum ogólnokształcące",
            icon: "i-mdi-school",
        },
        {
            label: "Technikum",
            icon: "i-mdi-cog",
        },
        {
            label: "Inne",
            icon: "i-mdi-star",
        },
    ],
]
</script>

<template>
    <div class="absolute bottom-6 left-4 z-10 flex flex-col items-start gap-2">
        <!-- School Type Dropdown Legend -->
        <UDropdownMenu
            :items="items"
            :content="{ side: 'top', align: 'start' }"
            :ui="{ content: 'w-64' }">
            <UButton
                label="Legenda"
                color="neutral"
                variant="outline"
                icon="i-heroicons-map"
                trailing-icon="i-heroicons-chevron-up"
                size="md" />

            <template #item="{ item }">
                <div class="flex items-center gap-3 py-1">
                    <UIcon :name="item.icon" class="h-6 w-6 text-secondary" />
                    <span class="text-sm font-medium text-default">
                        {{ item.label }}
                    </span>
                </div>
            </template>
        </UDropdownMenu>

        <!-- Score Gradient Legend -->
        <div
            class="inline-flex overflow-hidden rounded-md border border-default bg-default shadow-sm">
            <span
                class="min-w-9 px-2 py-1 text-center text-xs font-semibold leading-5 text-default">
                0
            </span>

            <div
                class="relative h-7 w-36 border-x border-default"
                :style="{ background: gradient }"></div>

            <span
                class="min-w-9 px-2 py-1 text-center text-xs font-semibold leading-5 text-default">
                100
            </span>
        </div>
    </div>
</template>
