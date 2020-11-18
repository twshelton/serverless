docker run --rm -ti \
  -e AZURE_STORAGE_CONNECTION_STRING="DefaultEndpointsProtocol=https;AccountName=memberemulator;AccountKey=N8+bp3hBq1JE9c5g3IfRtCknbW0TMGzOaR5VmqIKkMrziZ0I/rZeiAcD3v/EmQhddPp6FTI44WMHJgqAABvaSw==;EndpointSuffix=core.windows.net" \
  --name=culedger-stress-server \
  stress:0.0.1 \
  bash
