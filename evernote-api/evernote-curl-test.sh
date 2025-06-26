# evernote-curl-test.sh

# Read the token from file
TOKEN=$(cat evernote_token.txt)

# Test API access - this just checks if the token works by listing notebooks
echo "Testing Evernote API access..."
echo "Using token: ${TOKEN:0:5}...${TOKEN:(-5)}" # Shows first and last 5 chars for security

# Try the API call to list notebooks
curl -v -X GET "https://www.evernote.com/shard/s1/notestore/listNotebooks" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json"

echo -e "\n\nIf you see a list of notebooks above, your token is working!"
echo "If you see an error, your token may be invalid or expired."