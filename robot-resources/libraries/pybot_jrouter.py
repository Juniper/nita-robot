#!/usr/bin/env python3
# ********************************************************                                                                                     #                                                                                                                                              # Project: nita-webapp
#
# Copyright (c) Juniper Networks, Inc., 2021. All rights reserved.
#                                                                                                                                              # Notice and Disclaimer: This code is licensed to you under the Apache 2.0 License (the "License"). You may not use this code except in compliance with the License. This code is not an official Juniper product. You can obtain a copy of the License at https://www.apache.org/licenses/LICENSE-2.0.html
#
# SPDX-License-Identifier: Apache-2.0
#
# Third-Party Code: This code may depend on other components under separate copyright notice and license terms. Your use of the source code for those components is subject to the terms and conditions of the respective license as noted in the Third-Party source code file.
#
# ********************************************************

# xml specific
from lxml import etree
from lxml.builder import E
import xml.etree.ElementTree as ET
import xml.dom.minidom
import lxml

# stdlib
from io import StringIO
import re
import subprocess as sub
from subprocess import Popen, PIPE
from subprocess import check_call
import os
import sys
import pdb
import errno
import time
from datetime import datetime
from datetime import date, timedelta
from time import sleep
from pprint import pprint
import logging
import hashlib
from socket import error as SocketError
import errno
import signal
from itertools import *
import csv
import tempfile

#third-party
import xmltodict
import yaml
import paramiko
# import ncclient.transport.errors as NcErrors
# import ncclient.operations.errors as TError
import jinja2
import csv
from select import select
import ftplib
import logging.handlers

# junos-ez
from jnpr.junos.utils.scp import SCP
from jnpr.junos.utils.fs import FS
from jnpr.junos.exception import *
from jnpr.junos.utils.config import Config
from jnpr.junos.utils.sw import SW
from jnpr.junos.utils.start_shell import StartShell
from jnpr.junos.factory import loadyaml
from jnpr.junos.op.routes import RouteTable
from jnpr.junos import Device
from jnpr.junos import *

# Robot libraries

from robot.libraries.BuiltIn import BuiltIn
from robot.libraries.OperatingSystem import OperatingSystem
from robot.api import logger

# Global Variables
timestamp = datetime.now().strftime("%Y-%m-%d")
timestamp2 = datetime.now().strftime("%Y-%m-%d-%H-%M-%S.%f")[:-3]
timestamp3 = datetime.now().strftime("%H_%M_%S")
timestamp4 = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")

# Global variables for shell connection

_SHELL_PROMPT = '% '
_JUNOS_PROMPT = '> '
_BASH_PROMPT = '?'
_SELECT_WAIT = 0.1
_RECVSZ = 1024


class ContinuableError(RuntimeError):
    ROBOT_CONTINUE_ON_FAILURE = True

class FatalError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True

class pybot_jrouter(object):

    ROBOT_LIBRARY_SCOPE = 'TEST SUITE'

    ROBOT_LISTENER_API_VERSION = 2

# -----------------------------------------------------------------------
# CONSTRUCTOR
# -----------------------------------------------------------------------
    def __init__(self, **kvargs):

        # Setting credentials
        self.user = kvargs['user']
        self.target = kvargs['target']
        self.password = kvargs['password']

        try:
            self.port = int(kvargs['port'])
        except KeyError:
            self.port = 22
        except ValueError as v_error:
            print("WARN Variable value problems: %s" %v_error)
            raise ContinuableError("Variable value problems: %s" %v_error)

        self.ROBOT_LIBRARY_LISTENER = self
        self._conn = Device(user=self.user, host=self.target, password=self.password, port=self.port, gather_facts=False)

