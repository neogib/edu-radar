<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui"

const route = useRoute()

// 'active' state automatically updates when the route changes
const items = computed<NavigationMenuItem[]>(() => [
    {
        label: "Mapa",
        to: "/map",
        icon: "i-mdi-map",
        active: route.path.startsWith("/map"),
    },
    {
        label: "O nas",
        to: "/",
        icon: "i-mdi-information",
        active: route.path.startsWith("/about"),
    },
    {
        label: "Kontakt",
        to: "/",
        icon: "i-mdi-phone", // Or 'i-mdi-email' depending on preference
        active: route.path.startsWith("/contact"),
    },
])
</script>

<template>
    <UHeader
        :toggle="{
            color: 'primary',
            class: 'rounded-full',
        }"
        :ui="{
            root: 'backdrop-blur-[2px]',
        }"
        mode="slideover">
        <template #title>
            <h1 class="text-2xl font-bold group">
                <span
                    class="text-gray-800 group-hover:text-indigo-600 transition-colors duration-200"
                    >Ranking</span
                >
                <span
                    class="text-indigo-600 group-hover:text-indigo-900 transition-colors duration-200"
                    >Szkół</span
                >
            </h1>
        </template>

        <template #right>
            <UNavigationMenu :items="items" class="hidden lg:flex" />
        </template>

        <template #body>
            <UNavigationMenu
                :items="items"
                orientation="vertical"
                class="-mx-2.5"
                :ui="{
                    link: 'px-3 py-2.5 text-base', // Bigger padding and font size for main items
                    linkLeadingIcon: 'size-6', // Bigger icon
                }" />
        </template>
    </UHeader>
</template>
