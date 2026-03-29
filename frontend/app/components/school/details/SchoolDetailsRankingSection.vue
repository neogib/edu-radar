<script setup lang="ts">
import type { SzkolaPublicWithRelations } from "~/types/schools"
import { formatPercentyl } from "~/utils/ranking"

interface Props {
    school: SzkolaPublicWithRelations
}

const props = defineProps<Props>()

const {
    hasRankingGroups,
    rankingGroups,
    rankingDonutCategories,
    getBetterThanPercent,
    getRankingDonutData,
    getRankingScopeColor,
} = useSchoolRankingSummary({
    school: () => props.school,
})
</script>

<template>
    <UCard v-if="hasRankingGroups" :ui="{ body: 'space-y-4' }">
        <template #header>
            <h2 class="text-lg font-semibold text-highlighted">Ranking</h2>
        </template>

        <div class="space-y-4">
            <div
                v-for="group in rankingGroups"
                :key="`${group.examType}-${group.year}`"
                class="space-y-2">
                <USeparator :label="`${group.label} · ${group.year}`" />

                <UCard
                    v-for="row in group.rows"
                    :key="`${group.examType}-${group.year}-${row.scope}`"
                    :ui="{ body: 'p-3' }">
                    <div
                        class="grid grid-cols-1 items-center gap-3 sm:grid-cols-[minmax(0,1fr)_110px]">
                        <div>
                            <p class="font-semibold" :class="row.textClass">
                                TOP {{ formatPercentyl(row.percentyl) }}%
                            </p>
                            <UBadge
                                class="mt-1"
                                variant="soft"
                                :color="getRankingScopeColor(row.scope)">
                                {{ row.scopeLabel }}
                            </UBadge>
                            <p class="mt-1 text-xs text-muted">
                                #{{ row.miejsce }} / {{ row.liczbaSzkol }}
                            </p>
                            <p
                                class="mt-1 text-sm font-medium text-highlighted">
                                Lepsza od
                                {{
                                    formatPercentyl(
                                        getBetterThanPercent(row.percentyl),
                                    )
                                }}% szkół
                            </p>
                        </div>

                        <div class="relative">
                            <DonutChart
                                :data="getRankingDonutData(row.percentyl)"
                                :categories="rankingDonutCategories"
                                :height="120"
                                :radius="0"
                                :arc-width="16"
                                :hide-legend="true" />
                            <div
                                class="pointer-events-none absolute inset-0 flex flex-col items-center justify-center">
                                <span class="text-[10px] text-muted">
                                    Lepsza od
                                </span>
                                <span
                                    class="text-lg font-semibold text-success">
                                    {{
                                        formatPercentyl(
                                            getBetterThanPercent(row.percentyl),
                                        )
                                    }}%
                                </span>
                            </div>
                        </div>
                    </div>
                </UCard>
            </div>
        </div>
    </UCard>
</template>
