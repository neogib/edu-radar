<script setup lang="ts">
import { LazySidebarMain } from "#components"
import type { SzkolaPublicWithRelations } from "~/types/schools"

definePageMeta({
    middleware: "redirect-map",
    layout: false,
})

useSeoMeta({
    title: "Mapa szkół w Polsce i rankingi",
    description:
        "Interaktywna mapa szkół w Polsce z rankingami, wynikami egzaminów i filtrowaniem.",
})

const selectedSchool = ref<SzkolaPublicWithRelations | null>(null)
const route = useRoute()
const { $api } = useNuxtApp()
const overlay = useOverlay()
const sidebar = overlay.create(LazySidebarMain)
let sidebarRequestId = 0

const schoolRouteParam = computed(() => {
    const match = route.path.match(/^\/map\/schools\/([^/]+)\/?$/)
    if (!match) return null
    return match[1] ?? null
})

const navigateToMap = () =>
    navigateTo(
        {
            path: "/map",
            query: route.query,
        },
        { replace: true },
    )

const navigateToSchool = (schoolId: number) =>
    navigateTo({
        path: `/map/schools/${schoolId}`,
        query: route.query,
    })

const handleSidebarCloseAction = () => {
    closeSidebar()

    setTimeout(() => {
        if (!window.location.pathname.startsWith("/map/schools/")) return
        void navigateToMap()
    }, 0)
}

const openSidebar = (school: SzkolaPublicWithRelations) => {
    selectedSchool.value = school

    if (overlay.isOpen(sidebar.id)) {
        sidebar.patch({
            selectedPoint: school,
            onClose: handleSidebarCloseAction,
        })
        return
    }

    const instance = sidebar.open({
        selectedPoint: school,
        onClose: handleSidebarCloseAction,
    })

    void instance.result.finally(() => {
        selectedSchool.value = null
    })
}

const closeSidebar = () => {
    sidebar.close()
    selectedSchool.value = null
}

const handlePointClick = (schoolId: number | null) => {
    if (schoolId === null) {
        void navigateToMap()
        return
    }

    void navigateToSchool(schoolId)
}

const fetchSchoolById = async (schoolId: number) => {
    try {
        return await $api<SzkolaPublicWithRelations>(`/schools/${schoolId}`)
    } catch {
        return null
    }
}

watch(
    schoolRouteParam,
    async (schoolRouteId) => {
        if (schoolRouteId === null) {
            closeSidebar()
            return
        }

        const schoolId = Number.parseInt(schoolRouteId, 10)

        if (!Number.isInteger(schoolId) || schoolId <= 0) {
            closeSidebar()
            await navigateToMap()
            return
        }

        const requestId = ++sidebarRequestId
        const school = await fetchSchoolById(schoolId)
        if (requestId !== sidebarRequestId) return

        if (!school) {
            closeSidebar()
            await navigateToMap()
            return
        }

        openSidebar(school)
    },
    { immediate: true },
)

onUnmounted(() => {
    sidebar.close()
})
</script>

<template>
    <div class="relative h-dvh w-screen overflow-hidden">
        <h1 class="sr-only">Mapa szkół w Polsce</h1>
        <NavBar overlay />
        <MapLegend />

        <div v-show="!selectedSchool">
            <MapFilters />
        </div>

        <!-- MapView taking full remaining space -->
        <MapView @point-clicked="handlePointClick" />
        <NuxtPage />
    </div>
</template>
