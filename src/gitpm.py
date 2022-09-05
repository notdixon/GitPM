#!/usr/bin/env python3
"""
  ____ _ _   ____  __  __ 
 / ___(_) |_|  _ \|  \/  |        The Git Package Manager
| |  _| | __| |_) | |\/| |             version 0.1
| |_| | | |_|  __/| |  | |
 \____|_|\__|_|   |_|  |_|  https://github.com/notdixon/GitPM

Copyright (C) 2022    notdixon

This program is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 2 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License along
with this program; if not, write to the Free Software Foundation, Inc.,
51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
"""

import os, io, sys, re
from datetime import date, datetime
from colorama import Fore, Style
import configparser as confparse

version = "0.1"

# Where is the GitPM Config File
gitpm_config = "/etc/gitpm.conf"

# Where is the "@installed" file
gitpm_installed_list = "/usr/share/gitpm/installed"

# GitPM Options
gitpm_srcdir = ""
gitpm_maxjobs = 1

# Git Options
git_clonedepth = 1
git_url = ""

# Colors - From 'colorama'
Red = f"{Fore.RED}{Style.BRIGHT}"
Green = f"{Fore.GREEN}{Style.BRIGHT}"
Yellow = f"{Fore.YELLOW}{Style.BRIGHT}"
Blue = f"{Fore.BLUE}{Style.BRIGHT}"
Cyan = f"{Fore.CYAN}{Style.BRIGHT}"
Magenta = f"{Fore.MAGENTA}{Style.BRIGHT}"
Reset = Style.RESET_ALL

def read_gitpm_config():
    """ Read the GitPM Config File """
    global gitpm_srcdir
    global gitpm_maxjobs

    global git_clonedepth

    # Read the config file with configparser
    config = confparse.ConfigParser()
    config.read(gitpm_config)
    config.sections()

    # GitPM Options
    gitpm_srcdir = config['general']['package_src_dir']
    gitpm_maxjobs = config['general']['maxjobs']

    git_clonedepth = config['git']['depth']

def gitpm_help():
    """ Show the available commands """
    print(f"\
{Yellow}GitPM v{version} - Available Commands{Reset}\n\n\
\
 [ --github / -gh ]     : Specify GitHub Repository\n\
 [ --gitlab / -gl ]     : Specify GitLab Repository\n\
 \n\
 [ --install   / -i ]   : Install the Package\n\
 [ --remove    / -r ]   : Uninstall The Package and Source Code\n\
 [ --build     / -b ]   : Only build the package, don't install\n\
 [ --installed / -I ]   : List installed packages\n\
\n\
 [ --help      / -h ]   : Show this Help\n\
\n\
 Example: {Magenta}gitpm --github notdixon/gitpm --install{Reset}\n\
          {Magenta}gitpm --remove notdixon/gitpm{Reset}")

def build_package(package_name):
    """ Build the package """
    print(f">>> Building {Blue}{package_name}{Reset}")
    package_dir = f"{gitpm_srcdir}/{package_name}"

    if os.path.isfile(f"{package_dir}/autogen.sh"):
        os.system(f"cd {package_dir} && ./autogen.sh")

    if os.path.isfile(f"{package_dir}/configure"):
        os.system(f"cd {package_dir} && ./configure")

    if os.path.isfile(f"{package_dir}/CMakeLists.txt"):
        os.system(f"mkdir -p {package_dir}/build && cd {package_dir}/build && cmake ..")
        if os.path.isfile(f"{package_dir}/build/Makefile"):
            os.system(f"cd {package_dir}/build && make -j{gitpm_maxjobs}")

    if os.path.isfile(f"{package_dir}/Makefile"):
        os.system(f"cd {package_dir} && make -j{gitpm_maxjobs}")

def record_package(package_name):
    """ Record the newly installed package in @installed """
    now = datetime.now()
    current_time = now.strftime("%d/%m/%y %-I:%M:%S%p")

    install_file = open(gitpm_installed_list, "a")
    install_file.write(package_name)
    install_file.write("\n")
    install_file.close()

    os.system(f"touch /tmp/gitpm_temp_file && touch {gitpm_installed_list}")
    install_file = open(gitpm_installed_list, "r")
    temp_file = open("/tmp/gitpm_temp_file", "r+")
    for line in install_file:
        if not line.isspace():
            temp_file.write(line)

    temp_file.close()
    os.system(f"cp /tmp/gitpm_temp_file {gitpm_installed_list} && rm /tmp/gitpm_temp_file")
    print(f">>> Successfully installed {Blue}{package_name}{Reset} {Magenta}{current_time}{Reset}")

