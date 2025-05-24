# Normalize Journal Titles

Normalize Journal Titles (NJT) is a command line tool to normalize journal titles obtained from user-entered data for interlibrary loan reports.

## Development Environment
This section provides guidance on setting up a NJT development environment on a local workstation.

### Prerequisites
The following instructions assume that "uv" is installed to enable the setup of an isolated Python environment.

See the following for setup instructions:
* https://docs.astral.sh/uv/getting-started/installation/

## Setup

Clone NJT from GitHub

```bash
git clone git@github.com:timkanke/normalize-journal-titles
cd normalize-journal-titles
uv venv
source .venv/bin/activate
```