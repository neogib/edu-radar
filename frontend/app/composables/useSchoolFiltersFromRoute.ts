export const useSchoolFiltersFromRoute = () => {
    const route = useRoute()

    // granular computeds to prevent re-evaluation of the main filter object
    // when unrelated query params (like bbox) change
    const typeParam = computed(() => route.query.type)
    const statusParam = computed(() => route.query.status)
    const categoryParam = computed(() => route.query.category)
    const vocationalParam = computed(() => route.query.vocational_training)
    const minScoreParam = computed(() => route.query.min_score)
    const maxScoreParam = computed(() => route.query.max_score)
    const qParam = computed(() => route.query.search || route.query.q)

    const parseArray = (v: unknown) => {
        if (!v) return undefined
        const arr = (Array.isArray(v) ? v : [v])
            .map(Number)
            .filter((n) => Number.isFinite(n) && n > 0)
            .sort((a, b) => a - b)
        return arr.length ? arr : undefined
    }

    const parseNumber = (v: unknown) => {
        if (!v) return undefined
        const n = Number(Array.isArray(v) ? v[0] : v)
        return Number.isFinite(n) ? n : undefined
    }

    const parseString = (v: unknown) => {
        if (!v) return undefined
        const s = String(Array.isArray(v) ? v[0] : v)
        return s.length >= 2 ? s : undefined
    }

    const filters = computed(() => {
        return {
            type: parseArray(typeParam.value),
            status: parseArray(statusParam.value),
            category: parseArray(categoryParam.value),
            vocational_training: parseArray(vocationalParam.value),
            min_score: parseNumber(minScoreParam.value),
            max_score: parseNumber(maxScoreParam.value),
            q: parseString(qParam.value),
        }
    })

    return { filters }
}
