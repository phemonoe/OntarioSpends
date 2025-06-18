#!/bin/bash

# Create output directory if it doesn't exist
mkdir -p data/details

# Function to switch to a different Mullvad server (only CA and US servers)
switch_mullvad_server() {
  echo "Switching to a different Mullvad server (CA or US only)..."
  # Get a list of available CA and US servers
  available_servers=($(mullvad relay list | grep -o '\(ca\|us\)-[a-z]\{3\}-[a-z]\{2,4\}-[0-9]\{3\}' | sort))

  # Choose a random server from the filtered list
  if [ ${#available_servers[@]} -gt 0 ]; then
    random_index=$((RANDOM % ${#available_servers[@]}))
    new_server=${available_servers[$random_index]}

    echo "Switching to server: $new_server"
    mullvad relay set location "$new_server"

    # Wait for connection to establish by checking status
    echo "Waiting for connection to establish..."
    while true; do
      status=$(mullvad status)
      if [[ "$status" == *"Connected"* ]]; then
        echo "Successfully connected to new server: $new_server"
        break
      elif [[ "$status" == *"Connecting"* ]]; then
        echo "Still connecting, waiting..."
      else
        echo "Connection status: $status"
      fi
      sleep 1
    done

    return 0
  else
    echo "Error: No available CA or US Mullvad servers found"
    return 1
  fi
}

# Function to download a single details page
download_details() {
  local id=$1
  local output_file="data/details/${id}.html"

  # Skip if file already exists
  if [ -f "$output_file" ]; then
    echo "File $output_file already exists. Skipping..."
    completed=$((completed + 1))

    return 0
  fi

  echo "Downloading details for ID: $id"
  curl "https://www.nserc-crsng.gc.ca/ase-oro/Details-Detailles_eng.asp?id=${id}" \
    --compressed \
    -s \
    --connect-timeout 3 \
    --max-time 3 \
    -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:136.0) Gecko/20100101 Firefox/136.0' \
    -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
    -H 'Accept-Language: en-CA,en-US;q=0.7,en;q=0.3' \
    -H 'Accept-Encoding: gzip, deflate, br, zstd' \
    -H 'Connection: keep-alive' \
    -o "$output_file"

  # Check if file was downloaded successfully
  if [ -s "$output_file" ]; then
    completed=$((completed + 1))
    current=$((current + 1))

    # Calculate elapsed time
    current_time=$(date +%s)
    elapsed_time=$((current_time - start_time))

    # Display progress only for every 10th current item
    if (( current % 10 == 0 )); then
        display_progress $current $total_urls $elapsed_time $completed
    fi

    return 0
  else
    rm -f "$output_file"  # Remove empty file
    return 1
  fi
}

export -f download_details

# Function to display progress bar and it/s
display_progress() {
  local current=$1
  local total=$2
  local completed_percent=$((current * 100 / total))
  local bar_width=40
  local elapsed_time=$3
  local completed=$4

  # Calculate iterations per second (it/s)
  local its=0
  if (( elapsed_time > 0 )); then
    its=$(echo "scale=2; $current / $elapsed_time" | bc)
  fi

  # Create the progress bar
  local completed_width=$((bar_width * completed_percent / 100))
  local remaining_width=$((bar_width - completed_width))

  printf "\r[%${completed_width}s%${remaining_width}s] %d/%d (%d%%) - %.2f it/s" \
         "$(printf '#%.0s' $(seq 1 $completed_width))" \
         "$(printf ' %.0s' $(seq 1 $remaining_width))" \
         "$completed" "$total" "$completed_percent" "$its"
}

# Variables for progress tracking
current=0
completed=0
start_time=$(date +%s)
total_urls=700000 # estimate

# Process all JSON files and extract IDs
find data/listing -name "nserc_results_*.json" | grep "$1" | while read json_file; do
  echo "Processing $json_file"

  # Extract all detail URLs from the JSON file
  detail_urls=($(jq -r '.aaData[][5]' "$json_file"))

  echo "Found $total_urls URLs to process"


  # Process each URL with retry logic
  for detail_url in "${detail_urls[@]}"; do
    MAX_RETRIES=5
    retry_count=0
    success=false

    while [ $retry_count -lt $MAX_RETRIES ] && [ "$success" = false ]; do
      # Try downloading
      if download_details "$detail_url"; then
        success=true
      else
        retry_count=$((retry_count + 1))
        echo -e "\nFailed to download: $detail_url (attempt $retry_count of $MAX_RETRIES)"

        if [ -n "$1" ]; then
          echo "Waiting for main process to switch proxy"
              # Wait for connection to establish by checking status
          while true; do
            status=$(mullvad status)
            if [[ "$status" == *"Connected"* ]]; then
              echo "Successfully connected to new server: $new_server"
              break
            elif [[ "$status" == *"Connecting"* ]]; then
              echo "Still connecting, waiting..."
            else
              echo "Connection status: $status"
            fi
            sleep 1
          done

        elif [ $retry_count -lt $MAX_RETRIES ]; then
          echo "Switching Mullvad server before retrying..."
          switch_mullvad_server
        else
          echo "Maximum retries reached for: $detail_url"
          exit 1
        fi
      fi
    done
  done

  # Print newline after progress bar
  echo ""
done

echo "All details pages have been downloaded."
