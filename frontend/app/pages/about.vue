<script setup lang="ts">
useSeoMeta({
    title: "O nas",
    description:
        "Dowiedz się, czym jest EduRadar i jak pomagamy rodzicom oraz uczniom porównywać szkoły w Polsce.",
})

/* ───── scroll-reveal observer ───── */
let observer: IntersectionObserver | null = null
let statsObserver: IntersectionObserver | null = null

onMounted(async () => {
    await nextTick()
    observer = new IntersectionObserver(
        (entries) => {
            entries.forEach((entry) => {
                if (entry.isIntersecting) {
                    entry.target.classList.add("revealed")
                    observer?.unobserve(entry.target)
                }
            })
        },
        { threshold: 0.12, rootMargin: "0px 0px -60px 0px" },
    )
    document
        .querySelectorAll("[data-reveal]")
        .forEach((el) => observer?.observe(el))
    const el = document.getElementById("stats-section")
    if (el) {
        statsObserver = new IntersectionObserver(
            (entries) => {
                const [entry] = entries
                if (entry?.isIntersecting) runCounters()
            },
            { threshold: 0.3 },
        )
        statsObserver.observe(el)
    }
})
onUnmounted(() => {
    observer?.disconnect()
    statsObserver?.disconnect()
})

/* ───── animated counters ───── */
const stats = ref([
    {
        value: 0,
        target: 50000,
        suffix: "+",
        label: "Placówek w bazie",
        icon: "i-mdi-school",
    },
    {
        value: 0,
        target: 16,
        suffix: "",
        label: "Województw",
        icon: "i-mdi-map",
    },
    {
        value: 0,
        target: 3,
        suffix: "",
        label: "Kroki do znalezienia szkoły",
        icon: "i-mdi-rocket-launch",
    },
])
const statsTriggered = ref(false)

function runCounters() {
    if (statsTriggered.value) return
    statsTriggered.value = true
    stats.value.forEach((s) => {
        const dur = 2000
        const steps = 70
        const inc = s.target / steps
        let cur = 0
        const t = setInterval(() => {
            cur += inc
            if (cur >= s.target) {
                s.value = s.target
                clearInterval(t)
            } else {
                s.value = Math.floor(cur)
            }
        }, dur / steps)
    })
}

/* ───── data ───── */
const highlights = [
    {
        icon: "i-mdi-map-marker-radius",
        title: "Interaktywna mapa",
        description: "Przeglądaj szkoły na interaktywnej mapie Polski.",
        gradient: "from-blue-500/20 to-cyan-500/20",
        iconColor: "text-blue-500",
    },
    {
        icon: "i-mdi-chart-line",
        title: "Rzetelne rankingi",
        description:
            "Łączymy dane egzaminacyjne, prezentując wyniki w przejrzystej skali 0–100.",
        gradient: "from-emerald-500/20 to-teal-500/20",
        iconColor: "text-emerald-500",
    },
    {
        icon: "i-mdi-database-check",
        title: "Oficjalne źródła",
        description:
            "Bazujemy wyłącznie na publicznych i regularnie aktualizowanych danych edukacyjnych.",
        gradient: "from-violet-500/20 to-purple-500/20",
        iconColor: "text-violet-500",
    },
    {
        icon: "i-mdi-compare",
        title: "Porównywanie szkół",
        description:
            "Analizuj wyniki poszczególnych szkół i wybierz najlepszą opcję.",
        gradient: "from-amber-500/20 to-orange-500/20",
        iconColor: "text-amber-500",
    },
    {
        icon: "i-mdi-filter-variant",
        title: "Zaawansowane filtry",
        description:
            "Filtruj po rodzaju szkoły, etapie edukacji i wynikach egzaminów.",
        gradient: "from-rose-500/20 to-pink-500/20",
        iconColor: "text-rose-500",
    },
    {
        icon: "i-mdi-cellphone",
        title: "Działa wszędzie",
        description:
            "Responsywna aplikacja — działa równie dobrze na komputerze, tablecie i telefonie.",
        gradient: "from-cyan-500/20 to-sky-500/20",
        iconColor: "text-cyan-500",
    },
] as const

