CONFIG = {
    "use_local": True,
    "use_s3": True,

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
        "provider": "fake",  # yandex or "fake"
        "dim": 256,  # dimension of the embeddings
    },
    "yandex": {
        "api_key": "###", # os.getenv("YANDEX_API_KEY", "")
        "folder_id": "b1g2758uu6otr3b7s64e", # os.getenv("YANDEX_FOLDER_ID", "")
        "doc_model_name": "text-search-doc",
        "model_version": "latest",  # or specify a version like "2023-10-01"
        "sleep_interval": 2.0,
        "disable_request_logging": False,
    },
    "milvus": {
        "host": "localhost",
        "port": 19530,
        "collection": "doc_vectors",
        "drop_old": False,
        "auto_id": True,
        "alias": "default",
        "search_query": "надо будет делать в двух вариантах",
        "search_top_k": 5,
    },
    "s3": {
        "s3_bucket": "files",
        "s3_prefix": "",
        "endpoint_url": "http://localhost:9000",
        "aws_access_key_id": "minioadmin",  # os.getenv("S3_ACCESS_KEY", "minioadmin"),
        "aws_secret_access_key": "minioadmin",  # os.getenv("S3_SECRET_KEY", "minioadmin"),
        "use_ssl": False,
        "signature_version": "s3v4",
    },
    "local_path": "/home/stickt/python/local_docs",
    "output_dir": "./output_docs",
    "debug": True,
    "delete_old_vectors": False,  # whether to delete old vectors by hashcode
}
