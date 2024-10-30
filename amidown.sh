#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# JSON file for monitored URLs
JSON_FILE="monitored_urls.json"

# Check if monitored_urls.json exists, else create it
if [[ ! -f $JSON_FILE ]]; then
    echo "[]" > "$JSON_FILE"
    echo -e "${CYAN}Created $JSON_FILE file.${NC}"
fi

# Check if a file was provided as an argument
if [[ -z "$1" ]]; then
    echo -e "${RED}Error: Please provide a file containing subdomains as an argument.${NC}"
    echo "Usage: $0 <filename>"
    exit 1
fi

# File containing subdomains
SUBDOMAINS_FILE="$1"

# Check if the file exists
if [[ ! -f $SUBDOMAINS_FILE ]]; then
    echo -e "${RED}Error: File $SUBDOMAINS_FILE not found.${NC}"
    exit 1
fi

# Function to add URL to JSON file if not already present
add_url_to_json() {
    local url="$1"
    if ! grep -q "\"$url\"" "$JSON_FILE"; then
        # Insert the URL into the JSON array
        jq --arg url "$url" '. += [$url]' "$JSON_FILE" > temp.json && mv temp.json "$JSON_FILE"
        echo -e "${GREEN}Added URL:${NC} $url"
    else
        echo -e "${RED}URL already monitored:${NC} $url"
    fi
}

# Process each line in the provided file
echo -e "${CYAN}Processing subdomains from $SUBDOMAINS_FILE...${NC}"
while IFS= read -r line || [ -n "$line" ]; do
    if [[ -n "$line" ]]; then
        add_url_to_json "$line"
    fi
done < "$SUBDOMAINS_FILE"

# Display confirmation
echo -e "${CYAN}Finished adding URLs to monitored_urls.json.${NC}"
