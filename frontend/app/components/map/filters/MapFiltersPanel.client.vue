<script setup lang="ts">
import type { MultiFilter } from "~/types/filters"
import type { FiltersOptions } from "~/types/schools"

const multiSelectFilters = defineModel<MultiFilter[]>()

const { min_score, max_score, hasActiveFilters, resetFilters } =
    useSchoolFilters()

// Get available items (not already selected) for a filter
const getAvailableItems = (
    options: FiltersOptions,
    selectedValues: number[] | undefined,
    currentIndex?: number,
) => {
    const allItems = options ?? []
    const items = allItems.map((option) => ({
        label: option.nazwa,
        value: option.id,
    })) // for select menu component

    if (!selectedValues || selectedValues.length === 0) {
        return items
    }

    // Keep items not selected, OR the current selection at this index
    return items.filter(
        (item) =>
            !selectedValues.includes(item.value) ||
            (currentIndex !== undefined &&
                selectedValues[currentIndex] === item.value),
    )
}

// Check if we can add more selections (more options still available)
const canAddMore = (
    optionsKey: FiltersOptions,
    userSelections: number[] | undefined,
) => {
    if (!userSelections || userSelections.length === 0) {
        return true
    }
    return userSelections.length < optionsKey.length
}
</script>
<template>
    <!-- Filter Panel -->
    <div
        class="max-h-[70vh] max-w-full overflow-x-auto overflow-y-auto rounded-xl border border-default bg-default/95 p-3 shadow-2xl backdrop-blur-md">
        <!-- Filter Options -->
        <div class="flex flex-col gap-2">
            <!-- Dynamic Filter Selects -->
            <div class="flex flex-wrap gap-4">
                <div
                    v-for="filter in multiSelectFilters"
                    :key="filter.key"
                    class="flex flex-col gap-2 min-w-50 flex-1 max-w-75">
                    <label class="text-xs font-medium text-toned">
                        {{ filter.label }}
                    </label>

                    <!-- Existing selections -->
                    <div
                        v-for="(selection, index) in filter.selected ?? []"
                        :key="`${filter.key}-${index}`"
                        class="flex gap-2 items-center">
                        <USelectMenu
                            :virtualize="{
                                estimateSize: 48, // estimated height per item
                                overscan: 12, // items to render outside viewport
                            }"
                            :model-value="selection"
                            :items="
                                getAvailableItems(
                                    filter.options,
                                    filter.selected,
                                    index,
                                )
                            "
                            value-key="value"
                            :search-input="{
                                placeholder: 'Szukaj...',
                                icon: 'i-mdi-magnify',
                                autofocus: false,
                            }"
                            size="sm"
                            :ui="{
                                content: 'min-w-[320px]',
                                itemLabel: 'whitespace-normal',
                            }"
                            class="flex-1 min-w-0"
                            @update:model-value="
                                (val: number) => {
                                    const current = [...(filter.selected ?? [])]
                                    current[index] = val
                                    filter.selected = current
                                }
                            " />
                        <UButton
                            icon="i-mdi-close"
                            color="error"
                            variant="ghost"
                            size="xs"
                            @click="
                                () => {
                                    const current = [
                                        ...(filter.selected as number[]),
                                    ]
                                    current.splice(index, 1)
                                    filter.selected = current
                                }
                            " />
                    </div>

                    <div
                        v-if="filter.addingState"
                        class="flex gap-2 items-center">
                        <USelectMenu
                            :virtualize="{
                                estimateSize: 48, // estimated height per item
                                overscan: 12, // items to render outside viewport
                            }"
                            :items="
                                getAvailableItems(
                                    filter.options,
                                    filter.selected,
                                )
                            "
                            :search-input="{
                                placeholder: 'Szukaj...',
                                icon: 'i-mdi-magnify',
                                autofocus: false,
                            }"
                            size="sm"
                            :ui="{
                                content: 'min-w-[320px]',
                                itemLabel: 'whitespace-normal',
                            }"
                            :model-value="undefined"
                            value-key="value"
                            placeholder="Wybierz z listy..."
                            default-open
                            class="flex-1 min-w-0"
                            @update:model-value="
                                (val: number) => {
                                    const current = [...(filter.selected ?? [])]
                                    current.push(val)
                                    filter.selected = current
                                    filter.addingState = false
                                }
                            " />
                        <UButton
                            icon="i-mdi-close"
                            color="neutral"
                            variant="ghost"
                            size="xs"
                            @click="filter.addingState = false" />
                    </div>
                    <!-- Add button -->
                    <UButton
                        v-if="
                            !filter.addingState &&
                            canAddMore(filter.options, filter.selected)
                        "
                        icon="i-mdi-plus"
                        :label="
                            !filter.selected || filter.selected.length === 0
                                ? filter.placeholder
                                : 'Dodaj kolejny'
                        "
                        color="neutral"
                        variant="ghost"
                        size="sm"
                        class="w-full"
                        @click="filter.addingState = true" />
                </div>
            </div>

            <!-- Score Range Section -->
            <div
                class="bg-muted rounded-lg p-2 flex flex-row flex-wrap gap-x-6 gap-y-2 items-center justify-center">
                <div class="flex items-center gap-1.5">
                    <UIcon name="i-mdi-star" class="text-amber-500 size-4" />
                    <span class="text-sm font-medium text-toned"
                        >Punkty (0-100)</span
                    >
                </div>
                <div class="flex items-center gap-4">
                    <div class="flex items-center gap-1">
                        <span class="text-xs text-muted">Min</span>
                        <UInputNumber
                            v-model="min_score"
                            :min="0"
                            :max="100"
                            size="sm"
                            placeholder="0"
                            class="w-25" />
                    </div>
                    <span class="text-dimmed text-xs">—</span>
                    <div class="flex items-center gap-1">
                        <span class="text-xs text-muted">Max</span>
                        <UInputNumber
                            v-model="max_score"
                            placeholder="100"
                            size="sm"
                            :min="0"
                            :max="100"
                            class="w-25" />
                    </div>
                </div>
            </div>

            <!-- Actions -->
            <div class="flex items-center justify-end pt-2 border-t border-default">
                <UButton
                    v-if="hasActiveFilters"
                    icon="i-mdi-close-circle"
                    label="Wyczyść filtry"
                    color="error"
                    variant="ghost"
                    size="sm"
                    @click="resetFilters" />
            </div>
        </div>
    </div>
</template>
