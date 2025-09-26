# Test the Video Recommendation API
Write-Host "=== Testing Video Recommendation API ===" -ForegroundColor Green

# Test endpoints
$baseUrl = "http://127.0.0.1:8000"

Write-Host "1. Testing personalized feed..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod "$baseUrl/feed?username=testuser" -Method GET
    $response | ConvertTo-Json -Depth 6 | Write-Output
    Write-Host "✅ Personalized feed test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Personalized feed test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n2. Testing category feed..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod "$baseUrl/feed?username=testuser&project_code=fitness" -Method GET
    $response | ConvertTo-Json -Depth 6 | Write-Output
    Write-Host "✅ Category feed test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Category feed test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n3. Testing pagination..." -ForegroundColor Yellow
try {
    $response = Invoke-RestMethod "$baseUrl/feed?username=testuser&limit=5&offset=0" -Method GET
    $response | ConvertTo-Json -Depth 6 | Write-Output
    Write-Host "✅ Pagination test passed" -ForegroundColor Green
} catch {
    Write-Host "❌ Pagination test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n4. Testing API documentation..." -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest "$baseUrl/docs" -Method GET
    if ($response.StatusCode -eq 200) {
        Write-Host "✅ API docs accessible at: $baseUrl/docs" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ API docs test failed: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host "`n=== Test Complete ===" -ForegroundColor Green
