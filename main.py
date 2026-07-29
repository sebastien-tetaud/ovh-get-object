"""Download objects from an OVH Object Storage (S3-compatible) bucket."""

import argparse
import json
import sys
from pathlib import Path

import boto3
from botocore.exceptions import ClientError

# OVH S3 endpoint. Region eu-west-par (Paris, 3-AZ).
# For other regions swap the region code, e.g. s3.gra.io.cloud.ovh.net
REGION = "eu-west-par"
ENDPOINT_URL = f"https://s3.{REGION}.io.cloud.ovh.net"

# Bucket this script targets by default (override with --bucket).
BUCKET = "cdse-catalogue"

# Default credentials file (JSON with accessKey / secretKey), next to this script.
DEFAULT_CREDENTIALS = Path(__file__).parent / "user-tNf8QE3dgAHK.txt"


def load_credentials(path: Path) -> tuple[str, str]:
    """Read the OVH JSON credentials file and return (access_key, secret_key)."""
    data = json.loads(path.read_text())
    return data["accessKey"], data["secretKey"]


def make_client(access_key: str, secret_key: str):
    """Create a boto3 S3 client pointed at the OVH endpoint."""
    return boto3.client(
        "s3",
        endpoint_url=ENDPOINT_URL,
        aws_access_key_id=access_key,
        aws_secret_access_key=secret_key,
        region_name=REGION,
    )


def iter_keys(client, bucket: str):
    """Yield (key, size, last_modified) for every object in the bucket."""
    paginator = client.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            yield obj["Key"], obj["Size"], obj["LastModified"]


def download_object(client, bucket: str, key: str, out_dir: Path) -> Path:
    """Download a single object into out_dir, preserving any key prefixes."""
    target = out_dir / key
    target.parent.mkdir(parents=True, exist_ok=True)
    client.download_file(bucket, key, str(target))
    return target


def download_all(client, bucket: str, out_dir: Path) -> None:
    """Download every object in the bucket into out_dir."""
    count = 0
    for key, _, _ in iter_keys(client, bucket):
        target = download_object(client, bucket, key, out_dir)
        count += 1
        print(f"  downloaded {key} -> {target}")
    print(f"  (empty)" if count == 0 else f"  -> {count} object(s) downloaded")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "key", nargs="?",
        help="Object key to download (omit to download the whole bucket).",
    )
    parser.add_argument(
        "-b", "--bucket", default=BUCKET,
        help=f"Bucket to download from (default: {BUCKET}).",
    )
    parser.add_argument(
        "-c", "--credentials", type=Path, default=DEFAULT_CREDENTIALS,
        help=f"OVH JSON credentials file (default: {DEFAULT_CREDENTIALS.name}).",
    )
    parser.add_argument(
        "-o", "--output", type=Path, default=Path("downloads"),
        help="Destination directory (default: downloads/).",
    )
    return parser


def main() -> None:
    args = build_parser().parse_args()

    try:
        access_key, secret_key = load_credentials(args.credentials)
    except (OSError, json.JSONDecodeError, KeyError) as exc:
        sys.exit(f"Failed to read credentials from {args.credentials}: {exc}")

    client = make_client(access_key, secret_key)

    try:
        if args.key:
            target = download_object(client, args.bucket, args.key, args.output)
            print(f"Downloaded {args.key} -> {target}")
        else:
            print(f"Bucket: {args.bucket} -> {args.output}/")
            download_all(client, args.bucket, args.output)
    except ClientError as exc:
        err = exc.response["Error"]
        sys.exit(f"S3 request failed ({err.get('Code', 'Error')}): "
                 f"{err.get('Message', exc)}")


if __name__ == "__main__":
    main()
