CONFIG = {
    "file_types": {
        ".txt": {
            "loader": "TextLoader",
            "splitter": {
                "type": "RecursiveCharacterTextSplitter",
                # "type": "none",
                "chunk_size": 1000,
                "chunk_overlap": 50,
                "separators": ["\n\n", "\n", " ", ""]
            }
        },
        ".csv": {
            "loader": "CSVLoader",
            "splitter": {
                "type": "none"
            }
        },
        ".pdf": {
            "loader": "PDFPlumberLoader",
            "splitter": {
                "type": "TokenTextSplitter",
                "chunk_size": 500,
                "chunk_overlap": 50,
                "encoding_name": "cl100k_base"
            }
        },
        ".docx": {
            "loader": "UnstructuredWordDocumentLoader",
            "splitter": {
                "type": "NLTKTextSplitter",
                "chunk_size": 800,
                "chunk_overlap": 100,
                "language": "russian"
            }
        },
        ".xlsx": {
            "loader": "UnstructuredExcelLoader",
            "splitter": {
                "type": "none"
            }
        },
        ".html": {
            "loader": "UnstructuredHTMLLoader",
            "splitter": {
                "type": "TokenTextSplitter",
                "chunk_size": 500,
                "chunk_overlap": 50,
                "encoding_name": "cl100k_base"
            }
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
    "sources": {
        "use_local": True,
        "use_s3": False,        
        "local_path": "/home/stickt/python/local_docs",
        "s3": {
            "s3_bucket": "files",
            "s3_prefix": "",
            "endpoint_url": "http://localhost:9000",
            "aws_access_key_id": "minioadmin",  # os.getenv("S3_ACCESS_KEY", "minioadmin"),
            "aws_secret_access_key": "minioadmin",  # os.getenv("S3_SECRET_KEY", "minioadmin"),
            "use_ssl": False,
            "signature_version": "s3v4",
        },    
    },
    "storage": {
        "store_type": "pgvector",  # "milvus" or "pgvector"
        "milvus": {
            "host": "localhost",
            "port": 19530,
            "collection": "doc_vectors",
            "drop_old": False,
            "auto_id": True,
            "alias": "default",
        },
        "pgvector": {
            "host": "localhost",
            "port": 5432,
            "user": "postgres",
            "password": "postgres",
            "database": "vector_db",
            "collection": "doc_vectors",
            "use_jsonb": True,  # use JSONB for metadata
        }
    },
    "search": {
        "search_query": "the work of a data analyst",
        "search_top_k": 5,
    },
    "output_dir": "./output_docs",
    "debug": True,
    "delete_old_vectors": True,  # whether to delete old vectors by hashcode
}
