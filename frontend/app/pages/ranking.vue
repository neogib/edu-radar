<script setup lang="ts">
import type { TableColumn } from "@nuxt/ui"
import type {
    RankingWithSchool,
    RankingScope,
    RankingTableRow,
    RankingsFiltersResponse,
    RodzajRankingu,
    RankingDirection,
} from "~/types/ranking"

const { data: filtersData, error: filtersError } =
    await useApi<RankingsFiltersResponse>("/rankings/filters")

const {
    yearOptions,
    typeOptions,
    scopeOptions,
    directionOptions,
    voivodeshipOptions,
    countyOptions,
} = useRankingsOptions(filtersData)

const {
    rankingsData,
    rankingsStatus,
    rankingsError,
    selectedPage,
    selectedYear,
    selectedType,
    selectedScope,
    selectedDirection,
    selectedVoivodeshipId,
    selectedCountyId,
} = useRankingsData(filtersData.value?.years[0] ?? new Date().getFullYear() - 1)

const formatNumber = (value: number) =>
    new Intl.NumberFormat("pl-PL", {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2,
    }).format(value)

const getPlaceByScope = (
    ranking: RankingWithSchool,
    scope: RankingScope,
): number => {
    if (scope === "WOJEWODZTWO") return ranking.miejsce_wojewodztwo
    if (scope === "POWIAT") return ranking.miejsce_powiat
    return ranking.miejsce_kraj
}

const tableRows = computed<RankingTableRow[]>(() => {
    const rankings = rankingsData.value?.rankings ?? []
    const scope = selectedScope.value
    if (!scope) return []

    return rankings.map((ranking) => ({
        id: ranking.id,
        place: getPlaceByScope(ranking, scope),
        schoolName: ranking.szkola.nazwa,
        city: ranking.szkola.miejscowosc.nazwa,
        status: ranking.szkola.status_publicznoprawny.nazwa,
        score: formatNumber(ranking.wynik),
    }))
})

const columns: TableColumn<RankingTableRow>[] = [
    { accessorKey: "place", header: "Miejsce" },
    { accessorKey: "schoolName", header: "Szkoła" },
    { accessorKey: "city", header: "Miejscowość" },
    { accessorKey: "status", header: "Status" },
    { accessorKey: "score", header: "Wynik" },
]

const schoolNameModalOpen = ref(false)
const selectedSchoolName = ref("")

const openSchoolNameModal = (schoolName: string) => {
    selectedSchoolName.value = schoolName
    schoolNameModalOpen.value = true
}

const getPlaceBadgeColor = (place: number) => {
    if (place <= 3) return "success"
    if (place <= 10) return "info"
    if (place <= 50) return "warning"
    return "neutral"
}

const totalItems = computed(() => rankingsData.value?.total ?? 0)
const itemsPerPage = computed(() => rankingsData.value?.pageSize ?? 50)
const totalPages = computed(() => rankingsData.value?.totalPages ?? 0)

const handleScopeChange = (scope: RankingScope) => {
    selectedScope.value = scope

    if (scope === "KRAJ") {
        selectedVoivodeshipId.value = undefined
        selectedCountyId.value = undefined
    } else if (scope === "WOJEWODZTWO") {
        selectedCountyId.value = undefined
        console.log(voivodeshipOptions.value[0], selectedVoivodeshipId.value)
        selectedVoivodeshipId.value = voivodeshipOptions.value[0]?.value
        console.log(voivodeshipOptions.value[0], selectedVoivodeshipId.value)
    } else if (scope === "POWIAT") {
        selectedVoivodeshipId.value = undefined
        selectedCountyId.value = countyOptions.value[0]?.value
    }

    selectedPage.value = 1
}

const hasError = computed(
    () => Boolean(filtersError.value) || Boolean(rankingsError.value),
)

const sortTrailingIcon = computed(() =>
    selectedDirection.value === "WORST"
        ? "i-lucide-arrow-down"
        : "i-lucide-arrow-up",
)
</script>

