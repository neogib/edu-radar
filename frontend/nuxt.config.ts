import tailwindcss from "@tailwindcss/vite"

const isDev = process.env.NODE_ENV === "development"

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
            strictTransportSecurity: isDev
                ? false
                : {
                      maxAge: 15_552_000,
                      includeSubdomains: true,
                  },
            crossOriginEmbedderPolicy: isDev ? "unsafe-none" : "require-corp",
            contentSecurityPolicy: isDev
                ? {
                      "upgrade-insecure-requests": false,
                      "script-src": [
                          "'self'",
                          "'unsafe-inline'",
                          "'unsafe-eval'",
                          "http:",
                          "https:",
                      ],
                      "style-src": ["'self'", "'unsafe-inline'", "https:"],
                      "connect-src": [
                          "'self'",
                          "http:",
                          "https:",
                          "ws:",
                          "wss:",
                      ],
                  }
                : {
                      "script-src": [
                          "'self'",
                          "https:",
                          "'unsafe-inline'",
                          "'strict-dynamic'",
                          "'nonce-{{nonce}}'",
                      ],
                      "style-src": ["'self'", "https:", "'unsafe-inline'"],
                      "img-src": ["'self'", "data:", "blob:"],
                      "font-src": ["'self'", "https:", "data:"],
                      "object-src": ["'none'"],
                      "base-uri": ["'none'"],
                      "script-src-attr": ["'none'"],
                      "upgrade-insecure-requests": true,
                  },
        },
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
