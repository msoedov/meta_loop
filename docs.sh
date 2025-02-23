#!/bin/bash

# migrate to https://github.com/bitfield/script

# Check if target directory is provided
if [ $# -ne 1 ]; then
    echo "Usage: $0 <target_dir>"
    echo "Example: $0 output"
    exit 1
fi

TARGET_DIR=$1 # Target directory for output

# Define repositories and their docs paths as a space-separated list
# Format: "repo_url docs_path repo_url docs_path ..."
REPOS="https://github.com/pydantic/pydantic-ai docs https://github.com/crewAIInc/crewAI docs https://github.com/microsoft/autogen docs"
# Add more repositories like this:
# REPOS="$REPOS https://github.com/user/other-repo doc"

# Create target directory if it doesn't exist
mkdir -p "$TARGET_DIR"

# Temporary working directory
TEMP_DIR=$(mktemp -d)

# Function to check if file contains image references
contains_images() {
    local file="$1"
    # Look for common markdown image patterns
    grep -qE "!\[.*\]\(.*\)" "$file" ||
        grep -qE "<img.*>" "$file" ||
        grep -qE "\[.*\]: .*\.(png|jpg|jpeg|gif|svg)" "$file"
}

# Function to process each repository
process_repo() {
    local repo_url="$1"
    local docs_path="$2"
    local repo_name=$(basename "$repo_url" .git)

    echo "Processing $repo_name..."

    # Clone repo to temp directory
    git clone --depth 1 "$repo_url" "$TEMP_DIR/$repo_name" 2>/dev/null

    # Create output directory for this repo
    mkdir -p "$TARGET_DIR/$repo_name"

    # Check if docs directory exists
    if [ -d "$TEMP_DIR/$repo_name/$docs_path" ]; then
        # Copy all markdown and mdx files first
        find "$TEMP_DIR/$repo_name/$docs_path" -type f \( -name "*.md" -o -name "*.mdx" \) -exec cp {} "$TARGET_DIR/$repo_name/" \;

        # Remove files with image references
        local removed_count=0
        local kept_count=0
        for md_file in "$TARGET_DIR/$repo_name"/*.{md,mdx}; do
            if [ -f "$md_file" ]; then
                if contains_images "$md_file"; then
                    rm "$md_file"
                    ((removed_count++))
                else
                    ((kept_count++))
                fi
            fi
        done

        # Provide feedback
        echo "Processed $repo_name: kept $kept_count files, removed $removed_count with images"

        # Remove empty directory if no files remain
        if [ "$kept_count" -eq 0 ]; then
            rmdir "$TARGET_DIR/$repo_name" 2>/dev/null
        fi
    else
        echo "Documentation path $docs_path not found in $repo_name"
    fi

    # Clean up temp repo clone
    rm -rf "$TEMP_DIR/$repo_name"
}

# Process the repo list
set -- $REPOS # Convert space-separated list to positional parameters
while [ $# -ge 2 ]; do
    process_repo "$1" "$2"
    shift 2 # Move to next repo_url and docs_path pair
done

# Clean up temp directory
rm -rf "$TEMP_DIR"

echo "Done processing all repositories"
