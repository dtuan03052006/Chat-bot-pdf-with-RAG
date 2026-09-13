import ollama
from tokenizer_embeding_vector_db import retrieve_top_k


SYSTEM_PROMPT = """Bạn là trợ lý AI chuyên gia giải đáp tài liệu.
Nhiệm vụ: Trả lời câu hỏi dựa HOÀN TOÀN vào các đoạn trích dẫn được cung cấp dưới đây.
Quy tắc bắt buộc:
1. Chỉ trả lời thông tin có trong ngữ cảnh.
2. Trích dẫn rõ nguồn tài liệu và số trang (Ví dụ: [Nguồn: file.pdf, Trang 3]).
3. Nếu tài liệu không đề cập, hãy nói thẳng: "Tài liệu được cung cấp không chứa thông tin này." Tuyệt đối không tự bịa đặt."""

def answer_ques(query,top_k=3):
    retrieve_chunks=retrieve_top_k(query,top_k)
    if not retrieve_chunks:
            return {"answer": "Không tìm thấy dữ liệu liên quan trong tài liệu.", "sources": []}
    content_block=[]
    for idx,c in enumerate(retrieve_chunks,1):
        block=f"[Trích dẫn {idx}] (Tài liệu: {c['source']}, Trang: {c['page']})\n{c['text']}"
        content_block.append(block)

    context_text="\n\n".join(content_block)

    user_prompt = f"""Dưới đây là ngữ cảnh trích xuất từ tài liệu:{context_text}
        Câu hỏi: {query}
        Câu trả lời:"""

    response = ollama.chat(
        model="qwen2.5:7b",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
    )
    return {
        "answer": response["message"]["content"],
        "sources": retrieve_chunks
    }
