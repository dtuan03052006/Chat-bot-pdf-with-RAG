import os
import re
import unicodedata
import pdfplumber

# 1. BẢNG MÃ & REGEX XỬ LÝ TIẾNG VIỆT CHUYÊN SÂU
VN_CHARS = (
    "a-zA-Z"
    "àáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩị"
    "òóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ"
    "ÀÁẢÃẠĂẰẮẲẴẶÂẦẤẨẪẬÈÉẺẼẸÊỀẾỂỄỆÌÍỈĨỊ"
    "ÒÓỎÕỌÔỒỐỔỖỘƠỜỚỞỠỢÙÚỦŨỤƯỪỨỬỮỰỲÝỶỸỴĐ"
)
# 1.1 Sửa lỗi từ bị vỡ ký tự (VD: "đ ư ợ c" -> "được", "q u y" -> "quy")
BROKEN_WORD_RE = re.compile(
    rf"(?<![{VN_CHARS}])([{VN_CHARS}])(?: ([{VN_CHARS}])){{1,6}}(?![{VN_CHARS}])"
)

# 1.2 Lọc Header, Footer, Số trang, watermark thường gặp
HEADER_FOOTER_PATTERNS = [
    r"(?i)Trang\s+\d+(\s*/\s*\d+)?",                   # Trang 1 / 10
    r"(?i)Page\s+\d+(\s+of\s+\d+)?",                   # Page 1 of 10
    r"(?i)CÔNG\s*BÁO/Số\s*[\d\s\+\-]+/[^\n]+",         # Header Công báo
    r"(?m)^\s*\d+\s*$",                                # Dòng chỉ chứa mỗi số trang lẻ loi
]

# 1.3 Nhận diện tiêu đề, mục, điều luật để KHÔNG gộp nhầm đoạn
HEADING_PATTERN = re.compile(
    r"^(Chương\s+[IVXLCDM\d]+|Điều\s+\d+|Mục\s+\d+|\d+\.|\([a-z\d]+\)|[a-zđ]\)|\-|\+)\b",
    re.IGNORECASE
)

# 2. CÁC HÀM LÀM SẠCH VĂN BẢN
def clean_VN_text(text):
    if not text:
        return ""

    text=unicodedata.normalize("NFC",text)

    for p in HEADER_FOOTER_PATTERNS:
        text=re.sub(p,"",text)

    text=re.sub(rf"([{VN_CHARS}]+)-\s*\n\s*([{VN_CHARS}]+)", r"\1\2", text)
    def _merge_chars(match):
        return match.group(0).replace(" ", "")
    text = BROKEN_WORD_RE.sub(_merge_chars, text)
    text = re.sub(r"[ \t]+", " ", text)
    return text.strip()

def rebuild_paragraphs(raw_text: str) -> str:
    """
    Ghép các dòng bị ngắt bừa bãi trong PDF thành đoạn văn hoàn chỉnh,
    nhưng vẫn giữ nguyên ranh giới của Tiêu đề, Điều, Khoản.
    """
    lines = [line.strip() for line in raw_text.splitlines() if line.strip()]
    if not lines:
        return ""
    rebuilt = [lines[0]]
    for i in range(1, len(lines)):
        curr_line = lines[i]
        prev_line = rebuilt[-1]
        # Nếu dòng hiện tại là Tiêu đề / Điều / Khoản mới -> Tách đoạn
        # Hoặc dòng trước kết thúc bằng dấu câu và dòng này viết hoa chữ cái đầu -> Tách đoạn
        is_new_clause = HEADING_PATTERN.match(curr_line)
        is_sentence_end = prev_line.endswith((".", "!", "?", ":", ";")) and curr_line[0].isupper()
        if is_new_clause or is_sentence_end:
            rebuilt.append(curr_line)
        else:
            # Ngược lại, đây chỉ là 1 câu dài bị PDF cắt xuống dòng -> Ghép lại
            rebuilt[-1] = f"{prev_line} {curr_line}"
    return "\n\n".join(rebuilt)

# 3. BÓC TÁCH BẢNG BIỂU (TABLE TO MARKDOWN)
def table_to_markdown(table: list) -> str:
    """Chuyển đổi bảng biểu trích xuất từ PDF sang định dạng bảng Markdown chuẩn."""
    if not table or len(table) < 2:
        return ""
    cleaned_table = []
    for row in table:
        cleaned_row = [re.sub(r"\s+", " ", str(cell or "")).strip() for cell in row]
        if any(cleaned_row):  # Không lấy dòng rỗng hoàn toàn
            cleaned_table.append(cleaned_row)
    if len(cleaned_table) < 2:
        return ""
    header = cleaned_table[0]
    separator = ["---"] * len(header)
    rows = cleaned_table[1:]
    md_lines = [
        "| " + " | ".join(header) + " |",
        "| " + " | ".join(separator) + " |",
    ]
    for row in rows:
        # Bổ sung ô rỗng nếu hàng thiếu cột
        while len(row) < len(header):
            row.append("")
        md_lines.append("| " + " | ".join(row[:len(header)]) + " |")
    return "\n" + "\n".join(md_lines) + "\n"

# 4. HÀM CHÍNH: XỬ LÝ TOÀN BỘ FILE PDF
def process_pdf(pdf_path: str) -> list[dict]:

    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Không tìm thấy file: {pdf_path}")
    
    file_name = os.path.basename(pdf_path)
    processed_pages = []
    print(f" Đang xử lý file PDF chuyên sâu: {file_name}...")

    with pdfplumber.open(pdf_path) as pdf:
        for idx, page in enumerate(pdf.pages):
            page_num = idx + 1
            
            # 1. Trích xuất các Bảng biểu có trên trang trước
            tables = page.extract_tables()
            table_markdowns = []
            for t in tables:
                md = table_to_markdown(t)
                if md:
                    table_markdowns.append(md)

            # 2. Trích xuất Text thông thường (loại trừ vùng chứa bảng nếu có)
            # pdfplumber tự động phân tích layout tọa độ (tránh lỗi 2 cột)
            raw_text = page.extract_text(layout=False) or ""

            # 3. Làm sạch văn bản và ghép đoạn thông minh
            cleaned_text = clean_VN_text(raw_text)
            final_text = rebuild_paragraphs(cleaned_text)

            # 4. Ghép Text và Bảng lại với nhau
            if table_markdowns:
                final_text += "\n\n[BẢNG DỮ LIỆU ĐÍNH KÈM TRANG]:\n" + "\n".join(table_markdowns)
            if final_text.strip():
                processed_pages.append({
                    "content": final_text,
                    "metadata": {
                        "source": file_name,
                        "page": page_num,
                        "has_table": len(table_markdowns) > 0,
                        "char_count": len(final_text)
                    }
                })
    print(f"Hoàn tất xử lý {len(processed_pages)} trang!")
    return processed_pages