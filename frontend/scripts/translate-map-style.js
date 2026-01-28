import fs from "fs"
import isEqual from "lodash/isEqual.js"
import { resolve } from "path"

const langCode = "pl"

const BASE = resolve(process.cwd(), "public/map-styles/style-base.json")

const OUT = resolve(process.cwd(), "public/map-styles/style-pl.json")

// load original style
const style = JSON.parse(fs.readFileSync(BASE, "utf-8"))

// apply transformation
for (const layer of style.layers) {
    if (!layer.layout) continue

    const textField = layer.layout["text-field"]
    if (!textField) continue

    if (isEqual(textField, ["to-string", ["get", "ref"]])) continue

    const id = layer.id
    const separator = id.includes("line") || id.includes("highway") ? " " : "\n"

    const parts = [
        ["get", `name_${langCode}`],
        ["get", `name:${langCode}`],
        ["get", "name"],
    ]

    layer.layout["text-field"] = [
        "case",
        ["has", "name:nonlatin"],
        ["concat", ["get", "name:latin"], separator, ["get", "name:nonlatin"]],
        ["coalesce", ...parts],
    ]
}

// write localized style
fs.writeFileSync(OUT, JSON.stringify(style, null, 2))
