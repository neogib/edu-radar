<template>
    <div class="min-h-screen bg-default">
        <!-- Navigation Bar -->
        <NavBar />

        <!-- Main Content -->
        <main class="max-w-7xl mx-auto px-2 sm:px-5 lg:px-8 py-8">
            <!-- Hero Section -->
            <div class="text-center mb-12">
                <h1
                    class="text-4xl md:text-6xl font-bold text-highlighted mb-4">
                    Ranking
                    <span class="text-primary">Szkół</span>
                    w Polsce
                </h1>
                <p class="text-xl text-toned max-w-3xl mx-auto leading-8">
                    Znajdź najlepsze szkoły w swojej okolicy. Porównuj wyniki,
                    sprawdzaj rankingi i podejmuj świadome decyzje dotyczące
                    dalszej edukacji.
                </p>
            </div>

            <!-- Main Content Grid -->
            <SchoolSearchForm />

            <!-- Additional Info Section -->
            <AdditionalInfo />
        </main>

        <AppFooter />
    </div>
</template>
