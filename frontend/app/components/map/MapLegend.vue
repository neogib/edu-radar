<script setup lang="ts">
const items = [
    [
        {
            label: "Przedszkole",
            icon: "i-mdi-triangle",
            color: "text-orange-500",
        },
        {
            label: "Szkoła podstawowa",
            icon: "i-mdi-square",
            color: "text-blue-500",
        },
        {
            label: "Liceum ogólnokształcące",
            icon: "i-carbon-diamond-solid",
            color: "text-purple-500",
        },
        {
            label: "Technikum",
            icon: "i-mdi-hexagon",
            color: "text-pink-500",
        },
        {
            label: "Inne",
            icon: "i-mdi-star",
            color: "text-yellow-500",
        },
    ],
]
</script>

<template>
    <div class="absolute bottom-6 left-4 z-40">
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
                    <UIcon
                        :name="item.icon"
                        class="h-6 w-6"
                        :class="item.color" />
                    <span
                        class="text-sm font-medium text-gray-700 dark:text-gray-200">
                        {{ item.label }}
                    </span>
                </div>
            </template>
        </UDropdownMenu>
    </div>
</template>
