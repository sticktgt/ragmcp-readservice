from .splitters import getRecursiveCharacterTextSplitter, getTokenTextSplitter, getNLTKTextSplitter

def get_splitter(splitter_type: str, config: dict):
    
    splitters = config.get("splitters", {})
    splitter_config = splitters.get(splitter_type, {})
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
