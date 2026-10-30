[branch]: https://github.com/Juniper/nita/tree/26.10
[readme]: https://github.com/Juniper/nita/blob/26.10/README.md

# NITA Robot 26.10

Welcome to NITA, an open source platform for automating the building and testing of complex networks.

# Release Notes

Please refer to the [README][readme] for more details.

# Installing

The simplest way to install nita-robot is by installing nita, which can be done by running the ``install.sh`` script located and in the parent [nita repo][branch] as described [here][readme].

## Installing as a Python package

The keyword library and resource files can also be installed without the container, for use from your own Robot Framework project:

```
pip install "nita-robot @ git+https://github.com/Juniper/nita-robot.git@main"
```

Then, in a suite or resource file:

```
*** Settings ***
Library     pybot_jrouter    user=${USER}    target=${HOST}    password=${PASSWORD}    WITH NAME    r1
Resource    nita_robot/device_resources.txt
Resource    nita_robot/show_cmd_keywords.txt
```

Robot Framework finds the resource files on the Python module search path, so no ``--pythonpath`` or absolute paths are needed. The container-specific variables files in ``robot-resources/variables_file`` are not included in the package.

## Accessing the container

You can access the nita-robot container via the shell, simply be running the following command:

```
user@host$ nita-cmd robot cli
If you don't see a command prompt, try pressing enter.
nita-robot:~# exit
exit
pod "nita-robot" deleted
user@host$
```

# Copyright

Copyright 2024, Juniper Networks, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
