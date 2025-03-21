curl -X POST "https://www.evernote.com/oauth" \
  -d "oauth_consumer_key=gatgpt-3463" \
  -d "oauth_signature_method=PLAINTEXT" \
  -d "oauth_signature=9f8bffab4792dd81ea464657c5a4c8dd2b8ab3666909591dc12ce6f9&" \
  -d "oauth_timestamp=$(date +%s)" \
  -d "oauth_nonce=$(openssl rand -hex 16)" \
  -d "oauth_callback=oob"