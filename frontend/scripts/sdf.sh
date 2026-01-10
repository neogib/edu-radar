#!/bin/bash

# Ensure ImageMagick and image-sdf are installed
# This script is used to convert 512x512 PNG files to 128x128 SDF PNG files for use with maplibre-gl

# directory for output SDF files
mkdir -p sdf-output

# Process each PNG file in the current directory
for file in ./*.png; do
    filename=$(basename "$file" .png)
    
    # prepare padding and colors
    magick "$file" \
        -fill white \
        -colorize 100% \
        -background black \
        -gravity center \
        -extent 1024x1024 \
        "temp_${filename}.png"
    
    # convert to sdf using https://www.npmjs.com/package/image-sdf
    image-sdf "temp_${filename}.png" -s 32 -d 8 -c black -o "sdf-output/${filename}.png"
    
    # clean up temporary file
    rm "temp_${filename}.png"
    
    echo "✓ ${filename}.png"
done
