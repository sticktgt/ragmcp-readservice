from .splitters import getRecursiveCharacterTextSplitter, getTokenTextSplitter, getNLTKTextSplitter

def get_splitter(splitter_config: dict):
    splitter_type = splitter_config.get("type", "recursive")

    if splitter_type == "RecursiveCharacterTextSplitter":
        return getRecursiveCharacterTextSplitter(splitter_config)
    elif splitter_type == "TokenTextSplitter":
        return getTokenTextSplitter(splitter_config)
    elif splitter_type == "NLTKTextSplitter":
        return getNLTKTextSplitter(splitter_config)
    elif splitter_type == "none":
        return None
    else:
        raise ValueError(f"Unsupported splitter type: {splitter_type}")
