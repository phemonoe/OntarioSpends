#!/bin/bash

# Parameters
START_RECORD=$1
OUTPUT_FILE="data/listing/nserc_results_$START_RECORD.json"
RECORDS_PER_PAGE=200
THREAD_ID=$((($START_RECORD/RECORDS_PER_PAGE)%8+1))
COOKIE_FILE="tmp/cookies_$THREAD_ID.txt"


# Skip downloading if the output file already exists
if [ -f "$OUTPUT_FILE" ]; then
  echo "Thread $THREAD_ID: Output file $OUTPUT_FILE already exists. Skipping download..."
  exit 0
fi

# Check if this is the first run for this thread
if [ $START_RECORD -eq 0 ] || [ ! -f "$COOKIE_FILE" ]; then
  echo "Thread $THREAD_ID: Setting up initial search parameters..."

  # Submit the search form to set parameters
  curl 'https://www.nserc-crsng.gc.ca/ase-oro/Results-Resultats_eng.asp' \
       --compressed \
       -X POST \
       -s \
       -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:136.0) Gecko/20100101 Firefox/136.0' \
       -H 'Accept: text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8' \
       -H 'Accept-Language: en-CA,en-US;q=0.7,en;q=0.3' \
       -H 'Accept-Encoding: gzip, deflate, br, zstd' \
       -H 'Referer: https://www.nserc-crsng.gc.ca/ase-oro/index_eng.asp' \
       -H 'Content-Type: application/x-www-form-urlencoded' \
       -H 'Origin: https://www.nserc-crsng.gc.ca' \
       -H 'Connection: keep-alive' \
       -H 'Upgrade-Insecure-Requests: 1' \
       -H 'Sec-Fetch-Dest: document' \
       -H 'Sec-Fetch-Mode: navigate' \
       -H 'Sec-Fetch-Site: same-origin' \
       -H 'Sec-Fetch-User: ?1' \
       -H 'Priority: u=0, i' \
       -c "$COOKIE_FILE" \
       --data-raw 'fiscalyearfrom=1991&fiscalyearto=2023&competitionyearfrom=0&competitionyearto=0&PersonName=&KeyWords=&KeyWordsIn=&OrgType=0&AreaApplicationOther=&ResearchSubjectOther=&Department=&AwardAmountMin=&AwardAmountMax=&ResultsBy=1&button=' \
       -o "tmp/search_setup_$THREAD_ID.html"
fi

# Now fetch the actual results page using AJAX
echo "Thread $THREAD_ID: Fetching records $START_RECORD to $(($START_RECORD+$RECORDS_PER_PAGE-1))..."
curl 'https://www.nserc-crsng.gc.ca/ase-oro/_incs/ajax.asp?lang=e' \
     --compressed \
     -X POST \
     -s \
     -H 'User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:136.0) Gecko/20100101 Firefox/136.0' \
     -H 'Accept: application/json, text/javascript, */*; q=0.01' \
     -H 'Accept-Language: en-CA,en-US;q=0.7,en;q=0.3' \
     -H 'Accept-Encoding: gzip, deflate, br, zstd' \
     -H 'Referer: https://www.nserc-crsng.gc.ca/ase-oro/Results-Resultats_eng.asp' \
     -H 'Content-Type: application/x-www-form-urlencoded; charset=UTF-8' \
     -H 'X-Requested-With: XMLHttpRequest' \
     -H 'Origin: https://www.nserc-crsng.gc.ca' \
     -H 'Connection: keep-alive' \
     -b "$COOKIE_FILE" \
     -c "$COOKIE_FILE" \
     -H 'Sec-Fetch-Dest: empty' \
     -H 'Sec-Fetch-Mode: cors' \
     -H 'Sec-Fetch-Site: same-origin' \
     -H 'Priority: u=0' \
     --data-raw "sEcho=2&iColumns=5&sColumns=&iDisplayStart=$START_RECORD&iDisplayLength=$RECORDS_PER_PAGE&mDataProp_0=0&mDataProp_1=1&mDataProp_2=2&mDataProp_3=3&mDataProp_4=4&sSearch=&bRegex=false&sSearch_0=&bRegex_0=false&bSearchable_0=true&sSearch_1=&bRegex_1=false&bSearchable_1=true&sSearch_2=&bRegex_2=false&bSearchable_2=true&sSearch_3=&bRegex_3=false&bSearchable_3=true&sSearch_4=&bRegex_4=false&bSearchable_4=true&iSortingCols=2&iSortCol_0=0&sSortDir_0=asc&iSortCol_1=3&sSortDir_1=desc&bSortable_0=true&bSortable_1=true&bSortable_2=true&bSortable_3=true&bSortable_4=true" \
     -o "$OUTPUT_FILE"

#sleep 2

echo "Thread $THREAD_ID: Downloaded records $START_RECORD to $(($START_RECORD+$RECORDS_PER_PAGE-1)) to $OUTPUT_FILE"

# Save the total record count if this is the first batch
if [ $START_RECORD -eq 0 ]; then
  TOTAL_RECORDS=$(jq -rc '.iTotalDisplayRecords' data/listing/nserc_results_0.json)
  echo $TOTAL_RECORDS > total_records.txt
  echo "Total records found: $TOTAL_RECORDS"
fi

