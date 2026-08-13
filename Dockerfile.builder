# uhta goal-oriented coding agent (Assignment 5).
#
# A SEPARATE image from the A3 crew's `Dockerfile`, deliberately. That one is
# part of a graded, tagged submission and its build-time gate is `run_crew.py
# --selftest`; nothing here should be able to break it.
#
# Two things this image needs that the crew image does not:
#
#   1. builder/ and content/. The A3 Dockerfile COPYs only crew/, prompts/,
#      blackboard/ and tests/ — neither the A4 content pipeline nor this one was
#      ever in it.
#
#   2. NODE. `builder/generate.py` runs two checks that need it: `node --check`
#      on the patched script, and — the important one — a headless EXECUTION of
#      the patched build's own acceptance self-test. Without node the first
#      degrades to a brace-count and the second reports SKIPPED, which loses the
#      check that caught a patch that parsed cleanly and killed the build on
#      load. An image that silently drops it is worse than no image.
FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

RUN apt-get update \
 && apt-get install -y --no-install-recommends nodejs \
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY crew/       ./crew/
COPY content/    ./content/
COPY builder/    ./builder/
COPY prompts/    ./prompts/
COPY blackboard/ ./blackboard/
COPY tests/      ./tests/
COPY tools/      ./tools/
COPY run_crew.py run_content.py run_builder.py ./
COPY README.md README-A5.md ARCHITECTURE.md ./

RUN mkdir -p /app/out

# Build-time proof, same discipline as the crew image: if the deterministic half
# of this pipeline cannot pass in this image, the BUILD fails rather than the
# first run. This also proves node is present and usable — J2, J9, J10 and J11
# all shell out to it, and J9 executes the patched build end to end.
RUN node --version && python3 run_builder.py --selftest

# Neither of the other two pipelines is disturbed by adding this one; prove it
# here rather than asserting it in a README.
RUN python3 run_content.py --selftest

ENTRYPOINT ["python3", "run_builder.py"]
CMD ["--selftest"]
