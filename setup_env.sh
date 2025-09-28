#!/bin/bash

set -e

# === Configuration ===
VENV_DIR=".venv"
TEST_FILE="test_app.py"

# === Check Python ===
if ! command -v python3 &> /dev/null; then
    echo "Python3 not found. Please install Python3."
    exit 1
fi
echo "Python3 is installed."
echo ""

# === Create virtual environment ===
echo "Creating virtual environment..."
python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"
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

if [ -f "$VENV_DIR/bin/activate" ]; then
    source "$VENV_DIR/bin/activate"
fi

python -m unittest $TEST_FILE
if [ \$? -ne 0 ]; then
    echo "Tests failed. Push aborted."
    exit 1
else
    echo "Test passed. Proceeding with push..."
fi
EOF

chmod +x "$HOOK_PATH"
echo "Git pre-push hook installed."
echo ""

# === Generating a SECRET_KEY in .env ===
echo "Generating a Secret Key for session cookies"
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")

if [ ! -f .env ]; then
	echo "SECRET_KEY=$SECRET_KEY" > .env
	echo ".env created with secret key"
else
	if grep -q "^SECRET_KEY=" .env; then
		sed -i "s/^SECRET_KEY=.*/SECRET_KEY=$SECRET_KEY/" .env
		echo "SECRET_KEY updated"
	else
		echo "SECRET_KEY=$SECRET_KEY" >> .env
		echo "SECRET_KEY appended to existing .env"
	fi
fi
echo ""

# === (Optional) Set Flask env vars in activate script ===
echo "export FLASK_APP=app.py" >> "$VENV_DIR/bin/activate"
echo "export FLASK_ENV=development" >> "$VENV_DIR/bin/activate"
echo""

# === Final instructions ===
echo ""
echo "Setup complete!"
echo "To start working, run:"
echo "   source $VENV_DIR/bin/activate"
echo "   flask run"
echo ""
