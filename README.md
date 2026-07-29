# ovh-bucket

A small [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html)
script for listing and downloading objects from an
[OVH Object Storage](https://www.ovhcloud.com/en/public-cloud/object-storage/)
bucket (S3-compatible).

By default it targets the **`cdse-catalogue`** bucket in OVH's **`eu-west-par`**
(Paris, 3-AZ) region — both configurable, see [Configuration](#configuration).

## Requirements

- Python **>= 3.13**
- [uv](https://docs.astral.sh/uv/)

## Setup

```bash
uv sync
```

Creates a `.venv` and installs dependencies from
[`pyproject.toml`](pyproject.toml).


## Usage

```bash
# Download the whole bucket
uv run main.py -o /path/out/dir/ -c /path/credentials.txt
```
