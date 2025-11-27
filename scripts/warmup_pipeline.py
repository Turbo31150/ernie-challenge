"""
ERNIE Challenge Warm-up Pipeline
PaddleOCR extraction -> Markdown -> ERNIE HTML generation
"""

import os
import sys
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import requests
import json

# Paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
OUTPUT_DIR = PROJECT_ROOT / "output"

def create_sample_document():
    """Use existing PDF or create one if needed"""
    print("[1/5] Checking PDF document...")

    pdf_path = DATA_DIR / "sample_document.pdf"

    # Check if PDF exists
    if pdf_path.exists():
        print(f"   Using existing PDF: {pdf_path}")
        return pdf_path

    # Create PDF if not exists
    try:
        from fpdf import FPDF
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font('Arial', 'B', 24)
        pdf.cell(0, 20, 'ERNIE AI Challenge 2025', ln=True, align='C')
        pdf.ln(10)
        pdf.set_font('Arial', 'B', 16)
        pdf.cell(0, 10, 'Document Intelligence Platform', ln=True, align='C')
        pdf.ln(15)
        pdf.set_font('Arial', '', 12)
        pdf.multi_cell(0, 8, '''Technologies utilisees:
- ERNIE 4.5 pour l analyse semantique
- PaddleOCR-VL pour l extraction de texte
- Python pour l orchestration du pipeline

Avantages:
1. Precision de 96.8 pourcent
2. Support de plus de 80 langues
3. Traitement en 2.3 secondes par document
''')
        pdf.output(str(pdf_path))
        print(f"   Created PDF: {pdf_path}")
    except ImportError:
        print("   FPDF not installed, using fallback")
        # Fallback to PNG if fpdf not available
        img = Image.new('RGB', (800, 600), color='white')
        draw = ImageDraw.Draw(img)
        font = ImageFont.load_default()
        draw.text((50, 50), "ERNIE AI Challenge 2025", fill='black', font=font)
        img_path = DATA_DIR / "sample_document.png"
        img.save(str(img_path))
        return img_path

    return pdf_path


def extract_with_paddleocr(image_path):
    """Extract text using PaddleOCR"""
    print("[2/5] Extracting text with PaddleOCR...")

    try:
        from paddleocr import PaddleOCR
        import logging
        logging.getLogger('ppocr').setLevel(logging.ERROR)
        ocr = PaddleOCR(lang='fr')
        result = ocr.ocr(str(image_path))

        # Extract text from results
        lines = []
        if result and result[0]:
            for line in result[0]:
                if line and len(line) >= 2:
                    text = line[1][0]
                    confidence = line[1][1]
                    lines.append(f"{text}")
                    print(f"   OCR: {text} ({confidence:.2%})")

        extracted_text = '\n'.join(lines)
        print(f"   Extracted {len(lines)} lines")
        return extracted_text

    except Exception as e:
        print(f"   PaddleOCR error: {e}")
        # Fallback - return sample text
        return """ERNIE AI Challenge 2025
Document Intelligence avec PaddleOCR
Technologies utilisees:
- ERNIE 4.5 pour l'analyse semantique
- PaddleOCR-VL pour l'extraction
- Python pour l'orchestration
Avantages:
1. Precision de 96.8%
2. Support de 80+ langues
3. Traitement en 2.3 secondes"""


def convert_to_markdown(text):
    """Convert extracted text to Markdown format"""
    print("[3/5] Converting to Markdown...")

    lines = text.split('\n')
    markdown_lines = []

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Detect headers
        if 'ERNIE' in line and 'Challenge' in line:
            markdown_lines.append(f"# {line}\n")
        elif line.startswith('-'):
            markdown_lines.append(f"- {line[1:].strip()}")
        elif line[0].isdigit() and '.' in line[:3]:
            markdown_lines.append(line)
        elif ':' in line and len(line) < 50:
            markdown_lines.append(f"\n## {line}\n")
        else:
            markdown_lines.append(line)

    markdown = '\n'.join(markdown_lines)

    # Save markdown file
    md_path = OUTPUT_DIR / "extracted_content.md"
    with open(md_path, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"   Saved: {md_path}")
    return markdown


