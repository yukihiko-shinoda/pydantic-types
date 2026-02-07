FROM futureys/claude-code-python-development:20260201121000
COPY pyproject.toml uv.lock /workspace/
# - Installation fails on Python 3.14 · Issue #327 · PyCQA/docformatter
#   https://github.com/PyCQA/docformatter/issues/327
RUN uv sync --python 3.13
COPY . /workspace
