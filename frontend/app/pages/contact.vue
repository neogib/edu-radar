<script setup lang="ts">
import type { FormSubmitEvent } from "@nuxt/ui"
import * as v from "valibot"

usePageSeo(
    "Kontakt - EduRadar",
    "Skontaktuj się z zespołem EduRadar w sprawie rankingu szkół i danych edukacyjnych.",
)

const schema = v.object({
    name: v.pipe(
        v.string("Imię i nazwisko jest wymagane."),
        v.nonEmpty("Imię i nazwisko jest wymagane."),
        v.maxLength(120, "Imię i nazwisko może mieć maksymalnie 120 znaków."),
    ),
    email: v.pipe(
        v.string("Adres e-mail jest wymagany."),
        v.nonEmpty("Adres e-mail jest wymagany."),
        v.email("Podaj poprawny adres e-mail."),
        v.maxLength(254, "Adres e-mail może mieć maksymalnie 254 znaki."),
    ),
    topic: v.pipe(
        v.string("Temat jest wymagany."),
        v.nonEmpty("Temat jest wymagany."),
        v.maxLength(150, "Temat może mieć maksymalnie 150 znaków."),
    ),
    message: v.pipe(
        v.string("Wiadomość jest wymagana."),
        v.nonEmpty("Wiadomość jest wymagana."),
        v.maxLength(2000, "Wiadomość może mieć maksymalnie 2000 znaków."),
    ),
})

type ContactFormSchema = v.InferOutput<typeof schema>

const state = reactive<ContactFormSchema>({
    name: "",
    email: "",
    topic: "",
    message: "",
})

type TurnstileWidgetRef = {
    reset: () => void
}

const turnstileToken = ref("")
const turnstileError = ref("")
const isSubmitting = ref(false)
const turnstileRef = useTemplateRef<TurnstileWidgetRef>("turnstileRef")

const { $api } = useNuxtApp()
const toast = useToast()

function notifyTurnstileError(description: string) {
    turnstileToken.value = ""
    turnstileError.value = description
    toast.add({
        title: "Błąd weryfikacji",
        description,
        color: "error",
        icon: "i-lucide-shield-alert",
    })
}

function handleTurnstileError(code?: string) {
    const suffix = code ? ` (kod: ${code})` : ""
    notifyTurnstileError(`Weryfikacja Turnstile nie powiodła się${suffix}.`)
}

function handleTurnstileExpired() {
    notifyTurnstileError("Weryfikacja wygasła. Spróbuj ponownie.")
}

function handleWindowError(event: ErrorEvent) {
    if (!event.message.includes("TurnstileError")) {
        return
    }
    notifyTurnstileError(
        "Wystąpił błąd skryptu Turnstile. Odśwież stronę i spróbuj ponownie.",
    )
}

const turnstileOptions = {
    size: "flexible",
    "error-callback": handleTurnstileError,
    "expired-callback": handleTurnstileExpired,
} satisfies Omit<Partial<Turnstile.RenderParameters>, "callback">

onMounted(() => {
    window.addEventListener("error", handleWindowError)
})

onBeforeUnmount(() => {
    window.removeEventListener("error", handleWindowError)
})

async function onSubmit(event: FormSubmitEvent<ContactFormSchema>) {
    if (!turnstileToken.value) {
        turnstileError.value = "Potwierdź weryfikację bezpieczeństwa."
        return
    }

    turnstileError.value = ""
    isSubmitting.value = true

    try {
        await $api("/contact", {
            method: "POST",
            body: {
                ...event.data,
                turnstileToken: turnstileToken.value,
            },
        })

        console.log("Contact form submitted:", event.data)
        state.name = ""
        state.email = ""
        state.topic = ""
        state.message = ""

        turnstileToken.value = ""
        turnstileRef.value?.reset()

        toast.add({
            title: "Wiadomość wysłana",
            description: "Dziękujemy! Skontaktujemy się z Tobą wkrótce.",
            color: "success",
            icon: "i-lucide-check-circle-2",
        })
    } catch {
        turnstileToken.value = ""
        turnstileRef.value?.reset()
        toast.add({
            title: "Nie udało się wysłać wiadomości",
            description:
                "Spróbuj ponownie za chwilę lub odśwież stronę, jeśli problem się powtarza.",
            color: "error",
            icon: "i-lucide-circle-alert",
        })
    } finally {
        isSubmitting.value = false
    }
}
</script>