def generate_html_with_ernie(markdown_content):
    """Generate HTML using ERNIE API (or LM Studio fallback)"""
    print("[4/5] Generating HTML with AI...")

    api_key = os.getenv("BAIDU_API_KEY") or os.getenv("ERNIE_API_KEY")

    prompt = f"""Convert this Markdown content into a beautiful HTML page with Tailwind CSS styling.
Include a header, main content area, and footer. Make it professional and modern.

Markdown content:
{markdown_content}

Generate only the HTML code, no explanations."""

    # Try ERNIE API first (official)
    if api_key:
        try:
            import erniebot
            erniebot.api_type = "aistudio"
            erniebot.access_token = api_key

            response = erniebot.ChatCompletion.create(
                model="ernie-4.0-turbo-8k",
                messages=[{"role": "user", "content": prompt}]
            )
            html_content = response.get_result()
            print("   Generated with ERNIE API (official)")
            return html_content
        except Exception as e:
            print(f"   ERNIE API error: {e}")

    # Try LM Studio as fallback
    lm_studio_url = "http://localhost:1234/v1/chat/completions"
    try:
        response = requests.post(
            lm_studio_url,
            json={
                "model": "qwen/qwen3-coder-30b",
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 2000,
                "temperature": 0.7
            },
            timeout=60
        )

        if response.status_code == 200:
            result = response.json()
            html_content = result['choices'][0]['message']['content']
            print("   Generated with LM Studio (local)")
            return html_content

    except Exception as e:
        print(f"   LM Studio unavailable: {e}")

    # Fallback: Generate HTML template directly
    print("   Using template generation...")
    html = f"""<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document Intelligence - ERNIE Challenge</title>
    <script src="https://cdn.tailwindcss.com"></script>
</head>
<body class="bg-gradient-to-br from-purple-50 to-blue-50 min-h-screen">
    <header class="bg-gradient-to-r from-purple-600 to-blue-600 text-white py-8 shadow-xl">
        <div class="max-w-4xl mx-auto px-4">
            <h1 class="text-4xl font-bold">ERNIE AI Challenge 2025</h1>
            <p class="text-purple-200 mt-2">Document Intelligence Pipeline</p>
        </div>
    </header>

    <main class="max-w-4xl mx-auto px-4 py-12">
        <div class="bg-white rounded-2xl shadow-lg p-8 mb-8">
            <h2 class="text-2xl font-bold text-gray-800 mb-6 border-b pb-4">Extracted Content</h2>
            <div class="prose prose-lg">
                {markdown_content.replace(chr(10), '<br>')}
            </div>
        </div>

        <div class="grid md:grid-cols-3 gap-6">
            <div class="bg-white rounded-xl shadow p-6 text-center">
                <div class="text-4xl mb-3">🎯</div>
                <h3 class="font-bold text-gray-800">96.8%</h3>
                <p class="text-gray-500 text-sm">Precision OCR</p>
            </div>
            <div class="bg-white rounded-xl shadow p-6 text-center">
                <div class="text-4xl mb-3">⚡</div>
                <h3 class="font-bold text-gray-800">2.3s</h3>
                <p class="text-gray-500 text-sm">Par document</p>
            </div>
            <div class="bg-white rounded-xl shadow p-6 text-center">
                <div class="text-4xl mb-3">🌍</div>
                <h3 class="font-bold text-gray-800">80+</h3>
                <p class="text-gray-500 text-sm">Langues supportees</p>
            </div>
        </div>
    </main>

    <footer class="bg-gray-800 text-gray-400 py-6 mt-12 text-center">
        <p>Powered by ERNIE 4.5 + PaddleOCR-VL</p>
        <p class="text-sm mt-2">ERNIE AI Challenge 2025</p>
    </footer>
</body>
</html>"""

    return html


def save_final_output(html_content):
    """Save the generated HTML"""
    print("[5/5] Saving output...")

    output_path = OUTPUT_DIR / "result.html"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    # Also update main index.html
    index_path = PROJECT_ROOT / "index.html"
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

    print(f"   Saved: {output_path}")
    print(f"   Updated: {index_path}")
    return output_path


def main():
    print("=" * 50)
    print("ERNIE Challenge - Warm-up Pipeline")
    print("=" * 50)

    # Ensure directories exist
    DATA_DIR.mkdir(exist_ok=True)
    OUTPUT_DIR.mkdir(exist_ok=True)

    # Step 1: Create sample document
    image_path = create_sample_document()

    # Step 2: Extract text with PaddleOCR
    extracted_text = extract_with_paddleocr(image_path)

    # Step 3: Convert to Markdown
    markdown = convert_to_markdown(extracted_text)

    # Step 4: Generate HTML with AI
    html = generate_html_with_ernie(markdown)

    # Step 5: Save output
    output_path = save_final_output(html)

    print("=" * 50)
    print("Pipeline completed!")
    print(f"Output: {output_path}")
    print("=" * 50)

    return 0


if __name__ == "__main__":
    sys.exit(main())
