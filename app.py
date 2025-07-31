import streamlit as st
import fitz  # PyMuPDF
import docx
import re
from io import BytesIO
from docx.shared import Pt
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

st.set_page_config(page_title="AdaptaProva", layout="centered")

st.title("🧠 AdaptaProva - Provas Adaptadas para Alunos com Neurodivergência")
st.markdown("Envie uma prova em PDF com texto selecionável e selecione a neurodivergência do aluno para gerar uma versão adaptada.")

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
    texto = re.sub(r'(?<!\n)\n(?!\n)', ' ', texto)
    texto = re.sub(r'(\w)-\s+(\w)', r'\1\2', texto)
    texto = re.sub(r'\n{2,}', '\n\n', texto)
    return texto

def extrair_questoes(texto):
    # Captura blocos que se iniciam com 'Questão', número e conteúdo, até a próxima questão ou fim do texto.
    padrao = re.compile(r'(?:Quest[aã]o\s*\d+[\s:–-]*)((?:.|\n)*?)(?=(?:Quest[aã]o\s*\d+[\s:–-]*)|$)', re.IGNORECASE)
    questoes = padrao.findall(texto)
    questoes_validas = []
    for q in questoes:
        # Considera válida se tiver pelo menos duas alternativas (A e B) no início de linha
        alternativas = re.findall(r'^[A-E][).]', q, re.MULTILINE)
        if len(alternativas) >= 2 and len(q.strip()) > 40:
            questoes_validas.append(q.strip())
    return questoes_validas[:5]

def formatar_questao(texto):
    # Separa o enunciado das alternativas
    linhas = texto.split('\n')
    enunciado = []
    alternativas = []
    for linha in linhas:
        if re.match(r'^[A-E][).]', linha.strip()):
            alternativas.append(linha.strip())
        elif linha.strip():
            enunciado.append(linha.strip())
    return ' '.join(enunciado).strip(), alternativas

def set_font_paragraph(paragraph, size=14, bold=False):
    for run in paragraph.runs:
        run.font.name = 'Arial'
        run.font.size = Pt(size)
        run.font.bold = bold
        r = run._element
        r.rPr.rFonts.set(qn('w:eastAsia'), 'Arial')

def set_spacing(paragraph, space_after=18):
    p = paragraph._element
    pPr = p.get_or_add_pPr()
    spacing = OxmlElement('w:spacing')
    spacing.set(qn('w:after'), str(space_after*20))  # Espaço depois em TWIPs
    spacing.set(qn('w:line'), '360')  # Espaçamento 1.5 linhas
    spacing.set(qn('w:lineRule'), 'auto')
    pPr.append(spacing)

if uploaded_file and tipo:
    if st.button("🔄 Gerar Prova Adaptada"):
        with st.spinner("Processando..."):
            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            texto = ""
            for page in doc:
                texto += page.get_text()
            texto = limpar_quebras(texto)

            # Exibe o texto extraído para depuração
            st.text_area("Texto extraído do PDF (para depuração):", texto, height=300)

            questoes = extrair_questoes(texto)
            st.write(f"Quantidade de
