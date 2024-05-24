#!/bin/bash

input_folder="input/1_NK_2023"
output_folder="output/1_NK_2023"
log_file="conversion.log"
error_file="conversion_errors.log"

# Create output folder structure before processing
find "$input_folder" -type d | while read -r dir; do
    mkdir -p "$output_folder${dir#$input_folder}"
done

# Function to convert a single file
convert_file() {
    local xls_file="$1"
    local relative_path
    relative_path=$(dirname "${xls_file#$input_folder}")
    if flatpak run org.libreoffice.LibreOffice --headless --convert-to html --outdir "$output_folder$relative_path" "$xls_file"; then
        echo "Converted: $xls_file" >> "$log_file"
    else
        echo "Failed: $xls_file" >> "$error_file"
    fi
}

# Count the total number of .xls files
total_files=$(find "$input_folder" -type f -name '*.xlsx' | wc -l)

# Initialize the counter
counter=0

# Find all .xls files and process them sequentially with a progress counter
find "$input_folder" -type f -name '*.xlsx' | while read -r xls_file; do
    counter=$((counter + 1))
    echo "Processing file $counter of $total_files: $xls_file"
    convert_file "$xls_file"
done

echo "Conversion completed. Check $log_file and $error_file for details."
