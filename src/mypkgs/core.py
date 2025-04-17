#!/usr/bin/env python3

import os
import re
import glob
import gzip


def get_manual_installed_packages():
    """
    Retrieves a list of manually installed Debian packages by parsing various
    files and logs, prioritizing accuracy without requiring sudo.

    This function combines information from dpkg extended states, apt history logs,
    and dpkg status to identify packages that were explicitly installed by the
    user.  It aims to be as accurate as possible without root privileges.

    Returns:
        set: A set of manually installed package names.  Returns an empty set
             if no packages are found or if there are errors accessing the files.
    """
    manual_packages = set()

    # 1. Get manually installed packages from /var/lib/dpkg/extended_states (most reliable)
    manual_packages_extended_states = _get_manual_installed_packages_from_extended_states()
    manual_packages.update(manual_packages_extended_states)

    # 2. Add packages from apt history logs (for completeness, less reliable)
    manual_packages_logs = _get_manual_installed_packages_from_logs()
    manual_packages.update(manual_packages_logs)

    # 3. Remove automatically installed packages (from dpkg status)
    auto_installed_packages = _get_auto_installed_packages()
    manual_packages.difference_update(auto_installed_packages)

    return manual_packages



def _get_manual_installed_packages_from_extended_states():
    """
    Retrieves manually installed packages from /var/lib/dpkg/extended_states.

    This file provides the most reliable information about whether a package was
    automatically or manually installed.  It does not require root privileges to read.

    Returns:
        set: A set of manually installed package names.
    """
    manual_packages = set()
    extended_states_file = "/var/lib/dpkg/extended_states"

    if not os.path.exists(extended_states_file):
        return set()  # File might not always exist

    try:
        with open(extended_states_file, "r", encoding="utf-8") as f:
            package_name = None
            auto_installed = False
            for line in f:
                if line.startswith("Package: "):
                    package_name = line[9:].strip()
                    auto_installed = False  # Reset for each package
                elif line.startswith("Auto-Installed: "):
                    auto_installed = line[16:].strip() == "yes"
                elif package_name and not auto_installed:
                    manual_packages.add(package_name)
    except (IOError, OSError) as e:
        print(f"Error reading {extended_states_file}: {e}")
        return set()

    return manual_packages



def _get_manual_installed_packages_from_logs():
    """
    Retrieves manually installed packages from APT history logs.

    This method parses /var/log/apt/history.log and its rotated versions to find
    package installation entries.  It's less reliable than extended_states because
    logs can be incomplete or rotated out.  It does not require root privileges to read.

    Returns:
        set: A set of manually installed package names.
    """
    manual_packages = set()
    log_files = glob.glob("/var/log/apt/history.log*")  # Include rotated logs
    install_pattern = re.compile(
        r"install\s+(?P<packages>([a-z0-9._+-]+(?:=[0-9.:~-]+)?)(,\s*[a-z0-9._+-]+(?:=[0-9.:~-]+)?)*)"
    )  # Matches "install" and captures package names (with versions)
    package_name_pattern = re.compile(r"([a-z0-9._+-]+)(?:=[0-9.:~-]+)?")  # Extracts package name from entry

    for log_file in log_files:
        if log_file.endswith(".gz"):  # Handle compressed logs
            try:
                with gzip.open(log_file, "rt", encoding="utf-8") as f:
                    for line in f:
                        if " install " in line:  # Find installation entries
                            match = install_pattern.search(line)
                            if match:
                                packages_str = match.group("packages")  # Get package list string
                                package_list = packages_str.split(", ")  # Split into individual packages
                                for package_entry in package_list:
                                    package_name_match = package_name_pattern.match(
                                        package_entry
                                    )
                                    if (
                                        package_name_match
                                        and package_name_match.group(1) != "."
                                    ):  # Extract and validate package name
                                        manual_packages.add(
                                            package_name_match.group(1)
                                        )  # Add to set
            except (IOError, OSError, gzip.BadGzipFile):
                pass  # Non-critical error, continue
        else:  # Handle uncompressed logs
            try:
                with open(log_file, "r", encoding="utf-8") as f:
                    for line in f:
                        if " install " in line:
                            match = install_pattern.search(line)
                            if match:
                                packages_str = match.group("packages")
                                package_list = packages_str.split(", ")
                                for package_entry in package_list:
                                    package_name_match = package_name_pattern.match(
                                        package_entry
                                    )
                                    if (
                                        package_name_match
                                        and package_name_match.group(1) != "."
                                    ):
                                        manual_packages.add(
                                            package_name_match.group(1)
                                        )
            except (IOError, OSError):
                pass  # Non-critical error, continue
    return manual_packages



def _get_auto_installed_packages():
    """
    Retrieves a set of automatically installed packages by parsing the dpkg status file.

    This function reads /var/lib/dpkg/status to identify packages that are currently
    marked as automatically installed.  This is used to exclude dependencies from
    the list of manually installed packages.  It does not require root privileges to read.

    Returns:
        set: A set of automatically installed package names.
    """
    auto_packages = set()
    status_file = "/var/lib/dpkg/status"

    if not os.path.exists(status_file):
        return set()  # File should always exist, but handle the case

    try:
        with open(status_file, "r", encoding="utf-8") as f:
            package_name = None
            for line in f:
                if line.startswith("Package: "):
                    package_name = line[9:].strip()
                elif line.startswith("Status: ") and "auto" in line:
                    if package_name:
                        auto_packages.add(package_name)
    except (IOError, OSError) as e:
        print(f"Error reading {status_file}: {e}")
        return set()

    return auto_packages



def main():
    """
    Main function to print the list of manually installed packages.

    This function calls get_manual_installed_packages() to retrieve the list and
    then prints the packages in sorted order for easy reading.
    """
    manual_packages = get_manual_installed_packages()

    if manual_packages:
        for package in sorted(manual_packages):
            print(package)
    else:
        print("No manually installed packages found.")


if __name__ == "__main__":
    main()