const steps = [
    {
        num: "01",
        icon: "i-mdi-map-marker-plus",
        title: "Wybierz lokalizację",
        desc: "Wskaż interesujący Cię region na mapie lub wpisz nazwę miejscowości.",
    },
    {
        num: "02",
        icon: "i-mdi-magnify",
        title: "Przeglądaj szkoły",
        desc: "Zobacz listę placówek w okolicy wraz z ich wynikami i pozycją w rankingu.",
    },
    {
        num: "03",
        icon: "i-mdi-check-decagram",
        title: "Porównaj i wybierz",
        desc: "Zestawiaj szkoły, analizuj dane i podejmij świadomą decyzję.",
    },
] as const

const values = [
    {
        icon: "i-mdi-shield-check",
        title: "Transparentność",
        desc: "Dane publiczne, metodologia jawna.",
    },
    {
        icon: "i-mdi-account-group",
        title: "Dostępność",
        desc: "Darmowa platforma dla każdego.",
    },
    {
        icon: "i-mdi-lightbulb-on",
        title: "Innowacyjność",
        desc: "Ciągły rozwój i nowe funkcje.",
    },
    {
        icon: "i-mdi-heart",
        title: "Pasja do edukacji",
        desc: "Wierzymy w siłę rzetelnych danych.",
    },
] as const

const faq = [
    {
        label: "Skąd pochodzą dane w EduRadar?",
        content:
            "Korzystamy z publicznych źródeł: wyników egzaminów ósmoklasisty i matur (OKE) oraz danych z Systemu Informacji Oświatowej (SIO). Bazę aktualizujemy po każdej sesji egzaminacyjnej.",
    },
    {
        label: "Czy EduRadar jest bezpłatny?",
        content: "Tak — EduRadar jest i pozostanie darmowy.",
    },
    {
        label: "Jak często aktualizowane są rankingi?",
        content:
            "Rankingi odświeżamy co najmniej raz w roku, po publikacji nowych wyników egzaminacyjnych przez Okręgowe Komisje Egzaminacyjne.",
    },
    {
        label: "Jak obliczany jest wynik szkoły?",
        slot: "scoring-system",
    },
    {
        label: "Czy mogę zasugerować nową funkcję?",
        content:
            "Oczywiście! Jesteśmy otwarci na feedback — napisz do nas przez formularz kontaktowy lub media społecznościowe.",
    },
]
</script>

