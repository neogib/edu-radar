import type {
    WynikE8PublicWithPrzedmiot,
    WynikEMPublicWithPrzedmiot,
} from "~/types/schools"
import type { ExamSection } from "~/types/subjects"
import { buildExamSection } from "~/utils/examSections"

interface UseExamSectionsOptions {
    wynikiE8: MaybeRefOrGetter<WynikE8PublicWithPrzedmiot[]>
    wynikiEm: MaybeRefOrGetter<WynikEMPublicWithPrzedmiot[]>
}

export const useExamSections = (options: UseExamSectionsOptions) => {
    const examSections = computed(() => {
        const sections: ExamSection[] = []

        const wynikiE8 = toValue(options.wynikiE8)
        const wynikiEm = toValue(options.wynikiEm)

        if (wynikiE8.length) {
            sections.push(buildExamSection("e8", wynikiE8))
        }

        if (wynikiEm.length) {
            sections.push(buildExamSection("em", wynikiEm))
        }

        return sections
    })

    const hasExamResults = computed(() => examSections.value.length > 0)

    return {
        examSections,
        hasExamResults,
    }
}
