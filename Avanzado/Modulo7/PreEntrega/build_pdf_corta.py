# -*- coding: utf-8 -*-
"""Arma la versión corta (4 hojas, una por componente de la consigna) de la pre-entrega del Módulo 7
a partir de corta/Pieza1..4.md. Sin portada: el encabezado va en la primera hoja.
El diagrama de la coreografía se toma de Pieza2_Arquitectura.md (versión extendida) para no duplicarlo.

Uso:  python build_pdf_corta.py
"""
import os, re, glob, datetime, tempfile, sys
import markdown
import build_pdf as B

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

HERE = os.path.dirname(os.path.abspath(__file__))
B.NOMBRE = "PreEntrega_Modulo7_JulioMartinWaisburd_versión_corta_V3"
B.CSS += """
@page { size: A4; margin: 11mm 12mm 13mm; }
body { font-size: 8.9pt; line-height: 1.3; }
h1 { font-size: 14pt; margin: 0 0 6px; padding-bottom: 3px; }
h2 { font-size: 11pt; margin: 10px 0 4px; }
p { margin: 4px 0; }
table { font-size: 7.9pt; margin: 4px 0; }
th, td { padding: 2.5px 5px; }
blockquote { margin: 4px 0; padding: 1px 8px; }
ol, ul { margin: 3px 0; padding-left: 18px; }
li { margin: 1px 0; }
.encabezado { font-size: 8.5pt; color: #374151; border-bottom: 1px solid #c8ccd2; padding-bottom: 4px; margin-bottom: 8px; }
.diagrama svg { width: 72%; display: block; margin: 2px auto; }
"""

def main():
    ext = open(os.path.join(HERE, "Pieza2_Arquitectura.md"), encoding="utf-8").read()
    diagrama = re.search(r'<div class="diagrama">.*?</div>', ext, re.S).group(0)
    hoy = datetime.date.today().strftime("%d/%m/%Y")
    md = markdown.Markdown(extensions=["tables", "fenced_code"])
    secciones = []
    for i, p in enumerate(sorted(glob.glob(os.path.join(HERE, "corta", "Pieza[1-4].md"))), 1):
        txt = open(p, encoding="utf-8").read().replace("{{DIAGRAMA}}", diagrama).replace("{{FECHA}}", hoy)
        clase = "medir" if i == 1 else "pieza"
        secciones.append(f'<section class="{clase}" id="pieza-{i}">{md.reset().convert(txt)}</section>')

    # Cada componente tiene que entrar en una sola hoja
    tmp = tempfile.mkdtemp(prefix="pdf_corta_")
    paginas = [B.render(s.replace('class="pieza"', 'class="medir"'), os.path.join(tmp, f"p{i}.pdf"))
               for i, s in enumerate(secciones, 1)]
    for i, n in enumerate(paginas, 1):
        print(f"  página {i}: {n} hoja/s" + ("" if n == 1 else "  <-- NO ENTRA EN UNA HOJA"))

    pdf = os.path.join(HERE, B.NOMBRE + ".pdf")
    if os.path.exists(pdf):
        os.remove(pdf)
    total = B.render("".join(secciones), pdf)
    print("PDF:", pdf, f"({os.path.getsize(pdf)//1024} KB) | hojas: {total}")

if __name__ == "__main__":
    main()
