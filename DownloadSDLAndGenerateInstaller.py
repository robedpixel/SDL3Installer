# STEPS
# Download latest windows x64 zip file from sdl repo (use regex?) to temp folder
# Record downloaded version number
# unzip contents to install
# Modify wxs version to downloaded version
# Run wix

import requests
import zipfile
import io
import re
import json
import os
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path


def main():
    github_sdl_repo_path = "/libsdl-org/SDL"
    # Regex to find version number, currently not needed
    # version_regex = "([0-9]+[.]){2}[0-9]"

    windows_regex = "win32-x64"
    file_blacklist = ["INSTALL.md", ".git-hash"]
    install_dir = "install"
    files_to_install = []
    libs_to_install = []

    # Download latest windows x64 zip file from sdl repo

    github_sdl_repo_abs_path = (
        "https://api.github.com/repos" + github_sdl_repo_path + "/releases/latest"
    )
    print("Getting latest SDL3 info")
    response_json = requests.get(url=github_sdl_repo_abs_path).json()

    # Grab version

    library_version = response_json["name"]
    print("Latest version: " + library_version)
    # Iterate through assets and find x86_64 zip

    asset_list = response_json["assets"]
    for asset in asset_list:
        if re.search(windows_regex, asset["name"]):
            dirname = os.path.dirname(__file__)
            temp_folder = os.path.join(dirname, "temp")
            install_folder = os.path.join(dirname, install_dir)

            Path(temp_folder).mkdir(parents=True, exist_ok=True)
            # Download contents into temp

            download_url = asset["browser_download_url"]
            print("Downloading SDL3...")
            r = requests.get(download_url)
            z = zipfile.ZipFile(io.BytesIO(r.content))
            Path(temp_folder).mkdir(parents=True, exist_ok=True)
            print("Extracting to temp folder...")
            z.extractall(temp_folder)
            # remove all files in install folder
            print("Removing old install files...")
            for root, dirs, files in os.walk(install_folder):
                for f in files:
                    os.unlink(os.path.join(root, f))
                for d in dirs:
                    shutil.rmtree(os.path.join(root, d))
            # move contents to install unless it's in blacklist
            print("Adding new install files...")
            Path(install_folder).mkdir(parents=True, exist_ok=True)
            temp_directory = os.fsencode(temp_folder)
            lib_folder_created = false
            for file in os.listdir(temp_directory):
                filename = os.fsdecode(file)
                if filename in file_blacklist:
                    continue
                else:
                    if Path(filename).suffix == ".dll":
                        if not lib_folder_created:
                            Path(install_folder+"/lib").mkdir(parents=True, exist_ok=True)
                            lib_folder_created = true
                        print("Adding: " + "lib/"+install_filename)
                        libs_to_install.append(filename)
                        os.replace(
                            temp_folder + "\\" + filename, install_folder + "\\lib\\" + install_filename
                        )
                    else:
                        print("Adding: " + install_filename)
                        files_to_install.append(install_filename)
                        os.replace(
                            temp_folder + "\\" + filename, install_folder + "\\" + install_filename
                        )
            # edit wxs file with new version and files
            print("Updating Package.wxs...")
            wxs_file = os.path.join(dirname, "Package.wxs")
            ET.register_namespace("", "http://wixtoolset.org/schemas/v4/wxs")
            ET.register_namespace("ui", "http://wixtoolset.org/schemas/v4/wxs/ui")
            tree = ET.parse(wxs_file)
            root = tree.getroot()
            for elem in root.iter():
                if elem.tag == "{http://wixtoolset.org/schemas/v4/wxs}Package":
                    elem.attrib["Version"] = library_version
                    for sub_elem_1 in elem.iter():
                        if sub_elem_1.tag == "{http://wixtoolset.org/schemas/v4/wxs}ComponentGroup":
                            for sub_elem_2 in sub_elem_1.iter():
                                if sub_elem_2.tag == "{http://wixtoolset.org/schemas/v4/wxs}Component" and sub_elem_2.attrib.get("Id")=="MainInstall":
                                    # Remove all old file entries
                                    elements_to_remove = []
                                    for sub_elem_3 in sub_elem_2.iter():
                                        if sub_elem_3.tag == "{http://wixtoolset.org/schemas/v4/wxs}File":
                                             elements_to_remove.append(sub_elem_3)
                                    for e in elements_to_remove:
                                        sub_elem_2.remove(e)
                                    for file in files_to_install:
                                        b = ET.SubElement(sub_elem_2, "{http://wixtoolset.org/schemas/v4/wxs}File").set("Source",install_dir+"/"+file)
                                if sub_elem_2.tag == "{http://wixtoolset.org/schemas/v4/wxs}Component" and sub_elem_2.attrib.get("Id")=="LibInstall":
                                    # Remove all old file entries
                                    elements_to_remove = []
                                    for sub_elem_3 in sub_elem_2.iter():
                                        if sub_elem_3.tag == "{http://wixtoolset.org/schemas/v4/wxs}File":
                                             elements_to_remove.append(sub_elem_3)
                                    for e in elements_to_remove:
                                        sub_elem_2.remove(e)
                                    for file in libs_to_install:
                                        b = ET.SubElement(sub_elem_2, "{http://wixtoolset.org/schemas/v4/wxs}File").set("Source",install_dir+"/lib/"+file)
            ET.indent(tree, '  ') 
            tree.write(wxs_file)
            print("Removing temp folder...")
            try:
                shutil.rmtree(temp_folder)
            except OSError as e:
                print("Error: %s - %s." % (e.filename, e.strerror))
            # Build Installer
            print("Building Installer...")
            os.chdir(dirname)
            os.system("dotnet build SDL3Installer.wixproj -c Release -r win-x64")
            print(library_version)
            break


if __name__ == "__main__":
    main()
