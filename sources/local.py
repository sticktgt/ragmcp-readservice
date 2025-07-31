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
                    relative_path = file_path.relative_to(self.root)
                    metadata = {
                        "original_name": file_path.name.lower(),
                        "source": str(relative_path.parent).lower(),  # <-- directory part only
                        "size_bytes": os.path.getsize(file_path),
                        "created_at": datetime.fromtimestamp(os.path.getctime(file_path)).isoformat(),
                        "source_connector": "local",
                    }
                    yield str(file_path), None, metadata, None
                except Exception as e:
                    error_message = f"error processing LocalFileSource {self.root}: {e}"
                    logger.error(e)
                    logger.debug(traceback.format_exc())                    
                    yield file_path.name, None, {}, error_message                    
