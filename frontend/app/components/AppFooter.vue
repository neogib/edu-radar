<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui"

const items: NavigationMenuItem[] = [
    { label: "O nas", to: "/about" },
    { label: "Kontakt", to: "/contact" },
]
</script>

<template>
    <UFooter class="mt-16 border-t border-default">
        <template #left>
            <p class="text-sm text-muted">
                © {{ new Date().getFullYear() }} EduRadar
            </p>
        </template>

        <UNavigationMenu :items="items" variant="link" />

        <template #right>
            <UButton
                color="neutral"
                variant="ghost"
                to="https://github.com/neogib/edu-map-rankings"
                target="_blank"
                icon="i-simple-icons-github"
                aria-label="GitHub" />
        </template>
    </UFooter>
</template>
