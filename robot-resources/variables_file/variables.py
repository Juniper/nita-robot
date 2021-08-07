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

import importlib.util
import sys

spec = importlib.util.spec_from_file_location("juniper_common", "/usr/share/nita-robot/robot-resources/variables_file/juniper_common.py")
module = importlib.util.module_from_spec(spec)
sys.modules["juniper_common"] = module
spec.loader.exec_module(module)

import juniper_common

import os
cwd = os.getcwd()

# import ansible variables
group_vars = cwd + "/../group_vars"
host_vars = cwd + "/../host_vars"

# barf if you can't find the directories
if (os.path.isdir(group_vars) == False) :
    raise Exception("Error, can't find directory: " + group_vars + " in " + cwd)
if (os.path.isdir(host_vars) == False) :
    raise Exception("Error, can't find directory: " + host_vars + " in " + cwd)

# parse the files
av = juniper_common.parse_ansible_vars(group_vars, host_vars)

# populate variables
user = av['group_vars']['all.yaml']['netconf_user']
password = av['group_vars']['all.yaml']['netconf_passwd']

# set the management ip variables i.e. vmx1_mgmt_ip = "100.123.1.0"
for key, value in iter(av['host_vars'].items()):
    if 'management_interface' in value.keys():
        ip = value['management_interface']['ip']
        exec(key.replace("-", "_").replace(".yaml","") + '_mgmt_ip = "' + ip + '"')

# core interface ip variables for use in tests
# create ci_vmx1_ge_0_0_0, etc
for key, value in iter(av['host_vars'].items()):
    if 'core_interfaces' in value.keys():
        for i in value['core_interfaces']:
            hname = key.replace("-","_").replace(".yaml", "")
            iname = i['int'].replace("/","_").replace("-","_")
            ip = i['ip']
            exec('ci_' + hname + '_' + iname + '=' + '"' + ip + '"')
