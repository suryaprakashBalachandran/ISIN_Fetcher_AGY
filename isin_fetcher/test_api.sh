#!/bin/bash

# Test the ISIN Fetcher API

echo "Testing ISIN Fetcher API..."
echo ""

curl -X POST "http://localhost:8000/fetch-isins" \
  -H "Content-Type: application/json" \
  -d '{
    "queries": [
      "tata motors PV",
      "Tata motors CV",
      "Parag Parikh Flexi Cap Fund"
    ]
  }' | python3 -m json.tool

echo ""
echo "Test complete!"
