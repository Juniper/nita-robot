# NITA Robot 21.7

Welcome to NITA 21.7.

Packages built from this branch will be nita-*-21.7-x where x is the packaging release.
This branch also contains patches from other branches or minor modifications as required to support the stability and usability of the release.
There are also some backwards compatibility packages here for ansible and robot that allow projects written for NITA 3.0.7 to work without having to make any changes.

Note that NITA 21.7 backward compatible with NITA 20.10 projects, provided the correct ansible and robot containers are installed.

# Copyright

Copyright 2021, Juniper Networks, Inc.

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

# Stable releases

The idea here is to provide multiple NITA based projects with a firm foundation that they can use to focus on solving customer problems rather than continually tweaking the underlying software.

It allows NITA projects to declare exactly which version of NITA they are compatible with.

Projects must explicitly use the versions of the containers provided by this package in order to avoid docker attempting to download from the registry.
No containers tagged as "latest" are provided by the package.

# Installing

## Dependencies

NITA depends on docker-ce and docker-compose.

* For the **docker-ce** instalation the instructions found here: https://docs.docker.com/engine/install/
* It is recomended to follow this steps after installing docker-ce: https://docs.docker.com/engine/install/linux-postinstall/
* To install **docker-compose** follow the instructions found here: https://docs.docker.com/compose/install/

## Installation

If you do not have the the required package files for your system, .deb for Ubuntu or .rpm for Centos refer to [BUILD.md](./BUILD.md) file for instructions on how to generate these files.

### Ubuntu

If you have been provided with the .deb package file, then follow the instructions provided in the [Dependencies](##Dependencies) section above and then run the following command:

```bash
sudo apt-get install ./nita-robot-4.1-21.7-1.deb
```

### Centos

If you have been provided with the .rpm package file, then follow the instructions provided in the [Dependencies](##Dependencies) section above and then run the following command:

```bash
sudo yum install ./nita-robot-4.1-21.7-1.noarch.rpm
```

# Misc

For more information on NITA releases refer to the [README.md](https://github.com/Juniper/nita-webapp/blob/main/README.md) for the NITA Webapp <link to that>
