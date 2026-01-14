export const useSchoolFiltersFromRoute = () => {
    const route = useRoute()

    const filters = computed(() => {
        const q = route.query

        const parseArray = (v: string | string[] | undefined) => {
            if (!v) return undefined
            const arr = Array.isArray(v) ? v : [v]
            const nums = arr
                .map(Number)
                .filter((n) => Number.isFinite(n) && n > 0)
            return nums.length ? nums : undefined
        }

        const parseNumber = (v: string | string[] | undefined) => {
            if (!v || Array.isArray(v)) return undefined
            const n = Number(v)
            return Number.isFinite(n) ? n : undefined
        }

        return {
            type: parseArray(q.type as string | string[] | undefined),
            status: parseArray(q.status as string | string[] | undefined),
            category: parseArray(q.category as string | string[] | undefined),
            vocational_training: parseArray(
                q.vocational_training as string | string[] | undefined,
            ),
            min_score: parseNumber(q.min_score as string | undefined),
            max_score: parseNumber(q.max_score as string | undefined),
        }
    })

    return { filters }
}
