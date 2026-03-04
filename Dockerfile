FROM nikolaik/python-nodejs:python3.13-nodejs20 AS base

# Setup env
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONFAULTHANDLER=1

FROM base AS build

COPY . /app/
WORKDIR /app

RUN python -m venv .venv && ./.venv/bin/python -m pip install -r requirements.txt

FROM build AS submodule

# Initialize, update, and build submodules
WORKDIR /app/fasset-bots
RUN git submodule update --init --recursive && yarn install --frozen-lockfile && yarn build && yarn cache clean;

FROM base AS runner

# set workdir
WORKDIR /app

# Copy virtual env from base stage
COPY --from=build /app/.venv ./.venv
ENV PATH="./.venv/bin:$PATH"

# Copy submodule
COPY --from=submodule /app/fasset-bots ./fasset-bots

# Copy python executables
COPY --from=build /app/src/ ./src/
COPY --from=build /app/contracts ./contracts/
COPY --from=build /app/scripts ./scripts

# copy entrypoint
COPY --from=build /app/entrypoint.sh ./entrypoint.sh
RUN chmod +x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]