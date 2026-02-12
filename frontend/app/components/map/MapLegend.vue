<script setup lang="ts">
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
    <div class="absolute bottom-6 left-4 z-10">
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
                    <span
                        class="text-sm font-medium text-gray-700 dark:text-gray-200">
                        {{ item.label }}
                    </span>
                </div>
            </template>
        </UDropdownMenu>
    </div>
</template>
