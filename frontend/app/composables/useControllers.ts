export const useControllers = () => {
    const bboxController = useState<AbortController | null>(
        "bbox-controller",
        () => null,
    )

    const streamingController = useState<AbortController | null>(
        "streaming-controller",
        () => null,
    )
    return { bboxController, streamingController }
}