<template>
    <div class="max-w-7xl mx-auto px-2 sm:px-5 lg:px-8 space-y-4">
        <UPageHeader
            title="Ranking szkół"
            description="Analizuj pozycję szkół w rankingach – porównuj miejsca w kraju, województwie lub powiecie."
            :ui="{
                root: 'mb-1 py-4',
                container: 'py-1 sm:py-2',
            }" />

        <div class="flex flex-wrap items-end gap-3">
            <USelectMenu
                :model-value="selectedYear"
                :items="yearOptions"
                value-key="value"
                :search-input="{ placeholder: 'Wybierz rok' }"
                color="primary"
                placeholder="Rok"
                class="min-w-28"
                @update:model-value="
                    (value: number) => {
                        selectedYear = value
                        selectedPage = 1
                    }
                " />

            <USelectMenu
                :model-value="selectedType"
                :items="typeOptions"
                value-key="value"
                :search-input="{ placeholder: 'Wybierz typ rankingu' }"
                color="info"
                placeholder="Typ rankingu"
                class="min-w-56"
                @update:model-value="
                    (value: RodzajRankingu) => {
                        selectedType = value
                        selectedPage = 1
                    }
                " />

            <USelect
                :model-value="selectedDirection"
                :items="directionOptions"
                value-key="value"
                :trailing-icon="sortTrailingIcon"
                class="min-w-52"
                @update:model-value="
                    (value: RankingDirection) => {
                        selectedDirection = value
                        selectedPage = 1
                    }
                " />

            <USelectMenu
                :model-value="selectedScope"
                :items="scopeOptions"
                value-key="value"
                :search-input="{ placeholder: 'Wybierz zakres' }"
                color="warning"
                placeholder="Zakres"
                class="min-w-40"
                @update:model-value="
                    (value: RankingScope) => handleScopeChange(value)
                " />

            <USelectMenu
                v-if="selectedScope === 'WOJEWODZTWO'"
                :model-value="selectedVoivodeshipId"
                :items="voivodeshipOptions"
                value-key="value"
                :search-input="{ placeholder: 'Wybierz Województwo' }"
                color="primary"
                placeholder="Województwo"
                class="min-w-56"
                @update:model-value="
                    (value: number) => {
                        selectedVoivodeshipId = value
                        selectedPage = 1
                    }
                " />

            <USelectMenu
                v-if="selectedScope === 'POWIAT'"
                :model-value="selectedCountyId"
                :items="countyOptions"
                virtualize
                value-key="value"
                :search-input="{ placeholder: 'Wybierz powiat' }"
                color="primary"
                placeholder="Powiat"
                class="min-w-72"
                @update:model-value="
                    (value: number) => {
                        selectedCountyId = value
                        selectedPage = 1
                    }
                " />
        </div>

        <div
            v-if="rankingsStatus === 'pending'"
            class="flex items-center gap-2 text-sm text-primary animate-pulse">
            <UIcon name="i-lucide-loader-circle" class="size-4 animate-spin" />
            <span>Ładowanie danych rankingu...</span>
        </div>

        <UAlert
            v-if="hasError"
            color="error"
            variant="soft"
            title="Nie udało się pobrać rankingów." />

        <div class="flex justify-center">
            <UPagination
                v-model:page="selectedPage"
                :total="totalItems"
                :items-per-page="itemsPerPage"
                :disabled="totalPages === 0"
                :sibling-count="0"
                show-edges
                color="primary"
                active-color="info" />
        </div>

        <UTable
            :data="tableRows"
            :columns="columns"
            :loading="rankingsStatus === 'pending'"
            loading-animation="carousel"
            loading-color="primary"
            empty="Brak wyników dla wybranych filtrów."
            class="rounded-lg border border-primary/20 bg-default/70">
            <template #place-cell="{ row }">
                <UBadge
                    variant="soft"
                    :color="getPlaceBadgeColor(row.original.place)">
                    {{ row.original.place }}
                </UBadge>
            </template>

            <template #schoolName-cell="{ row }">
                <UTooltip :text="row.original.schoolName">
                    <UButton
                        color="neutral"
                        variant="link"
                        class="w-60 lg:w-[320px] max-w-105 truncate p-0 text-left"
                        :label="row.original.schoolName"
                        @click="openSchoolNameModal(row.original.schoolName)" />
                </UTooltip>
            </template>

            <template #score-cell="{ row }">
                <span class="font-medium text-primary">
                    {{ row.original.score }}
                </span>
            </template>
        </UTable>

        <div class="flex justify-center">
            <UPagination
                v-model:page="selectedPage"
                :total="totalItems"
                :items-per-page="itemsPerPage"
                :disabled="totalPages === 0"
                :sibling-count="0"
                show-edges
                color="primary"
                active-color="info" />
        </div>

        <UModal
            v-model:open="schoolNameModalOpen"
            title="Pełna nazwa szkoły"
            :ui="{ body: 'break-words' }">
            <template #body>
                <p>{{ selectedSchoolName }}</p>
            </template>
        </UModal>
    </div>
</template>
