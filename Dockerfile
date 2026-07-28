# uhta rules-pipeline crew.
#
# The image carries the crew AND the blackboard, because the Playtester executes
# the vendored reference simulator (blackboard/sim/harness.py) as a subprocess —
# there is no external service to reach and no model weights to fetch. A container
# with no ANTHROPIC_API_KEY can still run `--selftest` and `--mock-llm` to
# completion, which is the point of both modes.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY crew/       ./crew/
COPY prompts/    ./prompts/
COPY blackboard/ ./blackboard/
COPY tests/      ./tests/
COPY run_crew.py README.md ARCHITECTURE.md ./

# out/ is a mount point in docker-compose; create it so a bare `docker run`
# without a volume still works.
RUN mkdir -p /app/out

# Build-time proof that the deterministic half of the crew works in this image:
# the blackboard, the validation gate, and a real harness execution. If the sim
# cannot run here, the build fails rather than the first run.
RUN python3 run_crew.py --selftest

ENTRYPOINT ["python3", "run_crew.py"]
CMD ["--selftest"]
