# ********************************************************
#
# Project: nita-robot
#
# Copyright (c) Juniper Networks, Inc., 2021. All rights reserved.
#
# Notice and Disclaimer: This code is licensed to you under the Apache 2.0 License (the "License"). You may not use this code except in compliance with the License. This code is not an official Juniper product. You can obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0.html
#
# SPDX-License-Identifier: Apache-2.0
#
# Third-Party Code: This code may depend on other components under separate copyright notice and license terms. Your use of the source code for those components is subject to the terms and conditions of the respective license as noted in the Third-Party source code file.
#
# ********************************************************

FROM python:3.11-alpine3.23 AS builder

RUN apk add --no-cache \
    build-base cargo libffi-dev libxml2-dev libxslt-dev openssl-dev

COPY requirements.txt /tmp/requirements.txt
RUN python -m venv /opt/venv \
 && /opt/venv/bin/pip install --no-cache-dir --upgrade pip \
 && /opt/venv/bin/pip install --no-cache-dir -r /tmp/requirements.txt \
 && /opt/venv/bin/pip check

FROM python:3.11-alpine3.23

RUN apk add --no-cache libffi libxml2 libxslt openssl

COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN mkdir -p /usr/share/nita-robot
COPY robot-resources /usr/share/nita-robot/robot-resources

LABEL net.juniper.framework="NITA"
LABEL org.opencontainers.image.source="https://github.com/Juniper/nita-robot"
