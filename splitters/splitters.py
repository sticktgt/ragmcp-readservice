from typing import Dict
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    TokenTextSplitter,
    NLTKTextSplitter,
    SpacyTextSplitter
)

def getRecursiveCharacterTextSplitter(config: Dict) -> RecursiveCharacterTextSplitter:
    chunk_size = config.get("chunk_size", 1000)
    chunk_overlap = config.get("chunk_overlap", 50)
    extra_args = {k: v for k, v in config.items() if k not in ["type", "chunk_size", "chunk_overlap"]}

    return RecursiveCharacterTextSplitter(chunk_size=chunk_size,
                                           chunk_overlap=chunk_overlap,**extra_args)
        
def getTokenTextSplitter(config: Dict) -> TokenTextSplitter:
    chunk_size = config.get("chunk_size", 1000)
    chunk_overlap = config.get("chunk_overlap", 50)
    extra_args = {k: v for k, v in config.items() if k not in ["type", "chunk_size", "chunk_overlap"]}

    return TokenTextSplitter(chunk_size=chunk_size,
                                           chunk_overlap=chunk_overlap,**extra_args)

def getNLTKTextSplitter(config: Dict) -> NLTKTextSplitter:
    chunk_size = config.get("chunk_size", 1000)
    chunk_overlap = config.get("chunk_overlap", 50)
    extra_args = {k: v for k, v in config.items() if k not in ["type", "chunk_size", "chunk_overlap"]}

    return NLTKTextSplitter(chunk_size=chunk_size,
                                           chunk_overlap=chunk_overlap,**extra_args)

def getSpacyTextSplitter(config: Dict) -> SpacyTextSplitter:
    chunk_size = config.get("chunk_size", 1000)
    chunk_overlap = config.get("chunk_overlap", 50)
    extra_args = {k: v for k, v in config.items() if k not in ["type", "chunk_size", "chunk_overlap"]}

    return SpacyTextSplitter(chunk_size=chunk_size,
                                           chunk_overlap=chunk_overlap,**extra_args)
        
