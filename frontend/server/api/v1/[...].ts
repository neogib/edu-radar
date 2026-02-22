import { joinURL } from "ufo"

export default defineEventHandler(async (event) => {
    // Get the runtime config value for apiBase
    const proxyUrl = useRuntimeConfig().proxyURL

    // Construct the target URL by removing the /api/v1/ prefix
    // /api/v1/schools -> schools
    const path = event.path.replace(/^\/api\/v1\//, "")
    console.log("Proxying request to:", joinURL(proxyUrl, path))
    const target = joinURL(proxyUrl, path)

    return proxyRequest(event, target)
})
