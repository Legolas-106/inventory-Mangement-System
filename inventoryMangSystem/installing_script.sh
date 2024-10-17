#!/bin/bash

# Step 1: Ensure the script and project are in the same directory
PROJECT_DIR="$(dirname "$0")"
cd "$PROJECT_DIR"

# Step 2: Check if Python3 is installed
if ! command -v python3 > /dev/null; then
  echo "Python3 is not installed. Please install Python3 before running this script."
  exit 1
fi

printf "\n\n\n\n###############Setting up VENV###############\n\n\n\n"


# Step 3: Prompt the user for the virtual environment name
read -p "Enter the name for your virtual environment: " VENV_NAME

# Step 4: Create a Python virtual environment with the entered name
echo "Creating Python virtual environment: $VENV_NAME..."
python3 -m venv $VENV_NAME

# Step 5: Activate the virtual environment
echo "Activating the virtual environment..."
source $VENV_NAME/bin/activate

# Step 6: Create or update a .env file inside the project directory
ENV_FILE="$PROJECT_DIR/inventoryMangSystem/.env"  # Update to your project name

# Create the .env file if it doesn't exist
if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
    echo ".env file created at $ENV_FILE"
else
    echo ".env file already exists at $ENV_FILE"
fi

# Add VENV_NAME to the .env file
echo "Saving environment variables in $ENV_FILE..."
echo "VENV_NAME=$VENV_NAME" > $ENV_FILE

echo ".env file created/updated with VENV_NAME."

# Step 7: Display success message
echo "Virtual environment '$VENV_NAME' has been created and activated."

printf "\n\n\n\n###############Installing Requirenment txt###############\n\n\n\n"


REQUIREMENTS_FILE="$PROJECT_DIR/inventoryMangSystem/requirements.txt"

if [ -f "$REQUIREMENTS_FILE" ]; then
    echo "Installing packages from $REQUIREMENTS_FILE..."
    pip install -r $REQUIREMENTS_FILE

    # Check if the installation was successful
    if [ $? -ne 0 ]; then
        echo "Error in installing packages. Some services might behave improperly."
    else
        echo "Packages installed successfully."
    fi
else
    echo "$REQUIREMENTS_FILE does not exist. Skipping package installation."
fi

deactivate

printf "\n\n\n\n###############Setting Up postgresql###############\n\n\n\n"


# Step 8: Ask for PostgreSQL connection details, including host, port, superuser, DB name, user, and password
echo "Please provide PostgreSQL connection details."

read -p "Enter the PostgreSQL host (default is 'localhost'): " DB_HOST
DB_HOST=${DB_HOST:-localhost}  # Default to 'localhost' if nothing is entered
read -p "Enter the PostgreSQL port (default is '5432'): " DB_PORT
DB_PORT=${DB_PORT:-5432}  # Default to '5432' if nothing is entered
read -p "Enter the name of the database you want to create: " DB_NAME
read -p "Enter the PostgreSQL superuser (default is 'postgres'): " PG_SUPERUSER
PG_SUPERUSER=${PG_SUPERUSER:-postgres}  # Default to 'postgres' if nothing is entered
read -p "Enter the name of the new database user you want to create: " DB_USER
read -sp "Enter the password for the new database user: " DB_PASSWORD
echo

# Save these details to the .env file
echo "DB_HOST=$DB_HOST" >> "$ENV_FILE"
echo "DB_PORT=$DB_PORT" >> "$ENV_FILE"
echo "DB_NAME=$DB_NAME" >> "$ENV_FILE"
echo "DB_USER=$DB_USER" >> "$ENV_FILE"
echo "DB_PASSWORD=$DB_PASSWORD" >> "$ENV_FILE"

# Step 9: Switch to the PostgreSQL superuser and create the database and user
echo "Switching to PostgreSQL superuser to create database and user..."

# Run PostgreSQL commands to create the database and the user, specifying host and port
sudo -u "$PG_SUPERUSER" psql<<EOF
-- Create the database
CREATE DATABASE $DB_NAME;

-- Create the new user with the provided password
CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';

EOF

if [ $? -ne 0 ]; then
    echo "Error: Failed to create database or user. Please check your PostgreSQL connection details and superuser credentials."
else
    echo "Database '$DB_NAME' and user '$DB_USER' created successfully."
fi

# Step 10: Grant privileges to the user for the new database
echo "Granting all privileges on the database '$DB_NAME' to user '$DB_USER'..."

sudo -u "$PG_SUPERUSER" psql<<EOF
-- Grant all privileges on the database to the new user
GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;
EOF

if [ $? -ne 0 ]; then
    echo "Error: Failed to grant privileges to user '$DB_USER' on database '$DB_NAME'."
else
    echo "Privileges granted successfully."
fi


printf "\n\n\n\n###############Running Python Make migrations and migrate###############\n\n\n\n"


# Step 11: Activate the virtual environment and run Django migrations
echo "Activating the virtual environment and running Django migrations..."

# Activate the virtual environment
source "$PROJECT_DIR/$VENV_NAME/bin/activate"

cd "$PROJECT_DIR/inventoryMangSystem"
echo "Cahnge the directory to project ones"

# Step 12: Run Django's makemigrations and migrate
echo "Running 'python manage.py makemigrations'..."
python manage.py makemigrations

if [ $? -ne 0 ]; then
    echo "Error: 'makemigrations' failed. Please check your Django models or database configuration."
    deactivate  # Deactivate the virtual environment if there's an error
    exit 1
fi

echo "Running 'python manage.py migrate'..."
python manage.py migrate

if [ $? -ne 0 ]; then
    echo "Error: 'migrate' failed. Please check your database configuration."
    deactivate  # Deactivate the virtual environment if there's an error
    exit 1
fi

echo "Migrations completed successfully."

# Step 13: Deactivate the virtual environment
deactivate
echo "Virtual environment deactivated."

printf "\n\n\n\n###############Setting up REDIS Variables###############\n\n\n\n"


# Step 14: Ask for Redis connection details
echo "Please provide Redis connection details."

read -p "Enter the Redis host (default is 'localhost'): " REDIS_HOST
REDIS_HOST=${REDIS_HOST:-localhost}  # Default to 'localhost' if nothing is entered
read -p "Enter the Redis port (default is '6379'): " REDIS_PORT
REDIS_PORT=${REDIS_PORT:-6379}  # Default to '6379' if nothing is entered
read -sp "Enter the Redis password (leave empty if none): " REDIS_PASSWORD
echo

# Save Redis connection details to the .env file
echo "REDIS_HOST=$REDIS_HOST" >> "$ENV_FILE"
echo "REDIS_PORT=$REDIS_PORT" >> "$ENV_FILE"
echo "REDIS_PASSWORD=$REDIS_PASSWORD" >> "$ENV_FILE"

echo "Redis connection details saved in .env file."


read -p "Enter Debug Level (True/False): " DEBUG_LEVEL

read -p "Enter Secret Key: " SECRET_KEY

read -p "Enter Allowed Hosts (comma-separated): " ALLOWED_HOSTS

cat <<EOL >> "$ENV_FILE"
DEBUG=$DEBUG_LEVEL
SECRET_KEY=$SECRET_KEY
ALLOWED_HOSTS=$ALLOWED_HOSTS
EOL


