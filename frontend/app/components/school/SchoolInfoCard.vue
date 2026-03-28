<script setup lang="ts">
import type { SchoolInfoItem, SchoolBadgeSection } from "~/types/schoolInfo"
import type { SzkolaPublicWithRelations } from "~/types/schools"
import {
    formatSchoolAddressLines,
    formatSchoolDate,
} from "~/utils/schoolFormat"

interface Props {
    school: SzkolaPublicWithRelations
}

const props = defineProps<Props>()

const directorFullName = computed(() =>
    `${props.school.dyrektorImie || ""} ${props.school.dyrektorNazwisko || ""}`.trim(),
)

const websiteHref = computed<string | null>(() => {
    const website = props.school.stronaInternetowa?.trim()
    if (!website) return null

    return website.startsWith("http://") || website.startsWith("https://")
        ? website
        : `https://${website}`
})

const schoolInfoItems = computed(() => {
    const addressLines = formatSchoolAddressLines(props.school)

    const rows: Array<SchoolInfoItem | null> = [
        props.school.liczbaUczniow !== null
            ? {
                  key: "students",
                  label: "Liczba uczniów",
                  icon: "i-mdi-account-group",
                  lines: [String(props.school.liczbaUczniow)],
              }
            : null,
        directorFullName.value
            ? {
                  key: "director",
                  label: "Dyrektor",
                  icon: "i-mdi-account-tie",
                  lines: [directorFullName.value],
              }
            : null,
        {
            key: "address",
            label: "Adres",
            icon: "i-mdi-map-marker",
            lines: addressLines.length ? addressLines : ["brak danych"],
        },
        props.school.telefon
            ? {
                  key: "phone",
                  label: "Telefon",
                  icon: "i-mdi-phone",
                  lines: [props.school.telefon],
              }
            : null,
        props.school.email
            ? {
                  key: "email",
                  label: "Email",
                  icon: "i-mdi-email",
                  lines: [props.school.email],
                  href: `mailto:${props.school.email}`,
              }
            : null,
        props.school.stronaInternetowa && websiteHref.value
            ? {
                  key: "website",
                  label: "Strona internetowa",
                  icon: "i-mdi-web",
                  lines: [props.school.stronaInternetowa],
                  href: websiteHref.value,
                  external: true,
              }
            : null,
        props.school.dataZalozenia
            ? {
                  key: "foundation-date",
                  label: "Data założenia placówki",
                  icon: "i-mdi-calendar-start",
                  lines: [formatSchoolDate(props.school.dataZalozenia)],
              }
            : null,
        props.school.dataRozpoczecia
            ? {
                  key: "start-date",
                  label: "Data rozpoczęcia działalności",
                  icon: "i-mdi-calendar-check",
                  lines: [formatSchoolDate(props.school.dataRozpoczecia)],
              }
            : null,
        props.school.dataLikwidacji
            ? {
                  key: "liquidation-date",
                  label: "Data likwidacji placówki",
                  icon: "i-mdi-calendar-remove",
                  lines: [formatSchoolDate(props.school.dataLikwidacji)],
              }
            : null,
    ]

    return rows.filter((item): item is SchoolInfoItem => item !== null)
})

const schoolBadgeSections = computed(() =>
    [
        props.school.etapyEdukacji.length
            ? {
                  key: "stages",
                  label: "Etapy edukacji",
                  icon: "i-mdi-book-open-variant",
                  color: "primary" as const,
                  items: props.school.etapyEdukacji,
              }
            : null,
        props.school.ksztalcenieZawodowe.length
            ? {
                  key: "professional",
                  label: "Kształcenie zawodowe",
                  icon: "i-mdi-briefcase-variant",
                  color: "secondary" as const,
                  items: props.school.ksztalcenieZawodowe,
              }
            : null,
    ].filter((section): section is SchoolBadgeSection => section !== null),
)

const identifierItems = computed(() =>
    [
        { label: "RSPO", value: String(props.school.numerRspo) },
        { label: "REGON", value: props.school.regon },
        { label: "NIP", value: props.school.nip },
    ].filter((item) => item.value !== null && item.value !== undefined),
)
</script>

<template>
    <UCard :ui="{ body: 'space-y-4' }">
        <template #header>
            <div class="flex items-center gap-2">
                <UIcon
                    name="i-mdi-school-outline"
                    class="size-4 text-primary" />
                <h4 class="text-sm font-semibold text-highlighted">
                    Informacje o placówce
                </h4>
            </div>
        </template>

        <ul class="space-y-3">
            <li
                v-for="item in schoolInfoItems"
                :key="item.key"
                class="grid grid-cols-[1rem_1fr] items-start gap-3">
                <UIcon :name="item.icon" class="mt-0.5 size-4 text-dimmed" />
                <div class="min-w-0">
                    <p class="text-xs text-muted">
                        {{ item.label }}
                    </p>
                    <a
                        v-if="item.href"
                        :href="item.href"
                        :target="item.external ? '_blank' : undefined"
                        :rel="item.external ? 'noopener noreferrer' : undefined"
                        class="break-all text-sm text-primary hover:text-secondary">
                        {{ item.lines[0] }}
                    </a>
                    <template v-else>
                        <p
                            v-for="line in item.lines"
                            :key="`${item.key}-${line}`"
                            class="text-sm text-highlighted">
                            {{ line }}
                        </p>
                    </template>
                </div>
            </li>
        </ul>

        <div
            v-for="section in schoolBadgeSections"
            :key="section.key"
            class="space-y-2">
            <USeparator :label="section.label" :icon="section.icon" />
            <div class="flex flex-wrap gap-1.5">
                <UBadge
                    v-for="badge in section.items"
                    :key="badge.id"
                    :color="section.color"
                    variant="soft"
                    class="max-w-full whitespace-normal py-1 text-center">
                    {{ badge.nazwa }}
                </UBadge>
            </div>
        </div>

        <div v-if="identifierItems.length" class="space-y-2">
            <USeparator
                label="Identyfikatory"
                icon="i-mdi-card-account-details-outline" />
            <dl class="space-y-1.5 text-xs">
                <div
                    v-for="identifier in identifierItems"
                    :key="identifier.label"
                    class="flex items-center justify-between gap-3">
                    <dt class="text-muted">{{ identifier.label }}:</dt>
                    <dd class="font-mono text-default">
                        {{ identifier.value }}
                    </dd>
                </div>
            </dl>
        </div>
    </UCard>
</template>
