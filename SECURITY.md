# Security policy

Phone Bridge controls a phone from a PC and a PC from a phone, so security reports are taken seriously. A readable description of what the app exposes is in **[docs/en/security.md](docs/en/security.md)** (فارسی: [docs/fa/security.md](docs/fa/security.md)).

## Supported versions

Only the **latest release** (and `main`) receives fixes.

## Reporting a vulnerability

**Please don't open a public issue.** Use one of these, in order of preference:

1. GitHub → *Security* tab → **Report a vulnerability** (private advisory), or
2. contact the maintainer privately through the contact on the repository owner's GitHub profile.

Include: version (`--version`), OS, steps to reproduce, impact, and whether you'd like credit. You'll get an acknowledgement as soon as a maintainer sees it (this is a volunteer project — typically within a few days) and we'll work with you on a fix and a coordinated disclosure.

## In scope

- The remote HTTP server (`PhoneKeyboardServer`): authentication bypass, token leakage, path traversal, injection into the PC, anything that works **without** the token or with the opt-in features still off.
- Command injection through values the app passes to `adb shell` (URLs, numbers, package names, paths).
- Unsafe file handling (downloads, zip extraction, temp files).
- Data exposure beyond what's documented.

## Known limitations (documented, not vulnerabilities)

Plain HTTP on the LAN, no rate limiting, token in the URL, listening on all interfaces — see the *Known limitations* list in [docs/en/security.md](docs/en/security.md#the-remote-server-phone--pc). Improvements are welcome as pull requests.

## Out of scope

Issues that require malware already running on your PC or phone, a malicious `adb` binary you chose to run, or physical access to an unlocked device.
