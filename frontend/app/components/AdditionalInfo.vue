<template>
    <div
        class="mt-16 rounded-2xl border border-default bg-linear-to-r from-indigo-100 via-violet-50 to-purple-100 dark:from-indigo-700 dark:via-violet-700 dark:to-purple-700 p-8">
        <div class="text-center">
            <h2 class="text-3xl font-bold text-highlighted mb-4">
                Dlaczego warto korzystać z naszego rankingu?
            </h2>
            <div class="grid md:grid-cols-3 gap-8 mt-8">
                <div
                    class="text-center rounded-xl border border-default bg-default p-5">
                    <NuxtImg
                        src="/images/filter_schools.png"
                        alt="Filtry i wyszukiwanie"
                        width="144"
                        height="144"
                        loading="lazy"
                        class="feature-image border border-accented" />
                    <h3 class="feature-heading text-highlighted">
                        Filtry i wyszukiwanie
                    </h3>
                    <p class="text-toned">
                        Filtruj szkoły według rodzaju, statusu i innych
                        kryteriów
                    </p>
                </div>
                <div
                    class="text-center rounded-xl border border-default bg-default p-5">
                    <NuxtImg
                        src="/images/location.png"
                        alt="Lokalizacja"
                        width="144"
                        height="144"
                        loading="lazy"
                        class="feature-image border border-accented" />
                    <h3 class="feature-heading text-highlighted">
                        Lokalizacja
                    </h3>
                    <p class="text-toned">
                        Znajdź szkoły w swojej okolicy na interaktywnej mapie
                    </p>
                </div>
                <div
                    class="text-center rounded-xl border border-default bg-default p-5">
                    <NuxtImg
                        src="/images/up-to-date_data.png"
                        alt="Aktualne dane"
                        width="144"
                        height="144"
                        loading="lazy"
                        class="feature-image border border-accented" />
                    <h3 class="feature-heading text-highlighted">
                        Aktualne dane
                    </h3>
                    <p class="text-toned">
                        Regularnie aktualizowane wyniki i statystyki szkół
                    </p>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
@reference "tailwindcss";

.feature-image {
    @apply w-36 h-36 rounded-full mb-4 mx-auto object-cover;
}

.feature-heading {
    @apply text-xl font-semibold mb-2;
}
</style>
