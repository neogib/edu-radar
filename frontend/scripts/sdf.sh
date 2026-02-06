#!/usr/bin/env bash

# Ensure ImageMagick and image-sdf are installed

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
FRONTEND_DIR="$(cd "${SCRIPT_DIR}/.." && pwd)"
INPUT_DIR="${FRONTEND_DIR}/app/assets/images/figures/input"
OUTPUT_DIR="${FRONTEND_DIR}/app/assets/images/figures/sdf"
TMP_DIR="${SCRIPT_DIR}/.sdf-tmp"

mkdir -p "${OUTPUT_DIR}" "${TMP_DIR}"

for file in "${INPUT_DIR}"/*.png; do
  [ -f "${file}" ] || continue

  filename="$(basename "${file}" .png)"
  temp_file="${TMP_DIR}/temp_${filename}.png"
  output_file="${OUTPUT_DIR}/${filename}.png"

  # 1. Resize to max 448x448 (maintains aspect ratio)
  # 2. Colorize the icon white
  # 3. Flatten onto a black background
  # 4. Add 32px black border to all sides (total +64px width/height)
  magick "${file}" \
    -resize 448x448 \
    -fill white \
    -colorize 100% \
    -background black \
    -alpha remove \
    -alpha off \
    -bordercolor black \
    -border 32 \
    "${temp_file}"

  # Convert to SDF:
  # 512px input / 8 = 64px max output
  # 32px spread covers the 32px border we added
  image-sdf "${temp_file}" -s 32 -d 8 -c black -o "${output_file}"

  echo "✓ ${output_file}"
done

rm -f "${TMP_DIR}"/temp_*.png
