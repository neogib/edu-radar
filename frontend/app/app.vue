<script setup lang="ts">
useSeoMeta({
    ogImage: "/og-image.png",
    twitterImage: "/og-image.png",
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
