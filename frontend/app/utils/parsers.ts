export const parseArray = (v: unknown) => {
    if (!v) return undefined
    const arr = (Array.isArray(v) ? v : [v])
        .map(Number)
        .filter((n) => Number.isFinite(n) && n > 0)
        .sort((a, b) => a - b)
    return arr.length ? arr : undefined
}

export const parseNumber = (v: unknown) => {
    if (!v) return undefined
    const n = Number(Array.isArray(v) ? v[0] : v)
    return Number.isFinite(n) ? n : undefined
}

export const parseString = (v: unknown) => {
    if (!v) return undefined
    const s = String(Array.isArray(v) ? v[0] : v)
    return s.length >= 2 ? s : undefined
}
