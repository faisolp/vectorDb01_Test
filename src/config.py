"""
Configuration Module for Vector Database Application
"""
import os

# File paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "document")
PDF_PATH = os.path.join(DATA_DIR, "Vector Database.pdf")

# Database configuration
COLLECTION_NAME = "pdf_collection_thai_labse"
MILVUS_HOST = "localhost"
MILVUS_PORT = "19530"

# Embedding model configuration
MODEL_NAME = "sentence-transformers/LaBSE"

# Document processing configuration
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# Search configuration
SEARCH_LIMIT = 5