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
    "splitter": {
        "chunk_size": 500,
        "chunk_overlap": 50,
        "separators": ["\n\n", "\n", " ", ""]
    },
    "s3_bucket": "files",
    "s3_prefix": "",
    "endpoint_url": "http://localhost:9000",
    "aws_access_key_id": "minioadmin",
    "aws_secret_access_key": "minioadmin",
    # "aws_access_key_id": os.getenv("S3_ACCESS_KEY", "minioadmin"),
    # "aws_secret_access_key": os.getenv("S3_SECRET_KEY", "minioadmin"),
    "use_ssl": False,
    "local_path": "/home/stickt/python/local_docs",
    "output_dir": "./output_docs"
}
