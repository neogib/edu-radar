<script setup lang="ts">
import type { SzkolaPublicWithRelations } from "~/types/schools"
import { formatNumber } from "~/utils/schoolDetailsFormat"

interface Props {
    school: SzkolaPublicWithRelations
}

const props = defineProps<Props>()

const locationLabel = computed(() => {
    const location = props.school.miejscowosc
    const county = location.gmina.powiat.nazwa
    const voivodeship = location.gmina.powiat.wojewodztwo.nazwa

    return [location.nazwa, `powiat ${county}`, voivodeship]
        .filter(Boolean)
        .join(" • ")
})
</script>

<template>
    <UCard>
        <template #header>
            <div
                class="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div class="space-y-2">
                    <h1
                        class="text-2xl font-semibold text-highlighted sm:text-3xl">
                        {{ school.nazwa }}
                    </h1>
                    <p class="text-sm text-toned">
                        {{ locationLabel }}
                    </p>
                </div>

                <div class="flex flex-wrap gap-2">
                    <UBadge color="primary" variant="soft">
                        {{ school.typ.nazwa }}
                    </UBadge>
                    <UBadge color="info" variant="soft">
                        {{ school.statusPublicznoprawny.nazwa }}
                    </UBadge>
                    <UBadge color="neutral" variant="soft">
                        {{ school.kategoriaUczniow.nazwa }}
                    </UBadge>
                    <UBadge
                        :color="school.zlikwidowana ? 'error' : 'success'"
                        variant="soft">
                        {{ school.zlikwidowana ? "Zlikwidowana" : "Aktywna" }}
                    </UBadge>
                </div>
            </div>
        </template>

        <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
            <div class="rounded-lg border border-default bg-default p-4">
                <p class="text-xs text-muted">Wynik szkoły</p>
                <p class="mt-1 text-2xl font-semibold text-primary">
                    {{ formatNumber(school.wynik) }}
                </p>
            </div>
            <div class="rounded-lg border border-default bg-default p-4">
                <p class="text-xs text-muted">Liczba uczniów</p>
                <p class="mt-1 text-2xl font-semibold text-highlighted">
                    {{ formatNumber(school.liczbaUczniow, 0) }}
                </p>
            </div>
            <div class="rounded-lg border border-default bg-default p-4">
                <p class="text-xs text-muted">Numer RSPO</p>
                <p class="mt-1 text-2xl font-semibold text-highlighted">
                    {{ school.numerRspo }}
                </p>
            </div>
        </div>
    </UCard>
</template>
