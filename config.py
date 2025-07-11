CONFIG = {
    "use_local": True,
    "use_s3": True,

    "file_types": {
        ".txt": "TextLoader",
        ".csv": "CSVLoader",
        ".pdf": "PDFPlumberLoader",
        ".docx": "UnstructuredWordDocumentLoader",
        ".doc": "UnstructuredWordDocumentLoader",
        ".html": "UnstructuredHTMLLoader",
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
        "endpoint": "http://localhost:5000/v1",
        "model": "local-embedding-model",
        "api_key": "dummy-key"
    },
    "s3_bucket": "files",
    "s3_prefix": "",
    "endpoint_url": "http://localhost:9001",
    "aws_access_key_id": "minioadmin",
    "aws_secret_access_key": "minioadmin",
    # "aws_access_key_id": os.getenv("S3_ACCESS_KEY", "minioadmin"),
    # "aws_secret_access_key": os.getenv("S3_SECRET_KEY", "minioadmin"),
    "use_ssl": False,
    "local_path": "/home/stickt/python/local_docs",
    "output_dir": "./output_docs",
    "debug_counters": True
}
