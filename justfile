lint:
    uv run ruff check --fix
    uv run ruff format

typing:
    uv run basedpyright

run:
    uv run -m src.main
