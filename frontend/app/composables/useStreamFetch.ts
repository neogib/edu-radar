export const useStreamFetch = () => {
    const config = useRuntimeConfig()

    const streamFetch = async <T>(
        url: string,
        options: {
            signal: AbortSignal
            onChunk: (chunk: T) => void
        },
    ) => {
        try {
            const response = await fetch(`${config.public.apiBase}${url}`, {
                signal: options.signal,
                headers: {
                    Accept: "application/x-ndjson", // NDJSON for streaming
                },
            })

            const reader = response.body?.getReader()
            if (!reader) throw new Error("No response body")

            const decoder = new TextDecoder()

            let buffer = ""

            while (true) {
                const { value, done } = await reader.read()
                if (done || options.signal.aborted) break

                buffer += decoder.decode(value, { stream: true })

                // NDJSON: one JSON object per line
                const lines = buffer.split("\n")

                buffer = lines.pop() ?? ""

                for (const line of lines) {
                    if (!line.trim()) continue
                    const parsed = JSON.parse(line)
                    options.onChunk(parsed)
                }
            }
        } catch (error) {
            // handle abort error separately, it is caused by another request
            if (error instanceof DOMException && error.name === "AbortError") {
                console.log("Fetch aborted by signal")
                return
            }

            console.error("Stream fetch error:", error)
            throw error
        }
    }

    return { streamFetch }
}
