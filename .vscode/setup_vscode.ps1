# setup_vscode.ps1
Write-Host "Setting up FastFood App in VS Code..." -ForegroundColor Green

# Create folders
New-Item -ItemType Directory -Force -Path "static\css" | Out-Null
New-Item -ItemType Directory -Force -Path "templates" | Out-Null
New-Item -ItemType Directory -Force -Path "instance" | Out-Null

# Install packages
Write-Host "Installing packages..." -ForegroundColor Yellow
python -m pip install --upgrade pip
python -m pip install Flask Flask-SQLAlchemy Flask-Login Werkzeug

Write-Host "`n✅ Setup complete!" -ForegroundColor Green
Write-Host "Run 'python app.py' to start the server" -ForegroundColor Cyan