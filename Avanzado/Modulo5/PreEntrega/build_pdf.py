# -*- coding: utf-8 -*-
"""Arma el PDF único de la pre-entrega del Módulo 5 a partir de Pieza1..5 (*.md) + capturas/.

- Portada con el índice al pie de la página: cada entrada es un link interno a su pieza, con el n.º de página.
- Cada pieza empieza en una página nueva; número de página al pie; marcadores (outline) del PDF.

Uso:  python build_pdf.py
Genera PreEntrega_Modulo5_JulioMartinWaisburd.html (intermedio) y .pdf (con Edge/Chrome headless).
"""
import os, re, glob, subprocess, datetime, pathlib, tempfile, time
import markdown

HERE = os.path.dirname(os.path.abspath(__file__))
NOMBRE = "PreEntrega_Modulo5_JulioMartinWaisburd"
PIEZAS = sorted(glob.glob(os.path.join(HERE, "Pieza[1-5]_*.md")))
BROWSERS = [r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
            r"C:\Program Files\Google\Chrome\Application\chrome.exe"]

CSS = """
@page { size: A4; margin: 16mm 14mm 18mm;
        @bottom-center { content: counter(page) " / " counter(pages); font: 8.5pt 'Segoe UI', Arial, sans-serif; color: #6b7280; } }
@page portada { @bottom-center { content: none; } }
body { font-family: 'Segoe UI', Arial, sans-serif; font-size: 10.5pt; color: #1d1d1f; line-height: 1.45; margin: 0; }
h1 { font-size: 17pt; color: #0b3d5c; border-bottom: 2px solid #0b3d5c; padding-bottom: 4px; margin-top: 0; }
h2 { font-size: 13pt; color: #0b3d5c; margin-top: 18px; break-after: avoid; }
table { border-collapse: collapse; width: 100%; margin: 8px 0; font-size: 9pt; break-inside: avoid; }
th, td { border: 1px solid #c8ccd2; padding: 4px 6px; vertical-align: top; text-align: left; }
th { background: #eef2f6; }
img { max-width: 100%; border: 1px solid #c8ccd2; margin: 6px 0 2px; break-inside: avoid; }
pre { background: #f5f6f8; border: 1px solid #dde1e6; padding: 8px; font-size: 8.3pt; white-space: pre-wrap; break-inside: avoid; }
code { font-family: Consolas, monospace; font-size: 9pt; }
blockquote { border-left: 3px solid #0b3d5c; margin: 8px 0; padding: 2px 10px; color: #333; background: #f7f9fb; }
.pieza { break-before: page; }
.portada { page: portada; height: 262mm; display: flex; flex-direction: column; justify-content: space-between; text-align: center; }
.portada .titulo { padding-top: 55mm; }
.portada h1 { border: none; font-size: 22pt; }
.portada p { font-size: 12pt; margin: 6px; }
.indice { text-align: left; border-top: 2px solid #0b3d5c; padding-top: 8px; }
.indice h2 { margin: 0 0 6px; font-size: 12pt; }
.indice a { display: flex; align-items: baseline; color: #1d1d1f; text-decoration: none; font-size: 11pt; padding: 3px 0; }
.indice a .t { flex: none; }
.indice a .dots { flex: 1; border-bottom: 1px dotted #9aa3ad; margin: 0 6px; transform: translateY(-3px); }
.indice a .p { flex: none; color: #0b3d5c; font-weight: 600; }
"""

def html_doc(body):
    return f'<!doctype html><html lang="es"><head><meta charset="utf-8"><base href="{pathlib.Path(HERE).as_uri()}/"><title>{NOMBRE}</title><style>{CSS}</style></head><body>{body}</body></html>'

def render(body, pdf_path):
    """Imprime el HTML a PDF con el navegador headless y devuelve la cantidad de páginas."""
    h = os.path.splitext(pdf_path)[0] + ".html"
    open(h, "w", encoding="utf-8").write(html_doc(body))
    exe = next(b for b in BROWSERS if os.path.exists(b))
    perfil = tempfile.mkdtemp(prefix="pdf_profile_")  # perfil aislado: no se engancha a un Edge/Chrome abierto
    subprocess.run([exe, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--generate-pdf-document-outline",
                    f"--user-data-dir={perfil}", f"--print-to-pdf={pdf_path}", pathlib.Path(h).as_uri()],
                   check=True, timeout=120, capture_output=True)
    # El navegador puede volver antes de terminar de escribir el archivo: esperar a que exista y su tamaño se estabilice.
    previo, t0 = -1, time.time()
    while time.time() - t0 < 60:
        tam = os.path.getsize(pdf_path) if os.path.exists(pdf_path) else -1
        if tam > 0 and tam == previo and open(pdf_path, "rb").read().rstrip().endswith(b"%%EOF"):
            break
        previo = tam
        time.sleep(1)
    return len(re.findall(rb"/Type\s*/Page[^s]", open(pdf_path, "rb").read()))

def main():
    md = markdown.Markdown(extensions=["tables", "fenced_code"])
    titulos, secciones = [], []
    for i, p in enumerate(PIEZAS, 1):
        txt = open(p, encoding="utf-8").read()
        titulos.append(txt.splitlines()[0].lstrip("# ").strip())
        secciones.append(f'<section class="pieza" id="pieza-{i}">{md.reset().convert(txt)}</section>')

    # 1) Pasada de medición: cuántas páginas ocupa cada pieza (cada una arranca en hoja nueva).
    tmp = tempfile.mkdtemp(prefix="pdf_medir_")
    paginas = [render(s.replace('class="pieza"', 'class="medir"'), os.path.join(tmp, f"p{i}.pdf"))
               for i, s in enumerate(secciones, 1)]
    inicio, pag = [], 2  # la portada es la página 1
    for n in paginas:
        inicio.append(pag); pag += n

    # 2) Pasada final: portada con índice al pie (links internos + n.º de página) y las piezas.
    hoy = datetime.date.today().strftime("%d/%m/%Y")
    indice = "".join(f'<a href="#pieza-{i}"><span class="t">{t}</span><span class="dots"></span><span class="p">pág. {p}</span></a>'
                     for i, (t, p) in enumerate(zip(titulos, inicio), 1))
    portada = f"""<section class="portada">
<div class="titulo"><h1>Pre-entrega Módulo 5<br>El Cerebro Documental de la IA (RAG)</h1>
<p>Proyecto integrador <b>AgendaBot</b> — AI Automation Avanzado (Coderhouse)</p>
<p><b>Julio Martín Waisburd</b></p><p>{hoy}</p></div>
<nav class="indice"><h2>Índice</h2>{indice}</nav></section>"""
    pdf = os.path.join(HERE, NOMBRE + ".pdf")
    if os.path.exists(pdf):
        os.remove(pdf)
    total = render(portada + "".join(secciones), pdf)
    esperado = 1 + sum(paginas)
    print("PDF:", pdf, f"({os.path.getsize(pdf)//1024} KB) | páginas: {total} (esperado {esperado})")
    for t, p, n in zip(titulos, inicio, paginas):
        print(f"  pág. {p:>2} ({n} hoja/s)  {t}")
    if total != esperado:
        print("  ATENCIÓN: el total no coincide; revisar los saltos de página.")

if __name__ == "__main__":
    main()
