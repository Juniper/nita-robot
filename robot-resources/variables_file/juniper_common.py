#!/usr/bin/env python3
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

# ANSIBLE variables
import yaml
from os import walk

def parse_ansible_vars(group_vars, host_vars):
    gf = []
    for (dirpath, dirnames, filenames) in walk(group_vars):
        gf.extend(filenames)
        break

    hf = []
    for (dirpath, dirnames, filenames) in walk(host_vars):
        hf.extend(filenames)
        break

    av = {}
    av['group_vars'] = {}
    for i in gf:
        f = open(group_vars + "/" + i, "r")
        y = yaml.load(f, Loader=yaml.SafeLoader)
        f.close()
        av['group_vars'][i] = y
    av['host_vars'] = {}
    for i in hf:
        f = open(host_vars + "/" + i, "r")
        y = yaml.load(f, Loader=yaml.SafeLoader)
        f.close()
        av['host_vars'][i] = y

    return av
