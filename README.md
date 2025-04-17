# mypkgs - List Manually Installed Debian Packages

`mypkgs` is a command-line utility that helps you identify Debian packages that were explicitly installed by the user. It aims for accuracy by analyzing various system files and logs without requiring root privileges (`sudo`).

## How it Works

`mypkgs` employs a multi-pronged approach to determine manually installed packages:

1.  **Parsing `/var/lib/dpkg/extended_states`:** This file provides the most reliable information about whether a package was automatically installed as a dependency or manually by the user.
2.  **Analyzing APT History Logs (`/var/log/apt/history.log*`):** It examines the APT history logs (including rotated versions) for explicit installation commands. This adds completeness but might be less reliable due to log rotation.
3.  **Filtering Automatically Installed Packages:** It reads `/var/lib/dpkg/status` to identify packages marked as automatically installed and removes them from the initially gathered list.

By combining these sources and filtering out automatically installed dependencies, `mypkgs` provides a more accurate list of packages you intentionally installed.

## Installation

If you have a `.deb` package for `mypkgs` (e.g., `mypkgs_0.1.0_all.deb`), you can install it using:

```bash
sudo apt install ./mypkgs_0.1.0_all.deb