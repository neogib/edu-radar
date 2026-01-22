export type MapIntent = string | null

export const useMapIntent = () => useState<MapIntent>("map-intent", () => null)
