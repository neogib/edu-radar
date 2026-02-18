import type { SelectMenuItem } from "@nuxt/ui"
import type { Ref } from "vue"
import {
    RANKING_DIRECTION_LABELS,
    RANKING_SCOPE_LABELS,
    RANKING_TYPE_LABELS,
} from "~/constants/ranking"
import type { RankingsFiltersResponse } from "~/types/ranking"

export const useRankingsOptions = (
    filtersData: Ref<RankingsFiltersResponse | undefined>,
) => {
    const yearOptions = computed<SelectMenuItem[]>(() =>
        (filtersData.value?.years ?? []).map((year) => ({
            label: String(year),
            value: year,
        })),
    )

    const typeOptions = computed<SelectMenuItem[]>(() =>
        (filtersData.value?.types ?? []).map((type) => ({
            label: RANKING_TYPE_LABELS[type],
            value: type,
        })),
    )

    const scopeOptions = computed<SelectMenuItem[]>(() =>
        (filtersData.value?.scopes ?? []).map((scope) => ({
            label: RANKING_SCOPE_LABELS[scope],
            value: scope,
        })),
    )

    const directionOptions = computed<SelectMenuItem[]>(() =>
        (filtersData.value?.directions ?? []).map((direction) => ({
            label: RANKING_DIRECTION_LABELS[direction],
            value: direction,
        })),
    )

    const voivodeshipOptions = computed<SelectMenuItem[]>(() =>
        (filtersData.value?.voivodeships ?? []).map((voivodeship) => ({
            label: voivodeship.nazwa,
            value: voivodeship.id,
        })),
    )

    const voivodeshipNameById = computed(() => {
        const voivodeships = filtersData.value?.voivodeships ?? []

        return new Map(
            voivodeships.map((voivodeship) => [
                voivodeship.id,
                voivodeship.nazwa,
            ]),
        )
    })

    const countyOptions = computed<SelectMenuItem[]>(() =>
        (filtersData.value?.counties ?? []).map((county) => ({
            label: `${county.nazwa} (${voivodeshipNameById.value.get(county.wojewodztwo_id) ?? "?"})`,
            value: county.id,
        })),
    )

    return {
        yearOptions,
        typeOptions,
        scopeOptions,
        directionOptions,
        voivodeshipOptions,
        countyOptions,
    }
}
