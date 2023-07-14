FROM python:3.9-slim-buster

RUN adduser --disabled-password pynecone

ENV NODE_VERSION=v20.0.0
ENV RXCONFIG_DOCKER=rxconfig_docker.py

ENV LANG=C.UTF-8 \
  LC_ALL=C.UTF-8 \
  PATH="${PATH}:/root/.poetry/bin"

RUN apt-get update && \
  apt-get install -y --no-install-recommends \
  curl \
  xz-utils \
  unzip \
  vim \
  openssh-server openssh-client \
  && rm -rf /var/lib/apt/lists/*

RUN mkdir -p -m 0700 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts

# Download latest nodejs binary
RUN curl https://nodejs.org/dist/${NODE_VERSION}/node-${NODE_VERSION}-linux-x64.tar.xz -O

# Extract & install
RUN tar -xf node-${NODE_VERSION}-linux-x64.tar.xz
RUN ln -s /node-${NODE_VERSION}-linux-x64/bin/node /usr/local/bin/node
RUN ln -s /node-${NODE_VERSION}-linux-x64/bin/npm /usr/local/bin/npm
RUN ln -s /node-${NODE_VERSION}-linux-x64/bin/npx /usr/local/bin/npx  

COPY pyproject.toml ./

# Install Poetry
RUN curl -sSL https://install.python-poetry.org | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

RUN --mount=type=ssh poetry install --no-root --without dev

CMD mkdir -p /app
COPY --chown=pynecone . /app
COPY --chown=pynecone $RXCONFIG_DOCKER /app/rxconfig.py
USER pynecone
WORKDIR /app
ENV BUN_INSTALL="/app/.bun"
RUN reflex init

CMD ["reflex","run" , "--env", "prod"]

EXPOSE 3000
EXPOSE 8000