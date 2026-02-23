<script setup lang="ts">
import logoFullVertical from "@/assets/logo/logo-full-vertical.svg"

useSeoMeta({
    title: "Wybierz szkołę świadomie",
    description:
        "Interaktywna mapa szkół. Znajdź najlepsze szkoły w swojej okolicy i porównuj rankingi.",
})
</script>

<template>
    <div class="max-w-7xl mx-auto px-2 sm:px-5 lg:px-8">
        <UPageHero
            title="Wybierz szkołę świadomie"
            description="Interaktywna mapa szkół. Znajdź najlepsze szkoły w swojej okolicy. Porównuj rankingi, sprawdzaj wyniki i podejmuj świadome decyzje."
            orientation="horizontal"
            :ui="{
                container: 'py-4 sm:py-6 lg:py-8',
            }"
            class="mb-6 sm:mb-8">
            <img
                :src="logoFullVertical"
                alt="Ranking Szkół"
                class="mx-auto h-36 w-auto sm:h-44 md:h-56 lg:h-64" />
        </UPageHero>

        <SchoolSearchForm />
        <AdditionalInfo />
    </div>
</template>
