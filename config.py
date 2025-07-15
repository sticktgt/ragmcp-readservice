CONFIG = {
    "use_local": True,
    "use_s3": False,

    "file_types": {
        ".txt": "TextLoader",
        ".csv": "CSVLoader",
        ".pdf": "PDFPlumberLoader",
        ".docx": "UnstructuredWordDocumentLoader",
        ".doc": "UnstructuredWordDocumentLoader",
    },
    "splitters": {
        ".txt": {
            "type": "recursive",
            "chunk_size": 500,
            "chunk_overlap": 50,
            "separators": ["\n\n", "\n", " ", ""]
        },
        ".pdf": {
            "type": "token",
            "chunk_size": 500,
            "chunk_overlap": 50,
            "encoding_name": "cl100k_base"
        },
        ".docx": {
            "type": "nltk",
            "chunk_size": 800,
            "chunk_overlap": 100,
            "language": "russian"
        },
        ".doc": {
            "type": "nltk",
            "chunk_size": 800,
            "chunk_overlap": 100,
            "language": "russian"
        },
        ".csv": {
            "type": "none"
        }
    },
    "embedding": {
        "provider": "yandex",  # yandex or "fake"
    },
    "yandex": {
        "api_key": "###", # os.getenv("YANDEX_API_KEY", "")
        "folder_id": "b1g2758uu6otr3b7s64e", # os.getenv("YANDEX_FOLDER_ID", "")
    },
    "milvus": {
        "host": "localhost",
        "port": 19530,
        "collection": "doc_vectors",
        "dim": 768,  # Yandex embedding dimension (mock or real)
        "overwrite": False
    },
    "s3_bucket": "files",
    "s3_prefix": "",
    "endpoint_url": "http://localhost:9001",
    "aws_access_key_id": "minioadmin", # os.getenv("S3_ACCESS_KEY", "minioadmin"),
    "aws_secret_access_key": "minioadmin", # os.getenv("S3_SECRET_KEY", "minioadmin"),
    "use_ssl": False,
    "local_path": "/home/stickt/python/local_docs",
    "output_dir": "./output_docs",
    "debug_counters": True
}
