
# librfap

[![GitHub release (latest SemVer including pre-releases)](https://img.shields.io/github/v/release/alexcoder04/librfap?include_prereleases)](https://github.com/alexcoder04/librfap/releases/latest)
[![GitHub top language](https://img.shields.io/github/languages/top/alexcoder04/librfap)](https://github.com/alexcoder04/librfap/search?l=python)
[![GitHub](https://img.shields.io/github/license/alexcoder04/librfap)](https://github.com/alexcoder04/librfap/blob/main/LICENSE)
[![GitHub issues](https://img.shields.io/github/issues/alexcoder04/librfap)](https://github.com/alexcoder04/librfap/issues)
[![GitHub pull requests](https://img.shields.io/github/issues-pr/alexcoder04/librfap)](https://github.com/alexcoder04/librfap/pulls)
[![GitHub commit activity](https://img.shields.io/github/commit-activity/m/alexcoder04/librfap)](https://github.com/alexcoder04/librfap/commits/main)
[![GitHub contributors](https://img.shields.io/github/contributors-anon/alexcoder04/librfap)](https://github.com/alexcoder04/librfap/graphs/contributors)

Client-side Python library for the rfap protocol.

See [here](#related-projects) for protocol specifications and other compatible
programs.

## Installation

### Stable release with pip

```sh
LOCATION=$(curl -s https://api.github.com/repos/alexcoder04/librfap/releases/latest \
    | grep "tag_name" \
    | awk '{print "https://github.com/alexcoder04/librfap/archive/" substr($2, 2, length($2)-3) ".zip"}')
curl -L -o "${TMPDIR:-/tmp}/librfap.zip" "$LOCATION"
pip3 install "${TMPDIR:-/tmp}/librfap.zip"
```

Or download and install manually from the [releases
page](https://github.com/alexcoder04/librfap/releases/latest).

### Latest version from this repo with pip

```sh
git clone https://github.com/alexcoder04/librfap
pip3 install ./librfap
```

### Arch Linux PKGBUILD

**Coming soon**

## Related projects

 - https://github.com/alexcoder04/rfap - general specification
 - https://github.com/alexcoder04/rfap-pycli - CLI client based on this library
 - https://github.com/alexcoder04/rfap-go-server - server side
 - https://github.com/BoettcherDasOriginal/rfap-cs-lib - C# client library

