#!/bin/bash

set -e

# === Configuration ===
VENV_DIR=".venv"
TEST_FILE="test_app.py"

# === Detect OS and set activation path ===
OS_TYPE=$(uname | tr '[:upper:]' '[:lower:]')
if [[ "$OS_TYPE" == *"mingw"* || "$OS_TYPE" == *"msys"* || "$OS_TYPE" == *"windows"* ]]; then
    ACTIVATE_PATH="$VENV_DIR/Scripts/activate"
    PYTHON_EXEC="python"
else
    ACTIVATE_PATH="$VENV_DIR/bin/activate"
    PYTHON_EXEC="python3"
fi

# === Check Python ===
if ! command -v $PYTHON_EXEC &> /dev/null; then
    echo "$PYTHON_EXEC not found. Please install Python 3."
    exit 1
fi
echo "Python is installed."
echo ""

# === Create virtual environment ===
echo "Creating virtual environment..."
$PYTHON_EXEC -m venv "$VENV_DIR"
source "$ACTIVATE_PATH"
echo ""

# === Upgrade pip and install dependencies ===
echo "Upgrading pip..."
pip install --upgrade pip

echo ""
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
else
    echo "No requirements.txt found. Skipping dependency installation."
fi
echo ""

# === Setup Git pre-push hook ===
echo "Setting up Git pre-push hook to enforce test pass..."

HOOK_PATH=".git/hooks/pre-push"

cat > "$HOOK_PATH" <<EOF
#!/bin/bash
echo "Running $TEST_FILE before push..."

if [ -f "$ACTIVATE_PATH" ]; then
    source "$ACTIVATE_PATH"
fi

$PYTHON_EXEC -m unittest $TEST_FILE
if [ \$? -ne 0 ]; then
    echo "Tests failed. Push aborted."
    exit 1
else
    echo "Tests passed. Proceeding with push..."
fi
EOF

chmod +x "$HOOK_PATH"
echo "Git pre-push hook installed."
echo ""

# === Generating a SECRET_KEY in .env ===
echo "Generating a Secret Key for session cookies"
SECRET_KEY=$($PYTHON_EXEC -c "import secrets; print(secrets.token_hex(32))")

if [ ! -f .env ]; then
    echo "SECRET_KEY=$SECRET_KEY" > .env
    echo ".env created with secret key"
else
    if grep -q "^SECRET_KEY=" .env; then
        sed -i.bak "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
        echo "SECRET_KEY updated"
    else
        echo "SECRET_KEY=$SECRET_KEY" >> .env
        echo "SECRET_KEY appended to existing .env"
    fi
fi
echo ""

# === (Optional) Set Flask env vars in activate script ===
echo "Setting Flask environment variables in virtual environment activation script..."
echo "export FLASK_APP=app.py" >> "$ACTIVATE_PATH"
echo "export FLASK_ENV=development" >> "$ACTIVATE_PATH"
echo ""

# === Final instructions ===
echo ""
echo "✅ Setup complete!"
echo "To start working, run:"
echo "   source $ACTIVATE_PATH"
echo "   flask run"
echo ""

