# Security Policy

## Reporting a vulnerability

DataSinking takes security seriously. If you discover a vulnerability — whether in the
Python client, the MCP server, or the `api.datasink.ing` endpoint — please report it
privately so it can be fixed before public disclosure.

**Do not open a public issue.** Instead email:

- **security@datasink.ing**

We will respond within 7 days with an acknowledgment, and aim to confirm the issue and
provide a timeline within 14 days.

### What to include

- A clear description of the issue and its impact.
- Steps to reproduce (as concrete as possible).
- Any affected endpoint, version, or configuration.

## Scope

- The `datasinking` Python client and `datasinking[mcp]` MCP server (this repository).
- The DataSinking API at `https://api.datasink.ing`.

## Supported versions

Only the latest published version on [PyPI](https://pypi.org/project/datasinking/) is
supported for security fixes.

## Disclosure

We follow a coordinated-disclosure process: once a fix is released we will credit the
reporter (unless you prefer to stay anonymous) and publish a short advisory.
