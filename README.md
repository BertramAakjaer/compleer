# Compleer
I used UV while developing the program and to control virtual enviroments, but pip should work as well.


## Installation & Setup (dev)
1. Clone the repository
```bash
# Clone this repository with git
git clone https://github.com/BertramAakjaer/compleer.git

# Open the directory in terminal
cd compleer/
```

2. Create Virtual Enviroment & activate
```bash
uv venv

source .venv/bin/activate
```

3. Install requirements
```bash
# For Users
uv sync

# For Devs
uv sync --no-dev
```

1. Run the program
```bash
uv run compleer
```


# Tools for Contribution

**Generating a requirements file**
```bash
uv pip compile pyproject.toml -o requirements.txt
```
**Install Program as development**
```bash
uv pip install -e .
```
**add new requirements**
```bash
uv add <package_name>
```

**Using ruff**
```bash
uv run ruff check .
uv run ruff check --fix .
uv run ruff format .
```