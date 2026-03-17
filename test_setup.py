import sys
print("Python yorumlayıcı:", sys.executable)

try:
    import PyPDF2
    print("✅ PyPDF2 yüklü")
except ImportError:
    print("❌ PyPDF2 yüklü değil")

try:
    import transformers
    print("✅ transformers yüklü")
except ImportError:
    print("❌ transformers yüklü değil")

try:
    import sentence_transformers
    print("✅ sentence-transformers yüklü")
except ImportError:
    print("❌ sentence-transformers yüklü değil")

try:
    import gradio
    print("✅ gradio yüklü")
except ImportError:
    print("❌ gradio yüklü değil")