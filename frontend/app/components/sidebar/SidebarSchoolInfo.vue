<script setup lang="ts">
import type { SchoolInfoItem, SchoolBadgeSection } from "~/types/schoolInfo"
import type { SzkolaPublicWithRelations } from "~/types/schools"

interface Props {
    selectedPoint: SzkolaPublicWithRelations
}

const props = defineProps<Props>()

const formatAddress = (school: SzkolaPublicWithRelations) => {
    const address = []
    const partsLine1 = []
    if (school.ulica?.nazwa) partsLine1.push(school.ulica.nazwa)
    if (school.numer_budynku) partsLine1.push(school.numer_budynku)
    if (school.numer_lokalu) partsLine1.push(`lok. ${school.numer_lokalu}`)

    if (partsLine1.length) address.push(partsLine1.join(" "))
    address.push(`${school.kod_pocztowy} ${school.miejscowosc.nazwa}`)

    return address
}

const directorFullName = computed(() =>
    `${props.selectedPoint.dyrektor_imie || ""} ${props.selectedPoint.dyrektor_nazwisko || ""}`.trim(),
)

const websiteHref = computed<string | null>(() => {
    const website = props.selectedPoint.strona_internetowa?.trim()
    if (!website) return null

    return website.startsWith("http://") || website.startsWith("https://")
        ? website
        : `https://${website}`
})

const schoolInfoItems = computed(() => {
    const rows: Array<SchoolInfoItem | null> = [
        props.selectedPoint.liczba_uczniow !== null
            ? {
                  key: "students",
                  label: "Liczba uczniów",
                  icon: "i-mdi-account-group",
                  lines: [String(props.selectedPoint.liczba_uczniow)],
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
            lines: formatAddress(props.selectedPoint),
        },
        props.selectedPoint.telefon
            ? {
                  key: "phone",
                  label: "Telefon",
                  icon: "i-mdi-phone",
                  lines: [props.selectedPoint.telefon],
              }
            : null,
        props.selectedPoint.email
            ? {
                  key: "email",
                  label: "Email",
                  icon: "i-mdi-email",
                  lines: [props.selectedPoint.email],
                  href: `mailto:${props.selectedPoint.email}`,
              }
            : null,
        props.selectedPoint.strona_internetowa && websiteHref.value
            ? {
                  key: "website",
                  label: "Strona internetowa",
                  icon: "i-mdi-web",
                  lines: [props.selectedPoint.strona_internetowa],
                  href: websiteHref.value,
                  external: true,
              }
            : null,
    ]

    return rows.filter((item): item is SchoolInfoItem => item !== null)
})

const schoolBadgeSections = computed(() =>
    [
        props.selectedPoint.etapy_edukacji.length
            ? {
                  key: "stages",
                  label: "Etapy edukacji",
                  icon: "i-mdi-book-open-variant",
                  color: "primary" as const,
                  items: props.selectedPoint.etapy_edukacji,
              }
            : null,
        props.selectedPoint.ksztalcenie_zawodowe.length
            ? {
                  key: "professional",
                  label: "Kształcenie zawodowe",
                  icon: "i-mdi-briefcase-variant",
                  color: "secondary" as const,
                  items: props.selectedPoint.ksztalcenie_zawodowe,
              }
            : null,
    ].filter((section): section is SchoolBadgeSection => section !== null),
)

const identifierItems = computed(() =>
    [
        { label: "RSPO", value: String(props.selectedPoint.numer_rspo) },
        { label: "REGON", value: props.selectedPoint.regon },
        { label: "NIP", value: props.selectedPoint.nip },
    ].filter((item) => item.value !== null && item.value !== undefined),
)
</script>
<template>
    <div class="border-b p-4">
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
                    <UIcon
                        :name="item.icon"
                        class="mt-0.5 size-4 text-dimmed" />
                    <div class="min-w-0">
                        <p class="text-xs text-muted">
                            {{ item.label }}
                        </p>
                        <a
                            v-if="item.href"
                            :href="item.href"
                            :target="item.external ? '_blank' : undefined"
                            :rel="
                                item.external
                                    ? 'noopener noreferrer'
                                    : undefined
                            "
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
    </div>
</template>
