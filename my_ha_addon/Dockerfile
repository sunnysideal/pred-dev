ARG BUILD_FROM
FROM $BUILD_FROM

# Set shell
SHELL ["/bin/bash", "-o", "pipefail", "-c"]

# Install requirements
RUN apk add --no-cache \
    python3 \
    py3-pip

# Copy data
COPY run.sh /
RUN chmod a+x /run.sh

COPY app /app
WORKDIR /app

# Install Python requirements
RUN pip3 install --no-cache-dir -r requirements.txt

CMD [ "/run.sh" ]
