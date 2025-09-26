cd 'C:\Users\ACER\OneDrive\Documents\AI VIDEO RECOMMENDATION ENGINE'
# Locate or install Python 3.12
 = ''; ='C:\Users\ACER\AppData\Local\Programs\Python\Python312\python.exe'; ='C:\Program Files\Python312\python.exe'
if (Test-Path ) { = } elseif (Test-Path ) { = } else { =Get-Command python.exe -ErrorAction SilentlyContinue; if (){=.Path} }
if (-not ) { winget install -e --id Python.Python.3.12 --accept-package-agreements --accept-source-agreements; Start-Sleep 5; if (Test-Path ){=} elseif (Test-Path ){=} else { Write-Error 'Python path not found. Reopen PowerShell and rerun.'; exit 1 } }
&  -m venv .venv; if (!(Test-Path .\.venv\Scripts\python.exe)) { Write-Error 'Failed to create venv'; exit 1 }
.\.venv\Scripts\python.exe -m pip install --upgrade pip
if (Test-Path .\requirements.txt) { .\.venv\Scripts\python.exe -m pip install -r requirements.txt } else { .\.venv\Scripts\python.exe -m pip install fastapi 'uvicorn[standard]' sqlalchemy alembic pydantic requests python-dotenv redis httpx pytest aiosqlite }
.\.venv\Scripts\python.exe -m alembic upgrade head
Start-Process -FilePath '.\.venv\Scripts\python.exe' -ArgumentList '-m uvicorn app.main:app --host 127.0.0.1 --port 8000' -WindowStyle Hidden
Start-Sleep -Seconds 7
try { Invoke-RestMethod 'http://127.0.0.1:8000/feed?username=testuser' | ConvertTo-Json -Depth 8 | Write-Output } catch { try { Invoke-RestMethod 'http://localhost:8000/feed?username=testuser' | ConvertTo-Json -Depth 8 | Write-Output } catch { Write-Error 'Server not reachable. Try different port: .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 9000' } }
