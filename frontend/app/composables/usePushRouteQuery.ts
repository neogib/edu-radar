import { useRouteQuery } from "@vueuse/router"
import type { MaybeRefOrGetter } from "vue"
import type { RouteParamValueRaw } from "vue-router"

type QueryValue = RouteParamValueRaw | string[]

export const usePushRouteQuery = <T extends QueryValue = QueryValue, K = T>(
    name: string,
    defaultValue?: MaybeRefOrGetter<T>,
    options?: Parameters<typeof useRouteQuery<T, K>>[2],
) =>
    useRouteQuery<T, K>(name, defaultValue, {
        mode: "push",
        ...options,
    })
