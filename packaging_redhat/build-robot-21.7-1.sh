#!/bin/bash

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

# stop the script if a command fails
set -e

PACKAGE=nita-robot-4.1
VERSION=21.7
RELEASE=1

# cleanup version if the directory name is used
VTMP="${VERSION#$PACKAGE-}"
VERSION=${VTMP%/}


if [[ "x$VERSION" == "x" ]]; then
    echo "Must provide package version"
    exit 1
fi

if [ ! -d ${PACKAGE}-${VERSION}-${RELEASE} ]; then
    echo "Directory ${PACKAGE}-${VERSION}-${RELEASE} does not exist"
fi

# installing docker-ce on host
if (yum list installed | grep docker-ce) >/dev/null 2>&1; then
    echo "docker-ce already installed"
else
    yum install -y yum-utils rpm-build
    yum-config-manager \
        --add-repo \
        https://download.docker.com/linux/centos/docker-ce.repo
    yum update -y
    yum install -y docker-ce --nobest
    systemctl start docker
fi

SOURCE_DIR=${PACKAGE}-${VERSION}-${RELEASE}/SOURCES

# copy cli scripts
SCRIPTSDIR=${SOURCE_DIR}/${PACKAGE}-${VERSION}/usr/local/bin
mkdir -p ${SCRIPTSDIR}
install -m 755 ../cli_scripts/* ${SCRIPTSDIR}

# pull all the required containers
IMAGEDIR=${SOURCE_DIR}/${PACKAGE}-${VERSION}/usr/share/${PACKAGE}/images
mkdir -p ${IMAGEDIR}
(
    cd ..
    ./build_container.sh
)
docker save juniper/nita-robot:21.7-1 | gzip > ${IMAGEDIR}/nita-robot-21.7.tar.gz

# Create a tarball of with source
(
    cd ${SOURCE_DIR}
    tar czf ${PACKAGE}-${VERSION}.tar.gz ${PACKAGE}-${VERSION}
)

# Build rpm file
export RPM_BUILD_DIR="${PWD}/${PACKAGE}-${VERSION}-${RELEASE}"
cp .rpmmacros ~
rpmbuild -ba ${PACKAGE}-${VERSION}-${RELEASE}/SPECS/${PACKAGE}.spec
