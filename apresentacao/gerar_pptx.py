"""Converte o PDF da apresentacao em .pptx, uma pagina por slide.

Cada pagina vira uma imagem em alta resolucao ocupando o slide inteiro, entao
o resultado e visualmente identico ao PDF. O texto nao fica editavel no
PowerPoint -- para editar, mexa no slides.template.html e gere tudo de novo.

Uso:
    .venv/bin/python apresentacao/gerar_pptx.py
"""

import pathlib

import pymupdf
from pptx import Presentation
from pptx.util import Emu

AQUI = pathlib.Path(__file__).parent
PDF = AQUI / "apresentacao.pdf"
PPTX = AQUI / "apresentacao.pptx"
PASTA_PNG = AQUI / "paginas"
ESCALA = 3  # 3x o tamanho do PDF, para nao serrilhar no projetor

# 16:9 widescreen, o mesmo formato do PDF (13,333 x 7,5 polegadas)
LARGURA = Emu(12192000)
ALTURA = Emu(6858000)


def main():
    if not PDF.exists():
        raise SystemExit(f"{PDF} nao existe. Gere o PDF antes.")

    PASTA_PNG.mkdir(exist_ok=True)
    documento = pymupdf.open(PDF)

    apresentacao = Presentation()
    apresentacao.slide_width = LARGURA
    apresentacao.slide_height = ALTURA
    em_branco = apresentacao.slide_layouts[6]  # layout sem placeholders

    for numero, pagina in enumerate(documento, start=1):
        imagem = pagina.get_pixmap(matrix=pymupdf.Matrix(ESCALA, ESCALA))
        caminho = PASTA_PNG / f"slide{numero}.png"
        imagem.save(caminho)

        slide = apresentacao.slides.add_slide(em_branco)
        slide.shapes.add_picture(str(caminho), 0, 0, width=LARGURA, height=ALTURA)
        print(f"  slide {numero}: {imagem.width}x{imagem.height} px")

    total = len(documento)
    apresentacao.save(PPTX)
    documento.close()
    print(f"\n  {total} slides gravados em {PPTX.relative_to(AQUI.parent)}")


if __name__ == "__main__":
    main()
