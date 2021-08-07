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

%define        __spec_install_post %{nil}
%define          debug_package %{nil}
%define        __os_install_post %{_dbpath}/brp-compress

Name:           nita-robot-4.1
Version:        21.7
Release:        1
Summary:        Network Implementation and Test Automation
Group:          Development/Tools
BuildArch:      noarch
License:        Apache License, Version 2.0, http://www.apache.org/licenses/LICENSE-2.0
URL:            https://www.juniper.net
Source0:        %{name}-%{version}.tar.gz
Requires:       docker-ce

BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root

%description
Network Implementation and Test Automation docker-compose based cli/web application for doing provisioning and testing of network hardware and software

%pre
if [ $(getenforce) != Permissive ]; then echo "******  Please disable SELinux during instalation (setenforce 0)  ******"; exit 1; fi

%prep
%setup -q

%build
# Empty section.

%install
rm -rf %{buildroot}
mkdir -p  %{buildroot}
# in builddir
cp -a * %{buildroot}

%clean
rm -rf %{buildroot}

%post
%{_sysconfdir}/nita-robot-%{version}/install.sh

%preun
if [ $(getenforce) != Permissive ]; then echo "******  Please disable SELinux during removal (setenforce 0)  ******"; exit 1; fi
%{_sysconfdir}/nita-robot-%{version}/remove.sh

%files
%defattr(-,root,root,-)
%{_sysconfdir}/nita-robot-%{version}/install.sh
%{_sysconfdir}/nita-robot-%{version}/remove.sh
%{_datadir}/%{name}/*
%{_prefix}/local/bin/*

%changelog
* Sat Aug 7 2021 Hugo Ribeiro  21.7-1
  - Updated broken dependencies
* Wed Sep 23 2020 Hugo Ribeiro  20.10-1
  - OS Release
