import type { BoundingBox } from "~/types/boundingBox"

export const useInitialBbox = () =>
    useState<BoundingBox | undefined>("initial-bbox")
