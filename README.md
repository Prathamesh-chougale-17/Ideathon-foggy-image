# Foggy Image Enhancement Project

This project implements a dark channel prior dehazing algorithm combined with adaptive histogram equalization for enhancing foggy and dark images.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- Ultralytics YOLO

### Setting up the Environment

#### Windows Users (using Git Bash)

1. Open Git Bash in the project directory
2. Make the venvbuilder script executable:

```bash
chmod +x venvbuilder.sh
```

3. Create and activate the virtual environment:

```bash
./venvbuilder.sh
source venv/Scripts/activate
```

#### Linux/Mac Users

1. Open terminal in the project directory
2. Make the venvbuilder script executable:

```bash
chmod +x venvbuilder.sh
```

3. Create and activate the virtual environment:

```bash
./venvbuilder.sh
source venv/bin/activate
```

### Manual Setup (if venvbuilder.sh fails)

1. Create virtual environment:

```bash
python -m venv venv
```

2. Activate virtual environment:

- Windows:

```terminal
    venv/Scripts/activate
```

- Linux/Mac:

```bash
source venv/bin/activate
```

3. Install requirements:

```bash
pip install -r requirements.txt
```

### Running the Application

1. Ensure your virtual environment is activated
2. Run the application:

```bash
python app.py
```

3. Press 'q' to quit the application

## Troubleshooting

- If you get permission errors, ensure venvbuilder.sh has execute permissions
- If packages fail to install, try updating pip:

```bash
pip install --upgrade pip
```

- For Windows users, make sure you're using Git Bash and not CMD or PowerShell

## License

This project is licensed under the MIT License - see the LICENSE file for details
