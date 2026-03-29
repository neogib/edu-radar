<script setup lang="ts">
interface Props {
    hasLeftColumnContent: boolean
}

defineProps<Props>()
</script>

<template>
    <div class="space-y-6">
        <UCard>
            <template #header>
                <div class="space-y-2">
                    <USkeleton class="h-10 w-full max-w-2xl" />
                    <USkeleton class="h-4 w-full max-w-xl" />
                </div>
            </template>

            <div class="grid gap-3 sm:grid-cols-2 xl:grid-cols-3">
                <USkeleton class="h-20" />
                <USkeleton class="h-20" />
                <USkeleton class="h-20" />
            </div>
        </UCard>

        <div
            class="grid grid-cols-1 gap-6"
            :class="hasLeftColumnContent ? 'lg:grid-cols-12' : ''">
            <div
                v-if="hasLeftColumnContent"
                class="min-w-0 space-y-6 lg:col-span-8">
                <UCard>
                    <USkeleton class="h-56" />
                </UCard>
                <UCard>
                    <USkeleton class="h-64" />
                </UCard>
                <UCard>
                    <USkeleton class="h-72" />
                </UCard>
            </div>
            <div
                class="min-w-0 space-y-6"
                :class="hasLeftColumnContent ? 'lg:col-span-4' : ''">
                <UCard>
                    <USkeleton class="h-72" />
                </UCard>
                <UCard>
                    <USkeleton class="h-48" />
                </UCard>
            </div>
        </div>
    </div>
</template>
