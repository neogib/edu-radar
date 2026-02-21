<template>
    <UPopover>
        <UButton
            icon="i-mdi-information-outline"
            variant="ghost"
            size="xs"
            class="text-muted hover:text-default"
            aria-label="Informacja o obliczaniu wyniku i rankingu" />

        <template #content>
            <div class="max-w-80 space-y-2 rounded-lg bg-elevated p-3 text-sm">
                <h6 class="text-sm font-semibold text-highlighted">
                    Jak obliczany jest wynik i ranking?
                </h6>

                <p>
                    <strong>Wynik szkoły</strong> to ważona mediana z trzech
                    przedmiotów:
                </p>

                <ul class="list-disc space-y-0.5 pl-4">
                    <li>matematyka - 50%</li>
                    <li>język polski – 25%</li>
                    <li>język angielski – 25%</li>
                </ul>

                <p>
                    Mediany w danym roku są ważone liczbą zdających, a wyniki z
                    poprzednich lat mają mniejszy wpływ na wynik końcowy (zanik
                    czasowy – każdy wcześniejszy rok liczony jest z wagą 70%
                    względem kolejnego).
                </p>

                <p>
                    <strong>Ranking szkół</strong> tworzony jest na podstawie
                    obliczonego wyniku i prowadzony oddzielnie dla szkół
                    podstawowych, liceów oraz techników.
                </p>

                <UButton
                    to="https://github.com/neogib/edu-radar/wiki/Scoring-System"
                    target="_blank"
                    rel="noopener noreferrer"
                    variant="link"
                    size="xs"
                    trailing-icon="i-mdi-open-in-new"
                    class="px-0">
                    Czytaj więcej
                </UButton>
            </div>
        </template>
    </UPopover>
</template>
