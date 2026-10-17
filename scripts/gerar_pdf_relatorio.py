#!/usr/bin/env python3
"""
Compilador profissional de relatório Markdown para PDF (ReportLab)
Gera docs/relatorio_etapa2.pdf formatado e paginado para entrega oficial.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.pdfgen import canvas

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_number(num_pages)
            super().showPage()
        super().save()

    def draw_page_number(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 9)
        self.setFillColor(colors.HexColor("#6b7280"))
        
        # Cabeçalho
        self.drawString(54, 750, "Laboratório de Banco de Dados — UCB 2026/2 | Prof. Samuel Novais Moura Júnior")
        self.setStrokeColor(colors.HexColor("#e5e7eb"))
        self.setLineWidth(0.5)
        self.line(54, 742, 558, 742)
        
        # Rodapé
        self.line(54, 45, 558, 45)
        page_text = f"Página {self._pageNumber} de {page_count}"
        self.drawRightString(558, 32, page_text)
        self.drawString(54, 32, "Sistema de Gestão de Contas e Operações Bancárias — Relatório Final N2")
        self.restoreState()

def build_pdf(md_path, pdf_path):
    with open(md_path, "r", encoding="utf-8") as f:
        md_text = f.read()

    doc = SimpleDocTemplate(
        pdf_path,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=64,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#1e3a8a'),
        spaceAfter=12
    )

    h1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=14,
        leading=18,
        textColor=colors.HexColor('#1e40af'),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=11,
        leading=15,
        textColor=colors.HexColor('#1f2937'),
        spaceBefore=10,
        spaceAfter=4,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor('#374151'),
        spaceAfter=6
    )

    bullet_style = ParagraphStyle(
        'Bullet',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9,
        leading=13,
        textColor=colors.HexColor('#374151'),
        leftIndent=15,
        firstLineIndent=-10,
        spaceAfter=3
    )

    code_style = ParagraphStyle(
        'Code',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10,
        textColor=colors.HexColor('#111827'),
        backColor=colors.HexColor('#f3f4f6'),
        spaceBefore=4,
        spaceAfter=6,
        leftIndent=10,
        rightIndent=10
    )

    story = []
    lines = md_text.split('\n')
    
    in_code_block = False
    code_buffer = []
    in_table = False
    table_rows = []

    for line in lines:
        sline = line.strip()

        if sline.startswith('```'):
            if in_code_block:
                in_code_block = False
                code_text = "<br/>".join(code_buffer)
                story.append(Paragraph(code_text, code_style))
                code_buffer = []
            else:
                in_code_block = True
            continue

        if in_code_block:
            safe_line = line.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace(' ', '&nbsp;')
            code_buffer.append(safe_line)
            continue

        # Tabelas Markdown
        if sline.startswith('|') and sline.endswith('|'):
            if '---' in sline:
                continue
            cells = [c.strip() for c in sline.split('|')[1:-1]]
            table_rows.append(cells)
            in_table = True
            continue
        elif in_table:
            # Finaliza tabela
            if table_rows:
                formatted_data = []
                for r_idx, row in enumerate(table_rows):
                    f_row = []
                    for c_idx, cell in enumerate(row):
                        cell_clean = cell.replace('**', '')
                        if r_idx == 0:
                            f_row.append(Paragraph(f"<b>{cell_clean}</b>", ParagraphStyle('TH', parent=body_style, fontName='Helvetica-Bold', fontSize=8.5, leading=11, textColor=colors.HexColor('#ffffff'))))
                        else:
                            f_row.append(Paragraph(cell_clean, ParagraphStyle('TD', parent=body_style, fontSize=8, leading=10.5)))
                    formatted_data.append(f_row)

                col_widths = [doc.width / len(table_rows[0])] * len(table_rows[0])
                if len(table_rows[0]) == 3:
                    col_widths = [doc.width * 0.25, doc.width * 0.45, doc.width * 0.30]
                elif len(table_rows[0]) == 2:
                    col_widths = [doc.width * 0.35, doc.width * 0.65]

                t = Table(formatted_data, colWidths=col_widths)
                t.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e40af')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('VALIGN', (0, 0), (-1, -1), 'TOP'),
                    ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
                    ('TOPPADDING', (0, 0), (-1, -1), 4),
                    ('LEFTPADDING', (0, 0), (-1, -1), 5),
                    ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                    ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e5e7eb')),
                    ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')])
                ]))
                story.append(t)
                story.append(Spacer(1, 8))
            table_rows = []
            in_table = False

        if not sline:
            continue

        if sline.startswith('# '):
            story.append(Paragraph(sline[2:].replace('**', ''), title_style))
            story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#1e40af'), spaceAfter=12))
        elif sline.startswith('## '):
            story.append(Paragraph(sline[3:].replace('**', ''), h1_style))
            story.append(HRFlowable(width="100%", thickness=0.8, color=colors.HexColor('#93c5fd'), spaceAfter=6))
        elif sline.startswith('### '):
            story.append(Paragraph(sline[4:].replace('**', ''), h2_style))
        elif sline.startswith('- ') or sline.startswith('* '):
            text = sline[2:]
            safe_text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(f"• {safe_text}", bullet_style))
        elif sline.startswith('1. ') or sline.startswith('2. ') or sline.startswith('3. ') or sline.startswith('4. ') or sline.startswith('5. ') or sline.startswith('6. ') or sline.startswith('7. ') or sline.startswith('8. ') or sline.startswith('9. ') or sline.startswith('10. '):
            safe_text = sline.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            story.append(Paragraph(safe_text, bullet_style))
        elif sline == '---':
            story.append(Spacer(1, 6))
            story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor('#e5e7eb'), spaceAfter=8))
        else:
            safe_text = sline.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
            # formata negrito markdown simples
            import re
            safe_text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', safe_text)
            safe_text = re.sub(r'`(.*?)`', r'<font name="Courier">\1</font>', safe_text)
            story.append(Paragraph(safe_text, body_style))

    doc.build(story, canvasmaker=NumberedCanvas)
    print(f"PDF gerado com sucesso: {pdf_path}")

if __name__ == "__main__":
    build_pdf("docs/relatorio_etapa2.md", "docs/relatorio_etapa2.pdf")
