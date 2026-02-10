<script setup lang="ts">
import type { SlideoverProps } from "@nuxt/ui"
import type { UseSwipeDirection } from "@vueuse/core"
import { useMediaQuery, usePointerSwipe } from "@vueuse/core"
import type { SzkolaPublicWithRelations } from "~/types/schools"

interface Props {
    selectedPoint: SzkolaPublicWithRelations
}

const props = defineProps<Props>()
const emit = defineEmits<{
    close: []
}>()
const isLgUp = useMediaQuery("(min-width: 1024px)")
const swipeTarget = shallowRef<HTMLElement | null>(null)
const isDismissedBySwipe = ref(false)

const swipe = usePointerSwipe(swipeTarget, {
    pointerTypes: ["touch", "pen"],
    onSwipeEnd(_: PointerEvent, direction: UseSwipeDirection) {
        const dragX = Math.max(0, swipe.distanceX.value)
        if (direction === "left" && dragX >= 100)
            isDismissedBySwipe.value = true
    },
})

const transform = computed(() => {
    if (isDismissedBySwipe.value) return "translateX(-100%)"
    if (!swipe.isSwiping.value) return "translateX(0)"

    const dragX = Math.max(0, swipe.distanceX.value)
    return `translateX(${-dragX}px)`
})

const contentProps = computed<NonNullable<SlideoverProps["content"]>>(
    // intentionally pass through DOM attrs/events to the underlying DialogContent.
    () =>
        ({
            ref: (el: Element | null) => {
                swipeTarget.value = el as HTMLElement | null
            },
            class: swipe.isSwiping.value
                ? ""
                : "transition-transform duration-200 ease-linear",
            onTransitionend: handleContentTransitionEnd,
            style: {
                transform: transform.value,
            },
        }) as unknown as NonNullable<SlideoverProps["content"]>,
)

const handleContentTransitionEnd = (event: Event) => {
    const transitionEvent = event as TransitionEvent

    if (
        isDismissedBySwipe.value &&
        transitionEvent.propertyName === "transform"
    ) {
        emit("close")
    }
}

const isPublicSchool = (status: string) => {
    return !status.toLowerCase().includes("nie")
}

// computed property for selected point score color
const scoreColor = computed(() => {
    return props.selectedPoint ? getScoreColor(props.selectedPoint.wynik) : ""
})
</script>

<template>
    <USlideover
        side="left"
        :modal="!isLgUp"
        :transition="!isDismissedBySwipe"
        title="Szczegóły placówki"
        close-icon="i-mdi-close"
        :content="contentProps"
        :ui="{
            overlay: 'lg:hidden',
            body: 'overflow-x-hidden p-0 sm:p-0',
        }">
        <template #body>
            <div class="relative pb-20">
                <div
                    class="p-4 bg-linear-to-br from-blue-50 to-indigo-50 border-b">
                    <h3 class="text-xl font-bold text-gray-900 mb-3">
                        {{ selectedPoint.nazwa }}
                    </h3>

                    <div class="flex flex-wrap gap-2 mb-4">
                        <span class="badge badge-blue">
                            <Icon
                                name="mdi:school-outline"
                                class="badge-icon" />
                            {{ selectedPoint.typ.nazwa || "Szkoła" }}
                        </span>

                        <span
                            class="badge"
                            :class="[
                                isPublicSchool(
                                    selectedPoint.status_publicznoprawny
                                        .nazwa || '',
                                )
                                    ? 'badge-green'
                                    : 'badge-purple',
                            ]">
                            <Icon
                                v-if="
                                    isPublicSchool(
                                        selectedPoint.status_publicznoprawny
                                            .nazwa || '',
                                    )
                                "
                                name="mdi:check-decagram" />
                            <Icon v-else name="mdi:lock" />
                            {{ selectedPoint.status_publicznoprawny.nazwa }}
                        </span>
                    </div>

                    <div
                        v-if="
                            selectedPoint.wynik !== null &&
                            selectedPoint.wynik !== undefined
                        "
                        class="bg-white rounded-xl p-4 shadow-sm">
                        <div class="flex items-center justify-between">
                            <div>
                                <p
                                    class="text-xs text-gray-500 uppercase tracking-wide mb-1">
                                    Wynik ogólny
                                </p>
                                <div class="flex items-baseline">
                                    <span
                                        :class="'text-3xl font-bold'"
                                        :style="{
                                            color: scoreColor,
                                        }">
                                        {{ selectedPoint.wynik.toFixed(2) }}
                                    </span>
                                </div>
                            </div>
                        </div>

                        <div class="mt-3 w-full bg-gray-200 rounded-full h-2">
                            <div
                                :class="[
                                    'h-2 rounded-full transition-all duration-500',
                                ]"
                                :style="{
                                    width: `${selectedPoint.wynik}%`,
                                    'background-color': scoreColor,
                                }" />
                        </div>
                    </div>
                </div>

                <SidebarExamResults
                    :wyniki-e8="selectedPoint.wyniki_e8"
                    :wyniki-em="selectedPoint.wyniki_em" />
                <SidebarSchoolInfo :selected-point="selectedPoint" />
            </div>
        </template>
    </USlideover>
</template>

<style scoped>
@reference "tailwindcss";

.badge-icon {
    @apply w-3 h-3 mr-1.5;
}
.badge {
    @apply inline-flex items-center px-3 py-1 rounded-full text-xs font-medium;
}
.badge-blue {
    @apply bg-blue-100 text-blue-800;
}
.badge-green {
    @apply bg-green-100 text-green-800;
}
.badge-purple {
    @apply bg-purple-100 text-purple-800;
}
</style>
