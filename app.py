"""
Document Intelligence with ERNIE & PaddleOCR
Simple, clean, official API only
"""

import os
from pathlib import Path

class DocumentProcessor:
    """Public-facing processor - simple ERNIE + PaddleOCR"""

    def __init__(self):
        self.api_key = os.getenv("ERNIE_API_KEY")
        self.ocr = None
        self._init_ocr()

    def _init_ocr(self):
        try:
            from paddleocr import PaddleOCR
            self.ocr = PaddleOCR(lang='fr')
        except (ImportError, Exception) as e:
            print(f"PaddleOCR init: {e}")
            self.ocr = None

    def extract_text(self, file_path):
        """Extract text from PDF/image using PaddleOCR"""
        if not self.ocr:
            return ""
        result = self.ocr.ocr(str(file_path))
        text = "\n".join([line[1][0] for page in result for line in page if line])
        return text

    def analyze_with_ernie(self, text, prompt=None):
        """Analyze text using ERNIE API"""
        if not prompt:
            prompt = f"Analyze this document and provide key insights:\n\n{text}"
        # ERNIE API call placeholder
        return {"status": "ready", "prompt": prompt[:200]}

    def process_document(self, file_path):
        """Main processing pipeline: PDF -> OCR -> ERNIE -> Output"""
        text = self.extract_text(file_path)
        analysis = self.analyze_with_ernie(text)
        return {"text": text, "analysis": analysis}

    def generate_html(self, content, output_path="output/index.html"):
        """Generate HTML output for GitHub Pages"""
        html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Intelligence - ERNIE</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gray-100 p-8">
    <div class="max-w-4xl mx-auto bg-white rounded-lg shadow-lg p-6">
        <h1 class="text-3xl font-bold text-blue-600 mb-4">Document Analysis</h1>
        <div class="prose">{content}</div>
        <footer class="mt-8 text-sm text-gray-500">
            Powered by ERNIE 4.5 & PaddleOCR-VL
        </footer>
    </div>
</body>
</html>"""
        Path(output_path).parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
        return output_path


if __name__ == "__main__":
    import sys
    processor = DocumentProcessor()

    if len(sys.argv) > 1:
        result = processor.process_document(sys.argv[1])
        print(result)
    else:
        print("Usage: python app.py <document_path>")
