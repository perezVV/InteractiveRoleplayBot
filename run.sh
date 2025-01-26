#!/bin/bash

# uv is used here largely because it makes installation of Python easy.
# At least, it is easier than installing Python manually.

# If uv doesn't exist, let's install uv. Installation is thankfully simple.
if ! [ -x "$(command -v uv)" ]; then
  curl -LsSf https://astral.sh/uv/install.sh | sh
fi

# Simple check to see if uv has already installed a virtual environment.
# uv does not work without it.
if [ ! -d ".venv" ]; then
  uv venv --python 3.10
fi

# From here, everything is relatively standard stuff, except we use uv.
uv pip install -r requirements.txt
uv run main.py

read -p "Press enter to continue."