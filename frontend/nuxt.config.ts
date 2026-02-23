import tailwindcss from "@tailwindcss/vite"
// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: "2025-07-15",
    devtools: { enabled: true },
    modules: [
        "@nuxt/eslint",
        "@nuxt/ui",
        "nuxt-maplibre",
        "@pinia/nuxt",
        "nuxt-charts",
        "@nuxt/scripts",
        "@nuxtjs/turnstile",
    ],
    turnstile: {
        siteKey: "your_site_key",
    },
    // Runtime environment configuration
    runtimeConfig: {
        proxyURL: "http://localhost:8000/api/v1",
        public: {
            apiBase: "/api/v1",
            martinBase: "http://localhost:3001",
        },
    },
    css: ["~/assets/css/main.css"],
    vite: {
        plugins: [tailwindcss()],
    },
    devServer: {
        host: "0.0.0.0",
    },
    app: {
        head: {
            title: "EduRadar",
            link: [
                { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" },
            ],
        },
    },
})
