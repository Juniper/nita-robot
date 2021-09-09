For the building purpose of a **Package** or **Docker Image** it is recommended to first clone the repo:
```
git clone <repo_url>
```

# Package Build

## Debian/Ubuntu Package

To generate a .deb package file for the instalation of the NITA Robot on a Debian based system you can run the *build-robot-21.7-1.sh* script file found under the *packaging* folder:
```bash
cd packaging
./build-robot-21.7-1.sh
```

## Centos/RedHat Package
To generate a .rpm package file for the instalation of the NITA Robot on a Centos based system you can run the *build-robot-21.7-1.sh* script file found under the *packaging_redhat* folder:
```bash
cd packaging_redhat
./build-robot-21.7-1.sh
```

# Docker Image Build
To build the Robot docker image you can simply run the *build_container.sh* also found on the root folder of this repo:
```bash
./build_container.sh
```
