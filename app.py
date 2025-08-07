import streamlit as st
from docx import Document
from docx.shared import Pt
from docx.enum.text import WD_PARAGRAPH_ALIGNMENT
from io import BytesIO

# Simulador de adaptação
def adaptar_questao(questao, tipos):
    enunciado, alternativas, resposta, tem_imagem = questao

    # TDAH e Ansiedade: segmenta o enunciado e simplifica alternativas longas
    if "TDAH" in tipos or "Ansiedade" in tipos:
        enunciado = "\n".join(enunciado.split(". "))
        alternativas = [alt[:100] + "..." if len(alt) > 100 else alt for alt in alternativas]

    # Dislexia: letras minúsculas e capitalização
    if "Dislexia" in tipos:
        enunciado = enunciado.lower().capitalize()

    return (enunciado, alternativas, resposta, tem_imagem)

# Geração de DOCX com dicas e questões
def gerar_docx_com_dicas(questoes, tipos, dicas_por_tipo):
    doc = Document()
    titulo = doc.add_heading("🧠 Prova Adaptada - AdaptaProva", level=1)
    titulo.alignment = WD_PARAGRAPH_ALIGNMENT.CENTER

    if tipos:
        doc.add_heading("🧭 Orientações iniciais", level=2)
        par = doc.add_paragraph()
        par.add_run("Você selecionou: ").bold = True
        par.add_run(", ".join(tipos)).italic = True
        par.add_run(". Aqui estão algumas dicas para você:")

        dicas_combinadas = []
        for t in tipos:
            dicas_combinadas.extend(dicas_por_tipo.get(t, []))
        dicas_combinadas = list(dict.fromkeys(dicas_combinadas))  # remove duplicatas

        for dica in dicas_combinadas:
            doc.add_paragraph("• " + dica, style="List Bullet")

    doc.add_paragraph("\n")

    for i, (enunciado, alternativas, _, tem_imagem) in enumerate(questoes):
        doc.add_heading(f"Questão {i+1}", level=3)
        if tem_imagem:
            doc.add_paragraph("🚩 Esta questão contém uma imagem na versão original.")
        doc.add_paragraph(enunciado)
        for alt in alternativas:
            doc.add_paragraph(f"- {alt}", style="List Bullet")

    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output

# Dicas por neurodivergência
dicas_por_tipo = {
    "TDAH": [
        "Use régua ou dedo para focar na linha.",
        "Leia uma questão por vez.",
        "Ignore distrações externas momentaneamente.",
        "Respire fundo se perder o foco."
    ],
    "Ansiedade": [
        "Faça pausas curtas para respirar.",
        "Lembre-se de que você pode voltar a questões difíceis.",
        "Evite se pressionar pelo tempo.",
        "Pense positivo: você pode fazer isso."
    ],
    "Dislexia": [
        "Leia em voz baixa se possível.",
        "Substitua palavras difíceis por sinônimos.",
        "Divida frases grandes em partes menores.",
        "Use marca-texto se tiver em mãos."
    ]
}

# Interface Streamlit
st.title("🧠 AdaptaProva - Gerador de Provas Acessíveis")

tipos = st.multiselect("Selecione as neurodivergências do aluno:", ["TDAH", "Ansiedade", "Dislexia"])

# Questões exemplo
questoes_originais = [
    ("Qual é a capital do Brasil? A cidade é conhecida por sua arquitetura moderna.",
     ["São Paulo", "Brasília", "Rio de Janeiro", "Belo Horizonte"], "Brasília", False),

    ("Observe a imagem e responda: Qual animal está representado?",
     ["Gato", "Cachorro", "Leão", "Cavalo"], "Leão", True)
]

if st.button("📄 Gerar Prova Adaptada"):
    questoes = [adaptar_questao(q, tipos) for q in questoes_originais]

    # Pré-visualização na tela
    for i, (enunciado, alternativas, _, tem_imagem) in enumerate(questoes):
        st.markdown(f"### Questão {i+1}")
        if tem_imagem:
            st.info("🚩 Esta questão contém uma imagem na versão original.")
        st.write(enunciado)
        for alt in alternativas:
            st.write(f"- {alt}")

    # Geração do DOCX com dicas
    docx_file = gerar_docx_com_dicas(questoes, tipos, dicas_por_tipo)
    st.download_button(
        label="📥 Baixar Prova Adaptada (.docx)",
        data=docx_file,
        file_name="prova_adaptada.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
