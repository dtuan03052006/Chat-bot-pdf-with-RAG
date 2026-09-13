def build_prompt(question, context):

    prompt = f"""
Bạn là một trợ lý AI.

Hãy trả lời câu hỏi dựa trên Context.

Không được tự bịa thông tin.

Nếu Context không chứa câu trả lời,
hãy nói rằng bạn không tìm thấy thông tin
trong tài liệu.

Context:
{context}

Question:
{question}

Answer:
"""

    return prompt

question = "FastAPI là gì?"

context = """
FastAPI là một web framework hiện đại
dành cho Python.

FastAPI hỗ trợ xây dựng API.
"""

prompt = build_prompt(
    question,
    context
)

print(prompt)