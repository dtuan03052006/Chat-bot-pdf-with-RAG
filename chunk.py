

from langchain_text_splitters import RecursiveCharacterTextSplitter

def chunking(pages_data, chunk_size=600, chunk_overlap=100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=["\n\n", "\n", ". ", " ", ""]
    )
    all_chunks=[]

    for page in pages_data:
        chunks=splitter.split_text(page["content"])
        for c in chunks:
            all_chunks.append({
                "text" : c,
                "source": page["metadata"]["source"],
                "page" : page["metadata"]["page"]
            }
            )
    return all_chunks

    