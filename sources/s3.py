import boto3
from pathlib import Path
from datetime import datetime
from typing import Iterator, Tuple, Optional
from botocore.config import Config as BotoConfig
from readservice.utils.logger import get_logger
import traceback

logger = get_logger()

class S3FileSource:
    def __init__(self, config: dict, file_types: dict):
        self.bucket = config["s3"]["s3_bucket"]
        self.prefix = config["s3"]["s3_prefix"]
        self.file_types = file_types
        self.endpoint_url = config["s3"]["endpoint_url"]
        session = boto3.Session()
        self.s3 = session.client(
            "s3",
            endpoint_url=self.endpoint_url,
            aws_access_key_id=config["s3"]["aws_access_key_id"],
            aws_secret_access_key=config["s3"]["aws_secret_access_key"],
            use_ssl=config["s3"]["use_ssl"],
            config=BotoConfig(signature_version=config["s3"]["signature_version"]),
        )

    def iterate_files(self) -> Iterator[Tuple[str, Optional[bytes], dict, Optional[str]]]:
        try:
            paginator = self.s3.get_paginator("list_objects_v2")
            for page in paginator.paginate(Bucket=self.bucket, Prefix=self.prefix):
                for obj in page.get("Contents", []):
                    key = obj["Key"]
                    ext = Path(key).suffix.lower()
                    if ext not in self.file_types:
                        continue
                    try:
                        response = self.s3.get_object(Bucket=self.bucket, Key=key)
                        data = response["Body"].read()
                        metadata = {
                            "original_name": Path(key).name,
                            "source": key,
                            "size_bytes": obj.get("Size"),
                            # size": len(data),
                            "created_at": obj.get("LastModified").isoformat() if obj.get("LastModified") else None,
                            "source_connector": f"s3:{self.endpoint_url}/"+self.bucket,
                        }
                        yield key, data, metadata, None
                    except Exception as e:
                        traceback_str = traceback.format_exc()
                        logger.debug(traceback_str)                    
                        yield key, None, {}, str(e)
        except Exception as outer_error:
            traceback_str = traceback.format_exc()
            logger.debug(traceback_str)                  
            yield "s3_connection", None, {}, str(outer_error)                        