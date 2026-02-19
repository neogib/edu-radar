<script setup lang="ts">
useSeoMeta({
    title: "O nas - EduRadar",
    description:
        "Dowiedz się, czym jest EduRadar i jak pomagamy rodzicom oraz uczniom porównywać szkoły w Polsce.",
})

const highlights = [
    {
        icon: "i-mdi-map-marker-radius",
        title: "Mapa szkół",
        description:
            "Pokazujemy szkoły na interaktywnej mapie, aby łatwo porównać placówki w swojej okolicy.",
    },
    {
        icon: "i-mdi-chart-line",
        title: "Rzetelne rankingi",
        description:
            "Łączymy dane egzaminacyjne i rankingowe, aby prezentować przejrzyste wyniki w skali 0-100.",
    },
    {
        icon: "i-mdi-database-check",
        title: "Dane z oficjalnych źródeł",
        description:
            "Bazujemy na publicznych i regularnie aktualizowanych danych edukacyjnych dla całej Polski.",
    },
] as const
</script>

<template>
    <div class="max-w-7xl mx-auto px-2 sm:px-5 lg:px-8 space-y-8">
        <UPageHero
            title="O EduRadar"
            description="Pomagamy rodzicom i uczniom podejmować świadome decyzje edukacyjne dzięki czytelnym danym, rankingom i mapie szkół."
            :ui="{
                container: 'py-4 sm:py-6',
            }" />

        <div class="grid gap-4 md:grid-cols-3">
            <UCard
                v-for="item in highlights"
                :key="item.title"
                :ui="{ body: 'space-y-3' }">
                <div class="flex items-start gap-3">
                    <UIcon :name="item.icon" class="size-6 text-primary mt-0.5" />
                    <div class="space-y-1">
                        <h2 class="font-semibold">{{ item.title }}</h2>
                        <p class="text-sm text-muted">{{ item.description }}</p>
                    </div>
                </div>
            </UCard>
        </div>

        <UCard :ui="{ body: 'space-y-4' }">
            <h2 class="text-lg font-semibold">Nasza misja</h2>
            <p class="text-sm text-muted">
                Chcemy uprościć dostęp do danych o szkołach i pokazać je w
                formie, która naprawdę pomaga w wyborze placówki. EduRadar
                łączy informacje o wynikach i lokalizacji szkół, żeby
                porównywanie było szybkie, wygodne i transparentne.
            </p>

            <div class="flex flex-wrap gap-3 pt-1">
                <UButton to="/map" icon="i-mdi-map-search" label="Przejdź do mapy" />
                <UButton
                    to="/ranking"
                    color="neutral"
                    variant="outline"
                    icon="i-mdi-trophy-outline"
                    label="Zobacz ranking" />
            </div>
        </UCard>

        <UAlert
            color="info"
            variant="soft"
            title="Dlaczego warto korzystać z EduRadar?"
            description="W jednym miejscu sprawdzisz położenie szkoły, porównasz wyniki i szybciej znajdziesz placówkę dopasowaną do swoich potrzeb." />
    </div>
</template>
