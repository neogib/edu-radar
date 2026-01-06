import tailwindcss from "@tailwindcss/vite"
// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: "2025-07-15",
    devtools: { enabled: true },
    modules: ["@nuxt/eslint", "@nuxt/ui", "nuxt-maplibre"],
    // Runtime environment configuration
    runtimeConfig: {
        proxyURL: "http://localhost:8000",
        public: {
            apiBase: "/api",
        },
    },
    css: ["./app/assets/css/main.css"],
    vite: {
        plugins: [tailwindcss()],
    },
})
