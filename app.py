import streamlit as st
import fitz  # PyMuPDF
import docx
import re
from io import BytesIO
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

st.set_page_config(page_title="AdaptaProva", layout="centered")

st.title("🧠 AdaptaProva - Provas Adaptadas para Alunos com Neurodivergência")
st.markdown("Envie uma prova em PDF com texto selecionável e selecione a neurodivergência do aluno para gerar uma versão adaptada.")

# Dicas por tipo de neurodivergência
dicas_por_tipo = {
    "TDAH": [
        "Destaque palavras-chave da pergunta.",
        "Leia a pergunta duas vezes antes de escolher a resposta.",
        "Tente eliminar as alternativas claramente erradas primeiro."
    ],
    "TEA": [
        "Preste atenção nas palavras que indicam ordem, como 'primeiro', 'depois', 'por fim'.",
        "Leia com calma. Respire fundo antes de cada pergunta.",
        "Use rascunho para organizar o que entendeu da questão."
    ],
    "Ansiedade": [
        "Lembre-se: você pode fazer uma pergunta de cada vez com calma.",
        "Respire fundo antes de começar cada questão.",
        "Você está preparado. Confie no seu raciocínio!"
    ]
}

uploaded_file = st.file_uploader("📄 Envie a prova em PDF", type=["pdf"])
tipo = st.selectbox("🧠 Neurodivergência do aluno:", ["TDAH", "TEA", "Ansiedade"])

def limpar_quebras(texto):
    texto = re.sub(r'(?<!\n)\n(?!\n)', ' ', texto)  # quebra de linha leve → espaço
    texto = re.sub(r'(\w)-\s+(\w)', r'\1\2', texto)  # junta palavras quebradas com hífen
    texto = re.sub(r'\n{2,}', '\n\n', texto)  # múltiplas quebras → parágrafo
    return texto

if uploaded_file and tipo:
    if st.button("🔄 Gerar Prova Adaptada"):
        with st.spinner("Processando..."):

            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            texto = ""
            for page in doc:
                texto += page.get_text()

            texto = limpar_quebras(texto)

            # Separar questões por "QUESTÃO"
            blocos = re.split(r'\bQUESTÃO\s+\d+', texto)
            blocos = [b.strip() for b in blocos if b.strip()]
            if len(blocos) > 10:
                blocos = blocos[1:]
            blocos = blocos[:10]

            docx_file = docx.Document()
            docx_file.ad_
