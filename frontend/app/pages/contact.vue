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
    ),
    email: v.pipe(
        v.string("Adres e-mail jest wymagany."),
        v.nonEmpty("Adres e-mail jest wymagany."),
        v.email("Podaj poprawny adres e-mail."),
    ),
    topic: v.pipe(
        v.string("Temat jest wymagany."),
        v.nonEmpty("Temat jest wymagany."),
    ),
    message: v.pipe(
        v.string("Wiadomość jest wymagana."),
        v.nonEmpty("Wiadomość jest wymagana."),
    ),
})

type ContactFormSchema = v.InferOutput<typeof schema>

const state = reactive<ContactFormSchema>({
    name: "",
    email: "",
    topic: "",
    message: "",
})

const toast = useToast()

async function onSubmit(event: FormSubmitEvent<ContactFormSchema>) {
    console.log("Contact form submitted:", event.data)
    toast.add({
        title: "Wiadomość wysłana",
        description: "Dziękujemy! Skontaktujemy się z Tobą wkrótce.",
        color: "success",
        icon: "i-lucide-check-circle-2",
    })
}
</script>

<template>
    <div
        class="relative min-h-[calc(100vh-12rem)] px-4 py-10 sm:px-6 lg:px-8 flex items-center justify-center">
        <div
            class="pointer-events-none absolute inset-0 bg-linear-to-br from-primary-500/10 via-transparent to-secondary-500/10" />

        <UCard
            class="relative w-full max-w-lg border border-default/60 bg-default/95 backdrop-blur">
            <template #header>
                <div class="space-y-2 text-center">
                    <p class="text-xs uppercase tracking-[0.18em] text-muted">
                        Kontakt
                    </p>
                    <h1 class="text-2xl font-semibold text-highlighted">
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
                        placeholder="Jan Kowalski" />
                </UFormField>

                <UFormField label="E-mail" name="email">
                    <UInput
                        v-model="state.email"
                        class="w-full"
                        type="email"
                        placeholder="jan.kowalski@email.com" />
                </UFormField>

                <UFormField label="Temat" name="topic">
                    <UInput
                        v-model="state.topic"
                        class="w-full"
                        placeholder="Współpraca / pytanie o dane" />
                </UFormField>

                <UFormField label="Wiadomość" name="message">
                    <UTextarea
                        v-model="state.message"
                        class="w-full"
                        :rows="6"
                        placeholder="Opisz, w czym możemy pomóc..." />
                </UFormField>

                <UButton
                    type="submit"
                    color="primary"
                    variant="solid"
                    block
                    class="justify-center">
                    Wyślij wiadomość
                </UButton>
            </UForm>
        </UCard>
    </div>
</template>