<template>
    <div class="space-y-0 overflow-hidden">
        <!-- ============ HERO ============ -->
        <section
            class="relative isolate px-4 pt-20 pb-24 sm:pt-28 sm:pb-32 text-center overflow-hidden">
            <div class="pointer-events-none absolute inset-0 -z-20">
                <NuxtImg
                    src="/images/hero-image.png"
                    alt="Hero image of students and parents exploring school data on a large interactive map, surrounded by educational icons and charts"
                    sizes="sm:100vw md:100vw lg:100vw xl:100vw 2xl:100vw"
                    :width="1536"
                    :height="1024"
                    preload
                    class="h-full w-full object-cover"
                    aria-hidden="true" />
            </div>
            <div
                class="pointer-events-none absolute inset-0 -z-10 bg-black/45" />
            <div
                class="pointer-events-none absolute inset-0 -z-10 bg-linear-to-b from-white/70 via-white/50 to-white/20 dark:from-black/35 dark:via-black/45 dark:to-black/55" />

            <div class="mx-auto max-w-3xl space-y-6" data-reveal>
                <UBadge
                    size="lg"
                    class="animate-fade-down bg-white/90 text-gray-900 ring-1 ring-white/60 backdrop-blur-sm dark:bg-gray-900/80 dark:text-gray-100 dark:ring-white/20">
                    <UIcon name="i-mdi-radar" class="mr-1 size-4" />
                    Poznaj EduRadar
                </UBadge>

                <h1
                    class="text-4xl sm:text-5xl lg:text-6xl font-extrabold tracking-tight text-primary animate-fade-up">
                    Świadome decyzje edukacyjne
                </h1>

                <p
                    class="mx-auto max-w-2xl text-lg sm:text-xl text-gray-800 dark:text-white/90 leading-relaxed animate-fade-up animation-delay-200">
                    Pomagamy rodzicom i uczniom porównywać szkoły w całej Polsce
                    dzięki czytelnym danym, rankingom i interaktywnej mapie.
                </p>

                <div
                    class="flex flex-wrap justify-center gap-3 pt-2 animate-fade-up animation-delay-400">
                    <UButton
                        to="/map"
                        size="lg"
                        icon="i-mdi-map-search"
                        label="Przeglądaj mapę" />
                    <UButton
                        to="/ranking"
                        size="lg"
                        color="neutral"
                        variant="soft"
                        icon="i-mdi-trophy-outline"
                        label="Zobacz ranking" />
                </div>
            </div>
        </section>

        <!-- ============ STATS ============ -->
        <section
            id="stats-section"
            class="relative bg-primary/3 border-y border-primary/10">
            <div
                class="mx-auto max-w-4xl px-4 py-14 grid gap-8 text-center sm:grid-cols-3">
                <div
                    v-for="(s, i) in stats"
                    :key="s.label"
                    data-reveal
                    :style="{ transitionDelay: `${i * 100}ms` }"
                    class="space-y-2">
                    <UIcon
                        :name="s.icon"
                        class="mx-auto size-7 text-primary/70" />
                    <p
                        class="text-3xl sm:text-4xl font-bold text-primary tabular-nums">
                        {{ s.value.toLocaleString("pl-PL") }}{{ s.suffix }}
                    </p>
                    <p class="text-sm text-muted">{{ s.label }}</p>
                </div>
            </div>
        </section>

        <!-- ============ FEATURES ============ -->
        <section class="mx-auto max-w-7xl px-4 py-20 space-y-12">
            <div class="text-center space-y-3" data-reveal>
                <h2 class="text-3xl font-bold tracking-tight">
                    Co oferuje EduRadar?
                </h2>
                <p class="text-muted max-w-xl mx-auto">
                    Zestaw narzędzi, które pomagają szybko i wygodnie znaleźć
                    najlepszą szkołę.
                </p>
            </div>

            <div class="grid gap-5 sm:grid-cols-2 lg:grid-cols-3">
                <UCard
                    v-for="(item, i) in highlights"
                    :key="item.title"
                    data-reveal
                    :style="{ transitionDelay: `${i * 80}ms` }"
                    class="group hover:shadow-lg hover:-translate-y-1 transition-all duration-300"
                    :ui="{ body: 'space-y-4 p-5 sm:p-6' }">
                    <div
                        :class="[
                            'inline-flex items-center justify-center rounded-xl p-3 bg-linear-to-br transition-transform duration-300 group-hover:scale-110',
                            item.gradient,
                        ]">
                        <UIcon
                            :name="item.icon"
                            :class="['size-6', item.iconColor]" />
                    </div>
                    <h3 class="font-semibold text-lg">{{ item.title }}</h3>
                    <p class="text-sm text-muted leading-relaxed">
                        {{ item.description }}
                    </p>
                </UCard>
            </div>
        </section>

        <!-- ============ HOW IT WORKS ============ -->
        <section class="bg-primary/3 border-y border-primary/10">
            <div class="mx-auto max-w-5xl px-4 py-20 space-y-14">
                <div class="text-center space-y-3" data-reveal>
                    <h2 class="text-3xl font-bold tracking-tight">
                        Jak to działa?
                    </h2>
                    <p class="text-muted max-w-lg mx-auto">
                        Trzy proste kroki dzielą Cię od świadomego wyboru
                        szkoły.
                    </p>
                </div>

                <div class="relative grid gap-10 md:grid-cols-3">
                    <!-- connector line (desktop) -->
                    <div
                        class="hidden md:block absolute top-12 left-[16.5%] right-[16.5%] h-0.5 bg-linear-to-r from-primary/30 via-primary/50 to-primary/30 rounded-full" />

                    <div
                        v-for="(step, i) in steps"
                        :key="step.num"
                        data-reveal
                        :style="{ transitionDelay: `${i * 150}ms` }"
                        class="relative flex flex-col items-center text-center space-y-4">
                        <!-- circle -->
                        <div
                            class="relative z-10 flex items-center justify-center size-24 rounded-full bg-linear-to-br from-primary/15 to-primary/5 ring-2 ring-primary/20 shadow-lg shadow-primary/10 group">
                            <UIcon
                                :name="step.icon"
                                class="size-10 text-primary" />
                            <span
                                class="absolute -top-1 -right-1 flex items-center justify-center size-7 rounded-full bg-primary text-primary-foreground text-xs font-bold shadow">
                                {{ step.num }}
                            </span>
                        </div>
                        <h3 class="font-semibold text-lg">{{ step.title }}</h3>
                        <p class="text-sm text-muted max-w-xs leading-relaxed">
                            {{ step.desc }}
                        </p>
                    </div>
                </div>
            </div>
        </section>

        <!-- ============ MISSION ============ -->
        <section class="mx-auto max-w-7xl px-4 py-20">
            <div class="grid gap-10 lg:grid-cols-2 items-center" data-reveal>
                <!-- text -->
                <div class="space-y-6">
                    <UBadge color="primary" variant="subtle">
                        <UIcon
                            name="i-mdi-bullseye-arrow"
                            class="mr-1 size-4" />
                        Nasza misja
                    </UBadge>
                    <h2 class="text-3xl font-bold tracking-tight">
                        Upraszczamy dostęp do danych o szkołach
                    </h2>
                    <p class="text-muted leading-relaxed">
                        Wierzymy, że każdy rodzic i uczeń zasługuje na
                        przejrzysty dostęp do informacji o szkołach. EduRadar
                        łączy dane z wielu publicznych źródeł i prezentuje je w
                        jednym miejscu — prosto, czytelnie i bez ukrytych
                        kosztów.
                    </p>
                    <p class="text-muted leading-relaxed">
                        Nie zastępujemy dni otwartych ani rozmów z
                        nauczycielami. Dajemy solidną bazę danych, od której
                        warto zacząć poszukiwania.
                    </p>

                    <div class="flex flex-wrap gap-3 pt-2">
                        <UButton
                            to="/map"
                            icon="i-mdi-map-search"
                            label="Przejdź do mapy" />
                        <UButton
                            to="/ranking"
                            color="neutral"
                            variant="outline"
                            icon="i-mdi-trophy-outline"
                            label="Zobacz ranking" />
                    </div>
                </div>

                <!-- values grid -->
                <div class="grid grid-cols-2 gap-4">
                    <UCard
                        v-for="(v, i) in values"
                        :key="v.title"
                        data-reveal
                        :style="{ transitionDelay: `${i * 100}ms` }"
                        class="group hover:shadow-md hover:-translate-y-0.5 transition-all duration-300"
                        :ui="{ body: 'p-4 space-y-2' }">
                        <div
                            class="inline-flex items-center justify-center rounded-lg p-2 bg-primary/10 transition-transform duration-300 group-hover:scale-110">
                            <UIcon :name="v.icon" class="size-5 text-primary" />
                        </div>
                        <h3 class="font-semibold text-sm">{{ v.title }}</h3>
                        <p class="text-xs text-muted leading-relaxed">
                            {{ v.desc }}
                        </p>
                    </UCard>
                </div>
            </div>
        </section>

        <!-- ============ FAQ ============ -->
        <section class="bg-primary/3 border-y border-primary/10">
            <div class="mx-auto max-w-3xl px-4 py-20 space-y-10">
                <div class="text-center space-y-3" data-reveal>
                    <h2 class="text-3xl font-bold tracking-tight">
                        Często zadawane pytania
                    </h2>
                    <p class="text-muted">
                        Odpowiedzi na najczęstsze pytania o platformę.
                    </p>
                </div>

                <div class="space-y-3" data-reveal>
                    <UAccordion :items="faq">
                        <template #scoring-system-body>
                            <div
                                class="space-y-2 text-sm text-muted leading-relaxed">
                                <p>
                                    <strong
                                        >Wynik szkoły jest normalizowany do
                                        skali 0–100</strong
                                    >.
                                </p>
                                <p>
                                    Bazuje na
                                    <strong>ważonej medianie</strong> wyników z
                                    trzech przedmiotów:
                                </p>
                                <p>
                                    <strong>matematyka (50%)</strong>,
                                    <strong>język polski (25%)</strong>,
                                    <strong>język angielski (25%)</strong>.
                                </p>
                                <p>
                                    Mediany są ważone liczbą zdających, a
                                    starsze lata mają mniejszy wpływ przez
                                    <strong>zanik czasowy</strong>.
                                </p>
                                <UButton
                                    to="https://github.com/neogib/edu-radar/wiki/Scoring-System"
                                    target="_blank"
                                    rel="noopener noreferrer"
                                    variant="link"
                                    size="xs"
                                    trailing-icon="i-mdi-open-in-new"
                                    class="px-0">
                                    Czytaj więcej
                                </UButton>
                            </div>
                        </template>
                    </UAccordion>
                </div>
            </div>
        </section>

        <!-- ============ CTA ============ -->
        <section class="relative isolate overflow-hidden">
            <div
                class="pointer-events-none absolute inset-0 -z-10 bg-linear-to-t from-primary/8 to-transparent" />
            <div
                class="mx-auto max-w-3xl px-4 py-24 text-center space-y-6"
                data-reveal>
                <h2 class="text-3xl sm:text-4xl font-bold tracking-tight">
                    Gotowy, aby znaleźć idealną szkołę?
                </h2>
                <p class="text-muted max-w-xl mx-auto text-lg leading-relaxed">
                    Dołącz do tysięcy rodziców i uczniów, którzy korzystają z
                    EduRadar, aby podejmować lepsze decyzje edukacyjne.
                </p>
                <div class="flex flex-wrap justify-center gap-3 pt-2">
                    <UButton
                        to="/map"
                        size="xl"
                        icon="i-mdi-rocket-launch"
                        label="Zacznij teraz" />
                    <UButton
                        to="/ranking"
                        size="xl"
                        color="neutral"
                        variant="outline"
                        icon="i-mdi-format-list-numbered"
                        label="Sprawdź ranking" />
                </div>
            </div>
        </section>
    </div>
</template>

<style scoped>
/* ───── scroll-reveal ───── */
[data-reveal] {
    opacity: 0;
    transform: translateY(28px);
    transition:
        opacity 0.6s cubic-bezier(0.16, 1, 0.3, 1),
        transform 0.6s cubic-bezier(0.16, 1, 0.3, 1);
}
[data-reveal].revealed {
    opacity: 1;
    transform: translateY(0);
}

/* ───── entrance animations ───── */
.animate-fade-up {
    animation: fadeUp 0.7s cubic-bezier(0.16, 1, 0.3, 1) both;
}
.animate-fade-down {
    animation: fadeDown 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
}
.animation-delay-200 {
    animation-delay: 0.2s;
}
.animation-delay-400 {
    animation-delay: 0.4s;
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(24px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
@keyframes fadeDown {
    from {
        opacity: 0;
        transform: translateY(-12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}
</style>
