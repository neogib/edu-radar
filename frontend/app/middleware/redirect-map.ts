// middleware/map.ts
import { MAP_CONFIG } from "~/constants/mapConfig"

export default defineNuxtRouteMiddleware((to) => {
    // run only on entering /map
    if (to.path !== "/map" && to.path !== "/map/") return

    const hasViewport =
        typeof to.query.x === "string" &&
        typeof to.query.y === "string" &&
        typeof to.query.z === "string"

    if (hasViewport) return

    return navigateTo(
        {
            path: "/map",
            query: {
                x: MAP_CONFIG.defaultCenter[0].toFixed(6),
                y: MAP_CONFIG.defaultCenter[1].toFixed(6),
                z: MAP_CONFIG.defaultZoom.toFixed(2),
                ...to.query, // preserve filters if any
            },
        },
        { replace: true },
    )
})