# -----------------------------------------------------------------------
# FUNCTIONS START HERE
# -----------------------------------------------------------------------

    def open_connection(self):

        try:
            self._conn.open(auto_probe=10)
            self._conn.timeout = 120*120
            return self
        except ConnectError as c_error:
            print("WARN Connection problems %s target: %s port: %s" % (c_error, self.target, self.port))
            raise ContinuableError("Connection problems %s target: %s port: %s" %(c_error, self.target, self.port))

    def close_connection(self):

        try:
            self._conn.close()
            return self
        except ConnectError as c_error:
            print("WARN Connection problems %s" %c_error)
            raise ContinuableError("Connection problems %s" %c_error)

    def load_configuration_from_file(self, synchronize=True, overwrite=False, **kvargs):

        """
            Function that load configuration on router from a file

            path : where the configuration file is located

            format:  possible values 'set' or 'xml' or 'bracket'  (so far only format 'set' is supported)

        """
        #overwrite = kvargs.pop ('overwrite',False)
        args = dict(data='')
        args.update(kvargs)
        if overwrite:
            return self.load_configuration(overwrite=True, **args)
        else:
            return self.load_configuration(overwrite=False, **args)

    def load_configuration_from_template(self,
                                            commit_comment='pybot_jrouter_load_configuration_from_template',
                                            format='set',
                                            conf_mode='exclusive',
                                            overwrite=False,
                                            merge=False,
                                            synchronize=True,
                                            force_synchronize=False,
                                            full=False,
                                            print_conf_diff=False,
                                            print_conf_detail=False,
                                            **kvargs):

        """
            # General Options:
                #     - format can be conf/set/xml
                #     - print_conf_diff will print the diff if desired
                #     - print_conf_detail will print the committed configuration if desired
                # Configuration Options:
                #    - conf_mode: can be exclusive/private/dynamic/batch
                # Load Options:
                #    - overwrite: Determines if the contents completely replace the existing configuration.  Default is False
                #    - merge: If set to True will set the load-config action to merge the default load-config action is 'replace'
                # Commit Options:
                #    - kvargs synchronize: Default True. On dual control plane systems, requests that the candidate configuration on one control plane be copied to the other control plane, checked for correct syntax, and committed on both Routing Engines. Default is True.
                #    - kvargs force_synchronize: Default False. On dual control plane systems, forces the candidate configuration on one control plane to be copied to the other control plane. Default is False
                #    - kvargs full: Default False. When True requires all the daemons to check and evaluate the new configuration
        """
        print("*INFO* Host %s|load_configuration_from_template|General Options: format=%s, print_conf_diff=%s, print_conf_detail=%s" % (self.target, format, print_conf_diff, print_conf_detail))

        synchronize = True
        force_synchronize = False
        full = False

        if 'force_synchronize' in kvargs.keys():
            force_synchronize = kvargs['force_synchronize']
        if 'synchronize' in kvargs.keys():
            synchronize = kvargs['synchronize']
        if 'full' in kvargs.keys():
            full = kvargs['full']

        ##Hidden variable: DO NOT USE  DO NOT EDIT
        #It will be set to True ONLY if routers.load_configuration_from_template_in_parallel is executed
        if 'parallel' in kvargs.keys():
            parallel = kvargs['parallel']
        else:
            parallel = False

        if force_synchronize:
            synchronize = True
            print("*INFO* Host %s|load_configuration_from_template|Force Synchronized Commit requested" % (self.target))
        if synchronize:
            print("*INFO* Host %s|load_configuration_from_template|Synchronized Commit requested" % (self.target))
        if full:
            print("*INFO* Host %s|load_configuration_from_template|Commit Full requested" % (self.target))
        print("*INFO* Host %s|load_configuration_from_template|Load Options: merge=%s, overwrite=%s" % (self.target, merge, overwrite))

        if format == 'set' and overwrite:
            overwrite = False
            print("*WARN* Host %s|load_configuration_from_template|Not possible to override the configuration with format=set. Overwriting disabled." % (self.target))

        yaml_file = kvargs['template_vars']
        # Loading files and rendering
        myvars = yaml.load(open(yaml_file).read())

        loadResp = ''
        commitResp = False

        print("*INFO* Host %s|load_configuration_from_template|Initializing variables. template_path=%s." % (self.target, kvargs['jinja2_file']))
        try:
            #Unlock/close configuration is managed by Config context manager
            with Config(self._conn, mode=conf_mode) as candidate:
                begin_load_datetime = datetime.now()
                if overwrite:
                    loadResp = candidate.load(template_path=kvargs['jinja2_file'], template_vars=myvars, format=format, overwrite=True, merge=merge)
                else:
                    loadResp = candidate.load(template_path=kvargs['jinja2_file'], template_vars=myvars, format=format, overwrite=False, merge=merge)
                finish_load_datetime = datetime.now()
                if loadResp.find("ok") is None:
                    print("*WARN* Host %s|load_configuration_from_template|Load Response did not throw an exception but something unexpected occurred: %s" % (self.target, etree.tostring(loadResp)))
                    return False

                if print_conf_diff:
                    try:
                        print('*INFO* Host %s|load_configuration_from_template|DIFF configuration to be committed  %s' % (self.target, candidate.diff()))
                    except lxml.etree.XMLSyntaxError as error:
                        print("*WARN* Host %s|load_configuration_from_template|Unable to retrieve the DIFF configuration to be committed. Printout will be skipped, trying to commit....: %s" % (self.target, error))

                begin_commit_datetime = datetime.now()
                if print_conf_detail:
                    try:
                        #begin_commit_datetime=datetime.now()
                        commitResp = candidate.commit(comment=commit_comment, sync=synchronize, force_sync=force_synchronize, full=full, detail=True)
                        #finish_commit_datetime=datetime.now()
                        print('*INFO* Host %s|load_configuration_from_template|Configuration to be committed:  %s' % (self.target, etree.tostring(commitResp)))
                    except lxml.etree.XMLSyntaxError as error:
                        print("*WARN* Host %s|load_configuration_from_template|Unable to retrieve the committed configuration. Printout will be skipped, check the node or try again with print_conf_detail=False....: %s" % (self.target, error))
                        return False
                else:
                    begin_commit_datetime = datetime.now()
                    commitResp = candidate.commit(comment=commit_comment, sync=synchronize, force_sync=force_synchronize, full=full, detail=False)
                    finish_commit_datetime = datetime.now()
        except LockError as lockError:
            print("*WARN* Host %s|load_configuration_from_template|Problems locking configuration: %s" % (self.target, lockError))
            if parallel:
                return "Exception %s:" %lockError
            else:
                raise FatalError("Host %s|load_configuration_from_template|Unable to lock configuration.....exiting: %s" % (self.target, lockError))
        except (RpcError, RpcTimeoutError) as rpcError:
            #warnings severity is already being ignored in the Config context manager
            print("*WARN* Host %s|load_configuration_from_template|Problems opening configuration: %s" % (self.target, rpcError))
            if parallel:
                return "Exception %s:" %rpcError
            else:
                raise FatalError("Host %s|load_configuration_from_template|Unable to open configuration.....exiting: %s" % (self.target, rpcError))
        except ConfigLoadError as configError:
            print("*WARN* Host %s|load_configuration_from_template|Template %s|Problems loading the configuration: %s.....exiting" % (self.target, kvargs['jinja2_file'], configError))
            if print_conf_diff:
                try:
                    print('*INFO* Host %s|load_configuration_from_template|DIFF configuration to be committed  %s' % (self.target, candidate.diff()))
                except lxml.etree.XMLSyntaxError as error:
                    print("*WARN* Host %s|load_configuration_from_template|Unable to retrieve the DIFF configuration to be committed. Printout will be skipped, trying to commit....: %s" % (self.target, error))
            if parallel:
                return "Exception %s:" %configError
            else:
                raise FatalError("Host %s|load_configuration_from_template|Template %s|Unable to load the configuration.....exiting: %s" % (self.target, kvargs['jinja2_file'], configError))
        except CommitError as commitError:
            print("*WARN* Host %s|load_configuration_from_template|Template %s|Problems committing the configuration: %s.....exiting" % (self.target, kvargs['jinja2_file'], commitError))
            if parallel:
                return "Exception %s:" %commitError
            else:
                raise FatalError("Host %s|load_configuration_from_template|Template %s|Unable to commit the configuration.....exiting: %s" % (self.target, kvargs['jinja2_file'], commitError))
        except UnlockError as unlockError:
            print("*WARN* Host %s|load_configuration_from_template|Problems unlocking the configuration: %s.....exiting" % (self.target, unlockError))
            if parallel:
                return "Exception %s:" %unlockError
            else:
                raise FatalError("Host %s|load_configuration_from_template|Unable to unlock the configuration.....exiting: %s" % (self.target, unlockError))
        except Exception as error:
            if 'Opening and ending tag mismatch: routing-engine ' in error:
                print('*INFO* Host %s|load_configuration_from_template|%s' %(self.target, error))
                pass
                return True
            else:
                print("*WARN* Host %s|load_configuration_from_template|An unhandled exception occurred: %s.....exiting" % (self.target, error))
                if parallel:
                    return "Exception %s:" %error
                else:
                    raise FatalError("Host %s|load_configuration_from_template|Unhandled Exception occurred.....exiting: %s" % (self.target, error))

        diff_load_time = finish_load_datetime - begin_load_datetime
        diff_commit_time = finish_commit_datetime - begin_commit_datetime
        total_time = finish_commit_datetime - finish_load_datetime
        print('*INFO* Host %s|load_configuration_from_template|Configuration successfully committed|Template: %s|Load Time: %s|Commit Time: %s| Total Time: %s' % (self.target, kvargs['jinja2_file'], self.pretty_time_delta(diff_load_time.seconds), self.pretty_time_delta(diff_commit_time.seconds), self.pretty_time_delta(total_time.seconds)))

        return True


    def load_configuration(self, commit_comment='__JRouter__', path=None, overwrite=False, **kvargs):

        """
            Function that load configuration on router

            **kvargs format:set|text|xml
                        data: data to load in the router
        """

        data = kvargs['data']
        format = kvargs['format']


        if ((format == "set") or (format == "xml") or (format == "conf") or (format == "text") or (format == "txt")):
            # Checking if this attribute was already attached to Device

            # This is required if we are going to change configuration several times
            if hasattr(self._conn, "candidate"):
                pass
            else:
                self._conn.bind(candidate=Config)
            try:
                self._conn.candidate.lock()
            except LockError as l_error:

                print("*WARN* Problems locking configuration: %s" % (l_error))
                raise FatalError("Problems locking configuration,exiting...")
                return False
            try:
                if ((data == "") and (path != None)):
                    if overwrite:
                        self._conn.candidate.load(path=path, format=format, overwrite=True)  # Load configuration from file
                    else:
                        self._conn.candidate.load(path=path, format=format)
                else:
                    if overwrite:
                        self._conn.candidate.load(data, format=format, overwrite=True)  # Load configuration from file
                    else:
                        self._conn.candidate.load(data, format=format)
            except ConfigLoadError as error:

                # hack to avoid return an error whenever config load get a warning
                if error.rpc_error['severity'] == 'warning':
                    print("*INFO* Problems loading configuration: %s" % (error.rpc_error['message']))

            except lxml.etree.XMLSyntaxError as error:
                print("*WARN* Problems loading configuration: %s" % (error))
                raise FatalError("Problems loading configuration,exiting...")


            print('*INFO* Configuration to be commited  %s' % (self._conn.candidate.diff()))
            try:
                self._conn.candidate.commit(comment=commit_comment)
                self._conn.candidate.unlock()
                return True
            except (CommitError, LockError) as err:
                #print err
                self._conn.candidate.rollback()
                print("*WARN* Problems commiting configuration: %s" % (err))
                raise FatalError("Error commiting configuration, exiting....")
        else:
            raise FatalError("Expected result is True but was False,test will go on")
            return False

    def jsnap(self, **kvargs):


        variables = BuiltIn().get_variables()

        # Assigning kvargs

        section = None


        if 'section' in kvargs.keys():
            section = kvargs['section']
        tag = kvargs['tag']
        snaptype = kvargs['snaptype']
        test = kvargs['test']
        mode = kvargs['mode']
        output_directory = variables['${path}']
        test_case = variables['${testname}']

        tmp_dir = tempfile.mkdtemp(prefix='_')
        dirpath = output_directory + "/" + tmp_dir + "/" + test_case.replace(" ","_") + "/" + self.target + "/snapshot/"

        #PARENT_ROOT=os.path.abspath(os.path.join(self.logdir, os.pardir))
        #GRANDPA=os.path.abspath(os.path.join(PARENT_ROOT, os.pardir))

        if not os.path.exists(dirpath):
            os.makedirs(dirpath, mode=0o777)

        timestamp = datetime.now().strftime("%Y-%m-%d")

        if snaptype == "snap":

            if section:
                cmd = 'jsnap --'+ snaptype + " " + timestamp + '_'+ tag + ' -l ' + self.user + ' -p ' + self.password + ' -t ' + self.target + ' -s' + section + ' ' + test
            else:
                cmd = 'jsnap --'+ snaptype + " " + timestamp + '_'+ tag + ' -l ' + self.user + ' -p ' + self.password + ' -t ' + self.target + ' ' + test
            print("Executing: %s" %cmd)
            jsnap_command = sub.Popen(cmd, stdout=sub.PIPE, stderr=sub.PIPE, shell=True, cwd=dirpath)
            output, errors = jsnap_command.communicate()
            if ((("Exiting." in errors)) or("Unable to connect to device: " in errors) or ("jsnap: not found" in errors) or ("appears to be missing" in output)):
                print(output)
                print(errors)
                raise FatalError("Unable to execute jsnap.....exiting")
            else:
                return True
            print(output, errors)
            return True

        elif snaptype == "snapcheck":

            if section:
                cmd = 'jsnap --'+ snaptype + " " + timestamp + '_'+ tag + ' -l ' + self.user + ' -p ' + self.password + ' -t ' + self.target + ' -s' + section + ' ' + test
            else:
                cmd = 'jsnap --'+ snaptype + " " + timestamp + '_'+ tag + ' -l ' + self.user + ' -p ' + self.password + ' -t ' + self.target  + ' ' + test
            print("Executing: %s" %cmd)
            jsnap_command = sub.Popen(cmd, stdout=sub.PIPE, stderr=sub.PIPE, shell=True, cwd=dirpath)
            output, errors = jsnap_command.communicate()

            print(output)
            print(errors)

            if ((("Exiting." in errors)) or("Unable to connect to device: " in errors) or ("jsnap: not found" in errors) or ("appears to be missing" in output)):

                print(output)
                print(errors)
                raise FatalError("Unable to execute jsnap.....exiting")

            else:
                if mode == "strict":
                    if "ERROR" in output or "ERROR" in errors:
                        raise FatalError("ERROR found in jsnap mode strict.....exiting")
                    else:
                        return True
                else:
                    return True

        elif snaptype == "check":

            if section:
                cmd_check = 'jsnap --'+ snaptype + " " + timestamp + '_pre' + ',' +  timestamp + '_post' + ' -l ' + self.user + ' -p ' + self.password + ' -t ' + self.target  + ' -s' + section + ' ' + test
            else:
                cmd_check = 'jsnap --'+ snaptype + " " + timestamp + '_pre' + ',' +  timestamp + '_post' + ' -l ' + self.user + ' -p ' + self.password + ' -t ' + self.target  + ' '  + test
            print("Executing: %s" %cmd_check)
            jsnap_command = sub.Popen(cmd_check, stdout=sub.PIPE, stderr=sub.PIPE, shell=True, cwd=dirpath)
            output, errors = jsnap_command.communicate()
            print(output)
            print(errors)

            if ((("Exiting." in errors)) or("Unable to connect to device: " in errors) or ("jsnap: not found" in errors) or ("appears to be missing" in output)):

                print(output)
                print(errors)
                raise FatalError("Unable to execute jsnap.....exiting")

            else:
                if mode == "strict":
                    if "ERROR" in output or "ERROR" in errors:
                        raise FatalError("ERROR found in jsnap mode strict.....exiting")
                    else:
                        return True
                else:

                    return True
        else:
            raise FatalError("Invalid snap type.....exiting")

    def rescue_configuration(self, **kvargs):

        """
            Function that issues Save/Load a Rescue Configuration

        """

        if 'action' in kvargs.keys():
            action = kvargs['action']

        # Saving rescue configuration
        if action == 'save':
            try:
                self._conn.rpc.request_save_rescue_configuration()
            except RpcError as err:
                rpc_error = err.__repr__()
                print(rpc_error)
            return self
        # Checking if this attribute was already attached to Device
        if hasattr(self._conn, "candidate"):
            pass
        else:
            self._conn.bind(candidate=Config)

        # Locking configuration
        try:
            self._conn.candidate.lock()
        except LockError as l_error:
            print("*WARN* Problems locking configuration: %s" % (l_error))
            raise FatalError("Unable to lock configuration.....exiting")

        # Loading rescue configuration
        if action == 'load':
            try:
                self._conn.rpc.load_configuration({'rescue': 'rescue'})
            except RpcError as err:
                rpc_error = err.__repr__()
                print(rpc_error)
            except ConfigLoadError as error:
                print("*WARN* Problems loading configuration: %s" % (error))
                raise FatalError("Unable to load configuration.....exiting")
            print('*INFO* Configuration to be commited  %s' % (self._conn.candidate.diff()))

            try:
                self._conn.candidate.commit(comment='loading rescue configuration')
                self._conn.candidate.unlock()
                return True

            except (CommitError, LockError) as err:
                print(err)
                raise FatalError("Unable to commit or unlock configuration......exiting")

    def commands_executor(self, **kvargs):

        """
            Function that issues commands

        """

        # Getting built-in variables

        variables = BuiltIn().get_variables()

        regex = ''
        xpath = ''
        if 'xpath' in kvargs.keys():
            xpath = kvargs['xpath']

        if 'regex' in kvargs.keys():
            regex = kvargs['regex']

        command = kvargs['command']
        format = kvargs['format']
        output_directory = variables['${path}']
        root_dir = variables['${OUTPUT_DIR}']
        test_case = variables['${testname}']

        if format == "text":

            tmp_dir = tempfile.mkdtemp(prefix='_')
            if output_directory == None:
                dirpath = "/collector/" + tmp_dir + "/" + timestamp + "/"
            else:
                dirpath = output_directory + "/" + tmp_dir + "/" + test_case.replace(" ", "_") + "/commands"

            # Create directory if does not exist
            if not os.path.exists(dirpath):
                os.makedirs(dirpath, mode=0o777)

            if regex:

                try:
                    cmd_to_execute = self._conn.rpc.cli(command)
                except RpcError as err:
                    rpc_error = err.__repr__()
                    print(xmltodict.parse(rpc_error)['rpc-error']['error-message'])
                    raise FatalError("Error executing RPC,exiting...")

                operations = command.split("|")[1:]
                result_tmp = cmd_to_execute.text
                lines = result_tmp.strip().split('\n')
                for operation in operations:
                    if re.search("count", operation, re.IGNORECASE):
                        print('*INFO* Count: %s lines' % len(lines))
                        return len(lines)
                    match = re.search('match "?(.*)"?', operation, re.IGNORECASE)
                    if match:
                        regex = match.group(1).strip()
                        lines_filtered = []
                        for line in lines:
                            if re.search(regex, line, re.IGNORECASE):
                                lines_filtered.append(line)
                        lines = lines_filtered
                    match = re.search('except "?(.*)"?', operation, re.IGNORECASE)
                    if match:
                        regex = match.group(1).strip()
                        lines_filtered = []
                        for line in lines:
                            if re.search(regex, line, re.IGNORECASE):
                                pass
                            else:
                                lines_filtered.append(line)
                        lines = lines_filtered

                text_matches = re.search(regex, cmd_to_execute.text, re.MULTILINE)

                if text_matches:
                    print(text_matches.groups())
                    return text_matches.groups()
            else:
                print("Executing: %s" %command)

                try:
                    cmd_to_execute = self._conn.rpc.cli(command)

                except RpcError as err:
                    rpc_error = err.__repr__()
                    print(xmltodict.parse(rpc_error)['rpc-error']['error-message'])
                    raise FatalError("Error executing RPC,exiting...")

                #print type(cmd_to_execute)
                if isinstance(cmd_to_execute, bool):
                    return True
                else:
                    cmd_clean = command.replace(" ", "_").replace('_"', '_').replace('"_', '_').replace('"', '').replace("/", "_")
                    filename = timestamp2 + '_'+ self.target  + "_" + cmd_clean + "." + "txt"
                    path = os.path.join(dirpath, filename).replace(root_dir, '.')
                    print("Saving file as: %s" %path)
                    print('*HTML* <a href="%s" target="_blank">%s</a>' % (path, path))

                    try:
                        with open(path, 'w') as file_to_save:
                            file_to_save.write(cmd_to_execute.text)
                        return True
                    except IOError as err:
                        print(err.errno, err.strerror)
                        raise FatalError("Error opening File, exiting...")

        elif format == "xml":

            if xpath:
                print("Executing: %s [%s]" %(command, xpath))

                try:
                    cmd_to_execute = self._conn.rpc.cli(command, format='xml')
                    xml_result = etree.tostring(cmd_to_execute)

                except RpcError as err:
                    rpc_error = err.__repr__()
                    print(xmltodict.parse(rpc_error)['rpc-error']['error-message'])
                    raise FatalError("Error executing RPC, exiting...")

                xpath_result = cmd_to_execute.xpath(xpath)[0].text.strip()

                if xpath_result == None:
                    raise FatalError("XPATH malformed, exiting...")
                else:
                    print(xpath_result)
                    return xpath_result
            else:
                try:
                    cmd_to_execute = self._conn.rpc.cli(command, format='xml')
                    xml_result = etree.tostring(cmd_to_execute)

                except RpcError as err:
                    rpc_error = err.__repr__()
                    print(xmltodict.parse(rpc_error)['rpc-error']['error-message'])
                    raise FatalError("Error executing RPC, exiting...")
                return xml_result
        else:
            raise FatalError("Format not valid, exiting...")

    def save_config_to_file(self, **kvargs):

        directory = kvargs['directory'] + '/' + timestamp4
        print("*INFO* Saving current configuration...")
        file_obj = StartShell(self._conn)
        file_obj.open()
        got = file_obj.run("cli -c 'show configuration | save " + directory + "_config.txt' ")
        file_obj.close()
        print("*INFO* %s" % (got))
        return got[-2].split("'")[1]

    def rollback(self, commit_comment='__JRouter__', **kvargs):

        """
            Function that performs rollback
                rollback_num = number

        """
        rollback_num = kvargs['rollback_num']

        try:
            rollback_num = int(rollback_num)
            if rollback_num > 50:
                raise FatalError("Sorry. 'rollback_num' must lower than 50")
        except Exception as e:
            raise FatalError("Sorry. 'rollback_num' must be an integer.")

        if hasattr(self._conn, "candidate"):
            pass
        else:
            self._conn.bind(candidate=Config)
        try:
            self._conn.candidate.lock()
        except LockError as l_error:
            print("*WARN* Problems locking configuration: %s" % (l_error))
            raise FatalError("Unable to lock configuration... exiting")

        try:
            print("Rolling back configuration....")
            self._conn.candidate.rollback(rollback_num)
            self._conn.candidate.commit(comment=commit_comment)
            self._conn.candidate.unlock()
            return True
        except RpcError as err:
            rpc_error = err.__repr__()
            raise FatalError(xmltodict.parse(rpc_error)['rpc-error']['error-message'])

    def switchover(self):
        """
            Function to perfom RE switchover
        """
        # We need to verify that backup RE is ready before proceed
        b_slot = self.get_slot('backup')
        b_state = self._conn.rpc.get_route_engine_information(slot=b_slot)
        state = b_state.findtext('route-engine/mastership-state')

        if (state != "backup"):
            raise FatalError("Backup RE is not ready")

        try:
            self.open_connection()
            print('Executing switchover to complete the SW upgrade !!!')
            switchover_cmd = self._conn.cli("request chassis routing-engine master switch no-confirm", format='xml', warning=False)
            self.close_connection()
        except ConnectError as c_error:
            raise FatalError(c_error)
        # except TError.TimeoutExpiredError as Terr:
        #     print Terr
        #     pass
        # except NcErrors.SessionCloseError as Serr:
        #     print Serr
        #     pass
        except SocketError as S_err:
            print(S_err)
            pass
        except ConnectClosedError as CC_error:
            print(CC_error)
            pass

        sleep(60)
        try:
            # WA for dealing with in band connections
            print("Re-opening connection.......")
            self._conn.open(auto_probe=900)
            return True
        except ConnectError as c_error:
            raise FatalError(c_error)



    def get_routing_table(self, **kvargs):
        """
            Function that gathers the routing table from a device. It returns the whole routing table if no route is specified.
            If route is specified, next_hop can be also specified and routing table nexthop output will be compared against it.
        """
        try:
            tbl = RouteTable(self._conn)
        except ConnectError as c_error:
            raise FatalError(c_error)

        complete_rt = tbl.get()
        if 'route' in kvargs.keys():
            route = kvargs['route']
        print('route', route)
        if route != 'None':
            single_rt = tbl.get(route)

        # Routing Table dictionary
        rt = {}
        for item in tbl:
            # Remove "RouteTableView:" from item = RouteTableView:0.0.0.0/0
            destination = str(item).split(":")[1]
            rt[destination] = [item.nexthop, item.age, item.via, item.protocol]

        return rt

    def pretty_time_delta(self, seconds):
        sign_string = '-' if seconds < 0 else ''
        seconds = abs(int(seconds))
        days, seconds = divmod(seconds, 86400)
        hours, seconds = divmod(seconds, 3600)
        minutes, seconds = divmod(seconds, 60)
        if days > 0:
            return '%s%dd%dh%dm%ds' % (sign_string, days, hours, minutes, seconds)
        elif hours > 0:
            return '%s%dh%dm%ds' % (sign_string, hours, minutes, seconds)
        elif minutes > 0:
            return '%s%dm%ds' % (sign_string, minutes, seconds)
        else:
            return '%s%ds' % (sign_string, seconds)


    def get_config(self, xml_filter=None):

        if xml_filter is None:
            cnf = self._conn.rpc.get_config()
        else:
            # Should user wants to filter out configuration and extract only a piece of it
            # e.g. SNMP
            #cnf = dev.rpc.get_config(filter_xml=etree.XML('<snmp></snmp>'))
            # interfaces
            #cnf = dev.rpc.get_config(filter_xml=etree.XML('<configuration><interfaces/></configuration>'))
            cnf = self._conn.rpc.get_config(filter_xml=etree.XML(xml_filter))
        #print etree.tostring(cnf)
        config = etree.dump(cnf)
        print(config)
        return config
