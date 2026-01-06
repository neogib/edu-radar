import { joinURL } from "ufo"

export default defineEventHandler(async (event) => {
    // Get the runtime config value for apiBase
    const proxyUrl = useRuntimeConfig().proxyURL
    // Construct the target URL by removing the /api/ prefix
    // /api/schools -> schools
    const path = event.path.replace(/^\/api\//, "")
    console.log("Proxying request to:", joinURL(proxyUrl, path))
    const target = joinURL(proxyUrl, path)

    return proxyRequest(event, target)
})
