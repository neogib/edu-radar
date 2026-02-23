import tailwindcss from "@tailwindcss/vite"

const isDev = process.env.NODE_ENV === "development"
const siteUrl = process.env.NUXT_SITE_URL ?? "https://eduradar.4one.ovh"
const siteName = process.env.NUXT_SITE_NAME ?? "EduRadar"

// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
    compatibilityDate: "2025-07-15",
    devtools: { enabled: true },
    modules: [
        "@nuxt/eslint",
        "@nuxt/ui",
        "nuxt-maplibre",
        "nuxt-charts",
        "@nuxt/scripts",
        "@nuxtjs/turnstile",
        "nuxt-security",
        "@nuxtjs/seo",
    ],
    turnstile: {
        siteKey: "your_site_key", // replace with your actual site key or just set NUXT_PUBLIC_TURNSTILE_SITE_KEY in .env
    },
    site: {
        url: siteUrl,
        name: siteName,
        indexable: !isDev,
    },
    ogImage: {
        enabled: false,
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
    security: {
        headers: {
            strictTransportSecurity: false,
            contentSecurityPolicy: false,
            crossOriginEmbedderPolicy: false,
            crossOriginOpenerPolicy: false,
            crossOriginResourcePolicy: false,
            originAgentCluster: false,
            xFrameOptions: "SAMEORIGIN",
            xContentTypeOptions: "nosniff",
            referrerPolicy: "no-referrer-when-downgrade",
        },
    },
    routeRules: {
        "/og-image.jpg": {
            cors: true,
            security: {
                headers: {
                    xFrameOptions: false,
                },
            },
        },
    },
    app: {
        head: {
            title: siteName,
            titleTemplate: "%s %separator %siteName",
            link: [
                { rel: "icon", type: "image/svg+xml", href: "/favicon.svg" },
            ],
        },
    },
})
