export interface SchoolInfoItem {
    key: string
    label: string
    icon: string
    lines: string[]
    href?: string
    external?: boolean
}

export interface SchoolBadgeSection {
    key: string
    label: string
    icon: string
    color: "primary" | "secondary"
    items: { id: number; nazwa: string }[]
}
