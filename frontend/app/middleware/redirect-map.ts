// middleware/map.ts
import { MAP_CONFIG } from "~/constants/mapConfig"

export default defineNuxtRouteMiddleware((to) => {
    // run only on entering /map
    if (to.path !== "/map" && to.path !== "/map/") return

    const x = Number(to.query.x)
    const y = Number(to.query.y)
    const z = Number(to.query.z)

    const validX = !isNaN(x) && x >= -90 && x <= 90
    const validY = !isNaN(y) && y >= -180 && y <= 180
    const validZ =
        !isNaN(z) && z >= MAP_CONFIG.minZoom && z <= MAP_CONFIG.maxZoom

    if (validX && validY && validZ) {
        return // all good
    }

    return navigateTo(
        {
            path: "/map",
            query: {
                ...to.query, // preserve filters if any
                x: validX ? x : MAP_CONFIG.defaultCenter[0],
                y: validY ? y : MAP_CONFIG.defaultCenter[1],
                z: validZ ? z : MAP_CONFIG.defaultZoom,
            },
        },
        { replace: true },
    )
})
