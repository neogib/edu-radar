<script setup lang="ts">
useSeoMeta({
    ogImage: "/og-image.jpg",
    twitterImage: "/og-image.jpg",
    twitterCard: "summary_large_image",
    ogType: "website",
})
</script>

<template>
    <UApp>
        <NuxtLayout>
            <NuxtPage />
        </NuxtLayout>
    </UApp>
</template>
