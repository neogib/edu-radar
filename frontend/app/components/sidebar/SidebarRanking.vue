<script setup lang="ts">
import type { SzkolaPublicWithRelations } from "~/types/schools"
import { useRankingGroups } from "~/composables/useRankingGroups"
import { formatPercentyl } from "~/utils/ranking"

interface Props {
    selectedPoint: SzkolaPublicWithRelations
}

const { selectedPoint } = defineProps<Props>()

const powiat = computed(() => selectedPoint.miejscowosc.gmina.powiat)
const { rankingGroups, hasRankingGroups } = useRankingGroups({
    rankingi: () => selectedPoint.rankingi ?? [],
    countyName: () => powiat.value.nazwa,
    voivodeshipName: () => powiat.value.wojewodztwo.nazwa,
})
</script>

<template>
    <div
        v-if="hasRankingGroups"
        class="border-b border-default p-4 dark:bg-elevated/35">
        <h4 class="mb-3 flex items-center text-base font-semibold text-default">
            <UIcon name="i-mdi-trophy" class="mr-2 size-5 text-amber-500" />
            Ranking
        </h4>

        <div
            v-for="(group, groupIndex) in rankingGroups"
            :key="`${group.examType}-${group.year}`"
            :class="{ 'mb-4': groupIndex < rankingGroups.length - 1 }">
            <h5 class="mb-2 text-sm font-semibold text-default">
                {{ group.label }} · {{ group.year }}
            </h5>

            <div class="space-y-1.5">
                <div
                    v-for="row in group.rows"
                    :key="`${group.examType}-${group.year}-${row.scope}`"
                    class="rounded-xl border border-default/70 bg-default/80 px-3 py-2 dark:border-white/10 dark:bg-elevated/70">
                    <div
                        v-if="row.medalIcon"
                        class="grid grid-cols-[auto_minmax(0,1fr)_auto] items-center gap-2 text-base">
                        <UIcon
                            :name="row.medalIcon"
                            mode="svg"
                            class="size-6 shrink-0" />
                        <div class="min-w-0">
                            <span
                                class="scope-badge"
                                :class="row.scopeBadgeClass">
                                {{ row.scopeLabel }}
                            </span>
                        </div>
                        <span class="rank-position">
                            #{{ row.miejsce }} / {{ row.liczbaSzkol }}
                        </span>
                    </div>

                    <div
                        v-else
                        class="grid grid-cols-[minmax(130px,auto)_minmax(0,1fr)_auto_auto] items-center gap-3">
                        <div class="min-w-0 flex flex-col items-start">
                            <p class="font-semibold" :class="row.textClass">
                                TOP {{ formatPercentyl(row.percentyl) }}%
                            </p>
                            <span
                                class="scope-badge mt-1"
                                :class="row.scopeBadgeClass">
                                {{ row.scopeLabel }}
                            </span>
                        </div>

                        <div
                            class="h-2.5 w-full overflow-hidden rounded-full bg-gray-200 dark:bg-gray-600/55">
                            <div
                                class="h-full rounded-full transition-all duration-500"
                                :class="row.barClass"
                                :style="{
                                    width: `${row.percentyl}%`,
                                }" />
                        </div>

                        <span
                            class="text-sm font-bold whitespace-nowrap"
                            :class="row.textClass">
                            {{ formatPercentyl(row.percentyl) }}%
                        </span>

                        <span class="rank-position">
                            #{{ row.miejsce }} / {{ row.liczbaSzkol }}
                        </span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>

<style scoped>
@reference "tailwindcss";

.rank-position {
    @apply text-sm whitespace-nowrap text-slate-600 dark:text-slate-300;
}

.scope-badge {
    @apply inline-flex max-w-full items-center truncate rounded-full px-2 py-0.5 text-xs font-semibold ring-1;
}
</style>