<template>
    <div
        class="relative isolate min-h-[calc(100vh-12rem)] px-4 py-10 sm:px-6 lg:px-8 flex items-center justify-center overflow-hidden">
        <div
            class="pointer-events-none absolute -top-24 -left-24 h-72 w-72 rounded-full bg-primary/15 blur-3xl" />
        <div
            class="pointer-events-none absolute -bottom-24 -right-24 h-72 w-72 rounded-full bg-secondary/15 blur-3xl" />
        <div
            class="pointer-events-none absolute inset-0 bg-linear-to-br from-primary-500/10 via-transparent to-secondary-500/10" />

        <UCard
            class="relative w-full max-w-lg border border-default/70 bg-default/95 shadow-xl shadow-black/5 backdrop-blur transition-transform duration-300 hover:-translate-y-0.5">
            <template #header>
                <div class="space-y-3 text-center">
                    <div
                        class="mx-auto inline-flex items-center gap-2 rounded-full border border-default bg-elevated/70 px-3 py-1 text-xs text-toned">
                        <UIcon
                            name="i-lucide-sparkles"
                            class="size-3.5 text-primary" />
                        <span>Skontaktuj się z zespołem</span>
                    </div>
                    <p class="text-xs uppercase tracking-[0.2em] text-muted">
                        Kontakt
                    </p>
                    <h1
                        class="text-2xl font-semibold text-highlighted sm:text-3xl">
                        Napisz do nas
                    </h1>
                    <p class="text-sm text-toned">
                        Chętnie odpowiemy na pytania dotyczące szkół, danych i
                        rankingów.
                    </p>
                </div>
            </template>

            <UForm
                :schema="schema"
                :state="state"
                class="space-y-5"
                @submit="onSubmit">
                <UFormField label="Imię i nazwisko" name="name">
                    <UInput
                        v-model="state.name"
                        class="w-full"
                        size="lg"
                        :maxlength="120"
                        placeholder="Jan Kowalski" />
                </UFormField>

                <UFormField label="E-mail" name="email">
                    <UInput
                        v-model="state.email"
                        class="w-full"
                        size="lg"
                        type="email"
                        :maxlength="254"
                        placeholder="jan.kowalski@email.com" />
                </UFormField>

                <UFormField label="Temat" name="topic">
                    <UInput
                        v-model="state.topic"
                        class="w-full"
                        size="lg"
                        :maxlength="150"
                        placeholder="Współpraca / pytanie o dane" />
                </UFormField>

                <UFormField label="Wiadomość" name="message">
                    <UTextarea
                        v-model="state.message"
                        class="w-full"
                        size="lg"
                        :rows="6"
                        :maxlength="2000"
                        placeholder="Opisz, w czym możemy pomóc..." />
                </UFormField>

                <UFormField label="Weryfikacja bezpieczeństwa" name="turnstile">
                    <NuxtTurnstile
                        ref="turnstileRef"
                        v-model="turnstileToken"
                        :options="turnstileOptions"
                        @update:model-value="turnstileError = ''" />
                    <p v-if="turnstileError" class="mt-2 text-sm text-error">
                        {{ turnstileError }}
                    </p>
                </UFormField>

                <UButton
                    type="submit"
                    color="primary"
                    variant="solid"
                    block
                    :loading="isSubmitting"
                    :disabled="isSubmitting"
                    class="justify-center">
                    <UIcon name="i-lucide-send" class="size-4" />
                    Wyślij wiadomość
                </UButton>
            </UForm>
        </UCard>
    </div>
</template>
