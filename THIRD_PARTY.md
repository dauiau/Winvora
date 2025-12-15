# Third-Party Dependencies

This document lists third-party software that Winvora depends on or integrates with.

## Wine (Wine Is Not an Emulator)

**License**: GNU Lesser General Public License (LGPL) v2.1 or later

**Description**: Wine is a compatibility layer capable of running Windows applications on several POSIX-compliant operating systems, such as Linux, macOS, and BSD.

**Usage in Winvora**: Winvora treats Wine as an **external dependency**. Wine is not embedded, bundled, or distributed with Winvora. Users must install Wine separately on their systems. Winvora provides a management layer and user interface to interact with Wine through its command-line interface and environment.

**Links**:
- Website: https://www.winehq.org/
- Source Code: https://gitlab.winehq.org/wine/wine
- License: https://gitlab.winehq.org/wine/wine/-/blob/master/COPYING.LIB

**LGPL Compliance**: Since Wine is used as an external dependency and not linked or embedded into Winvora, and Winvora is licensed under MIT, there are no licensing conflicts. Users install and maintain their own Wine installations independently.

---

## Important Note

Winvora itself is licensed under the MIT License. All code in this repository is original work and does not contain any GPL-licensed code or code copied from GPL projects such as Whisky or similar applications.

If you add additional third-party dependencies to this project, please document them in this file with:
1. Name of the dependency
2. License type
3. Brief description
4. How it's used in the project
5. Links to project homepage and license