def remove_from_installed(package_name):
    """ Remove a package from @installed """
    print(f">>> Removing {Green}{package_name}{Reset} from {Blue}@installed{Reset}")

    if os.path.isfile("/tmp/cleaned"):
        os.system("rm /tmp/cleaned")

    delete = f"{package_name}\n"
    with open(gitpm_installed_list) as fin, open("/tmp/cleaned", "a") as fout:
        for line in fin:
            for word in delete:
                line = line.replace(package_name, "")
            if not line.isspace():
                fout.write(line)

    os.system(f"mv /tmp/cleaned {gitpm_installed_list}")

def show_packages():
    print(f"{Magenta}Installed Packages{Reset}\n")
    os.system(f"/bin/cat {gitpm_installed_list}")
    
def remove_package(package_name):
    """ Remove an installed package """
    package_dir = f"{gitpm_srcdir}/{package_name}"

    if os.path.isfile(f"{package_dir}/build/Makefile"):
        os.system(f"cd {package_dir}/build && make uninstall")

    if os.path.isfile(f"{package_dir}/Makefile"):
        os.system(f"cd {package_dir} && make uninstall")

    package_regex = re.sub("/.*", "", package_name)
    os.system(f"rm -rf {gitpm_srcdir}/{package_name}")

    if len(os.listdir(f"{gitpm_srcdir}/{package_regex}")) == 0:
        os.system(f"rm -rf {gitpm_srcdir}/{package_regex}")

    remove_from_installed(package_name)

def download_sources(package_url, package_name):
    """ Download the Sources """
    package_dir = f"{gitpm_srcdir}/{package_name}"
    print(f">>> Downloading {Blue}{package_url}{Reset}")

    if not os.path.isdir(f"{package_dir}"):
        os.system(f"git clone --depth={git_clonedepth} {package_url} {package_dir}")
        
def install_package(package_url, package_name):
    """ Install a package """
    package_dir = f"{gitpm_srcdir}/{package_name}"
    download_sources(package_url, package_name)
    build_package(package_name)
    print(f">>> Installing {Blue}{package_name}{Reset}")

    if os.path.isfile(f"{package_dir}/build/Makefile"):
        os.system(f"cd {package_dir}/build && make install")

    if os.path.isfile(f"{package_dir}/Makefile") or os.path.isfile(f"{package_dir}/makefile"):
        os.system(f"cd {package_dir} && make install")

    print(f">>> Recording {Blue}{package_name}{Reset} in {Magenta}@installed{Reset}")
    record_package(package_name)
        
if __name__ == '__main__':
    if len(sys.argv) == 1:
        gitpm_help()
        exit(0)
    else:
        read_gitpm_config()
        for i, arg in enumerate(sys.argv):
            if arg == "--github" or arg == "-gh":
                try:
                    git_url = f"https://github.com/{sys.argv[i + 1]}.git"
                    package_name = sys.argv[i + 1]
                except IndexError:
                    print(f">>> {Red}Error{Reset}: No package was specified")
                    
            if arg == "--gitlab" or arg == "-gl":
                try:
                    git_url = f"https://gitlab.com/{sys.argv[i + 1]}.git"
                    package_name = sys.argv[i + 1]
                except IndexError:
                    print(f">>> {Red}Error{Reset}: No package was specified")

            if arg == "--remove" or arg == "-r":
                try:
                    package_name = sys.argv[i + 1]
                    remove_package(package_name)
                except IndexError:
                    print(f">>> {Red}Error{Reset}: No package to remove")

            if arg == "--install" or arg == "-i":
                if len(package_name) == 0:
                    print(f">>> {Red}Error{Reset}: No package to install")
                    exit(-1)
                install_package(git_url, package_name)

            if arg == "--build" or arg == "-b":
                if len(package_name) == 0:
                    print(f">>> {Red}Error{Reset}: No package to install")
                    exit(-1)
                download_sources(git_url, package_name)
                build_package(package_name)
                
            if arg == "--help" or arg == "-h":
                gitpm_help()

            if arg == "--installed" or arg == "-I":
                show_packages()
