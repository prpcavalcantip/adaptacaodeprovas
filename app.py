import streamlit as st
import fitz  # PyMuPDF
import docx
import re
from io import BytesIO
from docx.shared import Pt, RGBColor
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT

st.set_page_config(page_title="AdaptaProva", layout="centered")

st.title("🧠 AdaptaProva - Provas Adaptadas para Alunos com Neurodivergência")
st.markdown("Envie uma prova em PDF com texto selecionável e selecione a neurodivergência do aluno para gerar uma versão adaptada.")

# Banco de dicas para cada neurodivergência
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

def eh_cabecalho(bloco):
    if re.search(r'^[A-E][\).]', bloco, flags=re.MULTILINE):
        return False
    if re.search(r'Aluno|Professor|Turma|Data', bloco, re.IGNORECASE):
        return True
    if len(bloco.strip()) < 40:
        return True
    return False

def separar_enunciado_alternativas(texto):
    partes = re.split(r'(?=^[A-Ea-e][\).])', texto, flags=re.MULTILINE)
    enunciado = partes[0].strip()
    alternativas = [alt.strip() for alt in partes[1:]] if len(partes) > 1 else []
    return enunciado, alternativas

def contem_imagem_ou_referencia(texto):
    padrao_img = r"(figura|imagem|ilustração|gráfico|esquema|diagrama|tabela|abaixo|acima|ao lado|veja a|observe a|\/Im\d+\.\w{3,4})"
    return bool(re.search(padrao_img, texto, re.IGNORECASE))

def selecionar_objetivas(blocos, total_questoes=10):
    questoes = []
    for bloco in blocos:
        enunciado, alternativas = separar_enunciado_alternativas(bloco)
        if len(alternativas) >= 3 and len(enunciado) < 700:
            tem_imagem = contem_imagem_ou_referencia(bloco)
            questoes.append((enunciado, alternativas, bloco, tem_imagem))
    questoes.sort(key=lambda x: len(x[0]))
    questoes_sem_img = [q for q in questoes if not q[3]]
    questoes_com_img = [q for q in questoes if q[3]]
    selecionadas = questoes_sem_img[:total_questoes]
    if len(selecionadas) < total_questoes:
        selecionadas += questoes_com_img[:total_questoes - len(selecionadas)]
    if len(selecionadas) < total_questoes:
        return None
    return selecionadas[:total_questoes]

if uploaded_file and tipo:
    if st.button("🔄 Gerar Prova Adaptada"):
        with st.spinner("Processando..."):

            doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
            texto = ""
            for page in doc:
                texto += page.get_text()

            if texto.strip() == "":
                st.warning("O PDF enviado não contém texto selecionável. Por favor, envie um PDF digital ou convertido para texto.")
                st.stop()

            blocos = re.split(r'\bQUEST[ÃA]O[\s:]*\d+\b[:.]?', texto, flags=re.IGNORECASE)
            blocos = [b.strip() for b in blocos if b.strip()]
            if blocos and eh_cabecalho(blocos[0]):
                blocos = blocos[1:]

            questoes = selecionar_objetivas(blocos, total_questoes=10)

            if not questoes:
                st.error("Não foram encontradas exatamente 10 questões objetivas válidas nesse PDF (sem imagem ou com aviso). Envie outro arquivo ou verifique o formato.")
                st.stop()

            docx_file = docx.Document()
            docx_file.add_heading("Prova Adaptada", 0)

            style = docx_file.styles["Normal"]
            style.font.size = Pt(14)
            style.font.name = "Arial"
            style.paragraph_format.line_spacing = 1.5
            style.paragraph_format.space_after = Pt(10)

            docx_file.add_paragraph("💡 DICAS PARA O ALUNO:", style="List Bullet")
            for dica in dicas_por_tipo[tipo]:
                p = docx_file.add_paragraph(dica, style="List Bullet")
                p.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                p.paragraph_format.line_spacing = 1.5
            docx_file.add_paragraph("")

            for i, (enunciado, alternativas, bloco_original, tem_imagem) in enumerate(questoes):
                titulo = docx_file.add_paragraph()
                run = titulo.add_run(f"QUESTÃO {i+1}")
                run.bold = True
                titulo.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                titulo.paragraph_format.space_after = Pt(2)

                if tem_imagem:
                    aviso_par = docx_file.add_paragraph()
                    aviso_run = aviso_par.add_run("🚩 Incluir imagem da prova original")
                    aviso_run.bold = True
                    # Definir cor vermelha
                    aviso_run.font.color.rgb = RGBColor(255, 0, 0)
                    aviso_par.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                    aviso_par.paragraph_format.line_spacing = 1.5
                    aviso_par.paragraph_format.space_after = Pt(6)
                    aviso_run.font.size = Pt(14)
                    aviso_run.font.name = "Arial"

                enun_par = docx_file.add_paragraph(enunciado)
                enun_par.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                enun_par.paragraph_format.line_spacing = 1.5
                enun_par.paragraph_format.space_after = Pt(15)
                for run in enun_par.runs:
                    run.font.size = Pt(14)
                    run.font.name = "Arial"

                docx_file.add_paragraph("")

                for alt in alternativas:
                    alt_par = docx_file.add_paragraph(alt)
                    alt_par.alignment = WD_PARAGRAPH_ALIGNMENT.LEFT
                    alt_par.paragraph_format.line_spacing = 1.5
                    alt_par.paragraph_format.space_after = Pt(6)
                    for run in alt_par.runs:
                        run.font.size = Pt(14)
                        run.font.name = "Arial"

                docx_file.add_paragraph("")

            buffer = BytesIO()
            docx_file.save(buffer)
            buffer.seek(0)

            st.success("✅ Prova adaptada gerada com sucesso!")
            st.download_button(
                label="📥 Baixar Prova Adaptada (.docx)",
                data=buffer,
                file_name="prova_adaptada.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
