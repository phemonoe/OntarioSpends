#!/bin/bash

# Create the output directory if it doesn't exist
mkdir -p data/details

# Extract all IDs using jq
ids=$(jq -rc '.response.docs.[].id' data/results.json)

# Define the download function
download_json() {
  ID="$1"

  local output_file="data/details/${ID}.json"

  # Skip if file already exists
  if [ -f "$output_file" ]; then
    return 0
  fi


    curl "https://webapps.cihr-irsc.gc.ca/decisions/sq?q=id:$ID&version=2.2&start=0&rows=50&indent=on&wt=json" \
    --compressed \
    -s \
    --connect-timeout 2 \
    --max-time 2 \
    -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:136.0) Gecko/20100101 Firefox/136.0' \
    -H 'Accept: application/json, text/javascript, */*; q=0.01' \
    -H 'Accept-Language: en-CA,en-US;q=0.7,en;q=0.3' \
    -H 'Accept-Encoding: gzip, deflate, br, zstd' \
    -H 'X-Requested-With: XMLHttpRequest' \
    -H 'Connection: keep-alive' \
    -H "Referer: https://webapps.cihr-irsc.gc.ca/decisions/p/project_details.html?applId=$ID&lang=en" \
    -H 'Cookie: JSESSIONID=38CBB75D6DC72ADC076ACA96DC7DF0C0' \
    -H 'Sec-Fetch-Dest: empty' \
    -H 'Sec-Fetch-Mode: cors' \
    -H 'Sec-Fetch-Site: same-origin' \
    -o "$output_file"

    echo "Downloaded $ID"
}

# Export the function so parallel can use it
export -f download_json

# Run the downloads in parallel
echo "$ids" | parallel -j 40 download_json {}