import os
from pathlib import Path
from datetime import datetime
from typing import Iterator, Tuple, Optional
from readservice.utils.logger import get_logger
import traceback

logger = get_logger()

class LocalFileSource:
    def __init__(self, root: str, file_types: dict):
        self.root = Path(root)
        self.file_types = file_types

    def iterate_files(self) -> Iterator[Tuple[str, Optional[bytes], dict, Optional[str]]]:
        for file_path in self.root.rglob("*"):
            if file_path.suffix.lower() in self.file_types:
                try:
                    metadata = {
                        "original_name": file_path.name,
                        "source": str(file_path),
                        "size_bytes": os.path.getsize(file_path),
                        "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                        "source_connector": "local",
                    }
                    yield str(file_path), None, metadata, None
                except Exception as e:
                    traceback_str = traceback.format_exc()
                    logger.debug(traceback_str)
                    yield file_path.name, None, {}, str(e)                    
