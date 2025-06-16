FROM python:3.13.4-slim-bookworm AS production
WORKDIR /workspace
RUN pip install --no-cache-dir uv==0.7.12
# The uv command also errors out when installing semgrep:
# - Getting semgrep-core in pipenv · Issue #2929 · semgrep/semgrep
#   https://github.com/semgrep/semgrep/issues/2929#issuecomment-818994969
COPY pyproject.toml uv.lock /workspace/
ENV SEMGREP_SKIP_BIN=true
RUN uv sync
COPY . /workspace
ENTRYPOINT [ "uv", "run" ]
CMD ["pytest"]
