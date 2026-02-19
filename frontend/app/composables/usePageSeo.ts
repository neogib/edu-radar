export function usePageSeo(title: string, description: string) {
    useSeoMeta({
        title,
        ogTitle: title,
        description,
        ogDescription: description,
    })
}
