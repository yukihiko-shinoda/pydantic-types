FROM node:24.3.0-bookworm-slim
WORKDIR /workspace
COPY --from=ghcr.io/astral-sh/uv:0.7.15 /uv /uvx /bin/
# The uv command also errors out when installing semgrep:
# - Getting semgrep-core in pipenv · Issue #2929 · semgrep/semgrep
#   https://github.com/semgrep/semgrep/issues/2929#issuecomment-818994969
ENV SEMGREP_SKIP_BIN=true
COPY pyproject.toml uv.lock /workspace/
RUN uv sync
COPY . /workspace
ENTRYPOINT [ "uv", "run" ]
CMD ["pytest"]
