#chunking
def recursive_split(text,chunk_size,separators):
    if len(text) < chunk_size:
        return [text]
    if not separators:
        return [
            text[i: i + chunk_size ] for i in range(0,len(text),chunk_size)
        ]
    separator=separators[0]
    parts=text.split(separator)
    chunks=[]
    curr=""
    for part in parts:
        if(len(curr) + len(part) + len(separator) <= chunk_size):
            curr += part + separator
        else:
            if curr:
                chunks.append(curr.strip())
            if len(part) > chunk_size:
                sub_text=recursive_split(part,chunk_size,separator[1:])
                chunk_size.extend(sub_text)
                curr=""
            else:
                curr=part + separator
    if curr:
        chunks.append(curr.strip)

    return chunks

#Lancgchain
from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter= RecursiveCharacterTextSplitter(
    chunk_size=100,
    chunk_overlap=20,
)

text = """
Python là một ngôn ngữ lập trình phổ biến.
Python được sử dụng nhiều trong AI và Data Science.

FastAPI là framework dùng để xây dựng API bằng Python.
FastAPI được sử dụng để xây dựng backend.

RAG là kỹ thuật kết hợp LLM với hệ thống tìm kiếm.
RAG giúp LLM sử dụng dữ liệu bên ngoài.
"""
chunks=splitter.split_text(text)

for i, chunk in enumerate(chunks):
    print(f"Chunk {i}:")
    print(chunk)
    print()
    