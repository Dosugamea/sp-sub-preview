# sp-sub-[INSERT SERVER NAME HERE]


![Python Version](https://img.shields.io/badge/python-v3.10.5-blue)
![License](https://img.shields.io/badge/license-AGPLv3%2B-green)

[INSERT SERVER DESCRIPTION] server for [sp-api-v3](https://github.com/PurplePalette/sp-api-v3)
This server meant micro service to [DO SOMETHING].

## Requirements

* Poetry(1.2.0)
* Python(>=3.10.X) (we recommend uses pyenv)

## Development setup
```bash
pyenv local 3.10.5
(optional: poetry config virtualenvs.in-project true --local)
poetry env use 3.10.5 (or python)
poetry install
cd server
poetry run python main.py
```

## Docs

- [API Spec / Stoplight (TODO)](#)
  - Or you can see [openapi schema at development server](http://localhost:8000/docs)
- [Detailed spec / Whimsical (TODO)](#)
