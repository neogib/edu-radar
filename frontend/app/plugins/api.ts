export default defineNuxtPlugin(() => {
    const config = useRuntimeConfig()

    const api = $fetch.create({
        baseURL: config.public.apiBase,

        onRequest({ request }) {
            console.log("API request:", request)
        },

        onResponse({ response }) {
            console.log("API response:", response._data)
        },

        onResponseError({ response }) {
            console.error("API error:", response.status)
        },
    })

    return {
        provide: {
            api,
        },
    }
})
