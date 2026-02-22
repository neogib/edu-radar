<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui"
import logoFullHorizontal from "@/assets/logo/logo-full-horizontal.svg"
import logoHorizontalSmall from "@/assets/logo/logo-full-horizontal-small.svg"

const route = useRoute()
const props = withDefaults(
    defineProps<{
        overlay?: boolean
    }>(),
    {
        overlay: false,
    },
)

const headerUi = computed(() =>
    props.overlay
        ? {
              root: "backdrop-blur-[2px]",
          }
        : undefined,
)

// 'active' state automatically updates when the route changes
const items = computed<NavigationMenuItem[]>(() => [
    {
        label: "Mapa",
        to: "/map",
        icon: "i-mdi-map",
        active: route.path.startsWith("/map"),
    },
    {
        label: "Ranking",
        to: "/ranking",
        icon: "i-mdi-chart-bar",
        active: route.path.startsWith("/ranking"),
    },
    {
        label: "O nas",
        to: "/about",
        icon: "i-mdi-information",
        active: route.path.startsWith("/about"),
    },
    {
        label: "Kontakt",
        to: "/contact",
        icon: "i-mdi-email",
        active: route.path.startsWith("/contact"),
    },
])
</script>

<template>
    <UHeader
        :class="props.overlay ? 'absolute inset-x-0 top-0' : undefined"
        :toggle="{
            color: 'primary',
            class: 'rounded-full',
        }"
        :ui="headerUi"
        mode="slideover">
        <template #title>
            <img
                :src="logoHorizontalSmall"
                alt="Ranking Szkół"
                class="h-8 w-auto md:hidden" />
            <img
                :src="logoFullHorizontal"
                alt="Ranking Szkół"
                class="hidden h-10 w-auto md:block" />
        </template>

        <UNavigationMenu :items="items" />

        <template #right>
            <UColorModeSelect size="sm" />

            <UTooltip text="Open on GitHub" :kbds="['meta', 'G']">
                <UButton
                    color="neutral"
                    variant="ghost"
                    to="https://github.com/neogib/edu-radar"
                    target="_blank"
                    icon="i-simple-icons-github"
                    aria-label="GitHub" />
            </UTooltip>
        </template>

        <template #body>
            <UNavigationMenu
                :items="items"
                orientation="vertical"
                class="-mx-2.5"
                :ui="{
                    link: 'px-3 py-2.5 text-base',
                    linkLeadingIcon: 'size-6',
                }" />
        </template>
    </UHeader>
</template>
