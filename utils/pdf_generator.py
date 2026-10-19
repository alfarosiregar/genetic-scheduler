"""Modul utilitas untuk ekspor Kalender Mingguan ke format PDF Landscape menggunakan ReportLab."""

import html
import io
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfgen import canvas
from utils.genetic_algorithm import parse_waktu


class _NumberedCanvas(canvas.Canvas):
    """Canvas kustom dua-tahap untuk penomoran halaman dinamis dan footer cetak."""

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
        self.setFont("Helvetica", 7.5)
        self.setFillColor(colors.HexColor("#64748B"))
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(34, 25, 841.89 - 34, 25)
        page_text = f"Halaman {self._pageNumber} dari {page_count}"
        self.drawRightString(841.89 - 34, 14, page_text)
        self.restoreState()


def _esc(val):
    """Mengamankan teks dari karakter khusus XML agar tidak menimbulkan error parsing ReportLab."""
    return html.escape(str(val) if val is not None else "")


def generate_weekly_calendar_pdf(df_cal, prodi_filter="Semua Program Studi", stats=None):
    """Menghasilkan file PDF Kalender Mingguan dalam orientasi Landscape berstandar A4."""
    buf = io.BytesIO()

    # Ukuran A4 Landscape: lebar 841.89 pt, tinggi 595.27 pt
    doc = SimpleDocTemplate(
        buf,
        pagesize=landscape(A4),
        leftMargin=34,
        rightMargin=34,
        topMargin=26,
        bottomMargin=36,
    )

    title_style = ParagraphStyle(
        "DocTitle",
        fontName="Helvetica-Bold",
        fontSize=14,
        leading=17,
        textColor=colors.HexColor("#1E1B4B"),
    )
    meta_style = ParagraphStyle(
        "DocMeta",
        fontName="Helvetica",
        fontSize=8,
        leading=10,
        textColor=colors.HexColor("#1E293B"),
    )
    day_hdr = ParagraphStyle(
        "DayHeader",
        fontName="Helvetica-Bold",
        fontSize=9,
        leading=11,
        alignment=1,
        textColor=colors.white,
    )

    c_time_ok = ParagraphStyle(
        "CardTimeOk",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor("#312E81"),
    )
    c_time_err = ParagraphStyle(
        "CardTimeErr",
        fontName="Helvetica-Bold",
        fontSize=7.5,
        leading=9,
        textColor=colors.HexColor("#991B1B"),
    )
    c_course = ParagraphStyle(
        "CardCourse",
        fontName="Helvetica-Bold",
        fontSize=7.8,
        leading=9.5,
        textColor=colors.HexColor("#0F172A"),
    )
    c_meta = ParagraphStyle(
        "CardMeta",
        fontName="Helvetica",
        fontSize=6.8,
        leading=8.5,
        textColor=colors.HexColor("#475569"),
    )

    elements = []

    # Judul dokumen
    elements.append(Paragraph("KALENDER JADWAL KULIAH MINGGUAN", title_style))
    elements.append(Spacer(1, 6))

    # Kotak ringkasan metadata
    total_kelas = len(df_cal)
    meta_data = [
        [
            Paragraph(f"<b>Program Studi:</b> {_esc(prodi_filter)}", meta_style),
            Paragraph(f"<b>Total Jadwal:</b> {total_kelas} Kelas", meta_style),
            Paragraph(f"<b>Tanggal Ekspor:</b> {datetime.now().strftime('%d/%m/%Y %H:%M WIB')}", meta_style),
        ]
    ]

    meta_table = Table(meta_data, colWidths=[280, 220, 273.89])
    meta_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#F8FAFC")),
                ("BOX", (0, 0), (-1, -1), 0.8, colors.HexColor("#CBD5E1")),
                ("INNERGRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ]
        )
    )
    elements.append(meta_table)
    elements.append(Spacer(1, 8))

    # Daftar kolom hari
    days_order = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]
    extra_days = [d for d in df_cal["Hari"].unique() if d not in days_order] if "Hari" in df_cal.columns else []
    active_days = days_order + extra_days

    # Pastikan setidaknya hari default aktif
    if "Hari" not in df_cal.columns or not any(d in df_cal["Hari"].values for d in active_days):
        active_days = ["Senin", "Selasa", "Rabu", "Kamis", "Jumat"]

    num_cols = len(active_days)
    usable_width = 841.89 - 68  # 773.89 pt
    col_w = usable_width / num_cols

    classes_by_day = {}
    for d in active_days:
        if "Hari" in df_cal.columns:
            sub = df_cal[df_cal["Hari"] == d].copy()
            if not sub.empty:
                sub["_sort"] = sub["Waktu"].apply(lambda w: (parse_waktu(w) or (9999, 9999))[0])
                classes_by_day[d] = sub.sort_values("_sort").to_dict("records")
            else:
                classes_by_day[d] = []
        else:
            classes_by_day[d] = []

    header_cells = [
        Paragraph(
            f"<b>{d.upper()}</b><br/><font size=7 color='#C7D2FE'>({len(classes_by_day[d])} Kelas)</font>",
            day_hdr,
        )
        for d in active_days
    ]
    table_rows = [header_cells]

    max_rows = max(len(classes_by_day[d]) for d in active_days)
    if max_rows == 0:
        table_rows.append([Paragraph("<font color='#94A3B8'><i>Tidak ada kelas terjadwal</i></font>", c_meta)] * num_cols)
    else:
        for r_idx in range(max_rows):
            row_cells = []
            for d in active_days:
                c_list = classes_by_day[d]
                if r_idx < len(c_list):
                    item = c_list[r_idx]
                    is_conflict = item.get("Konflik", 0) > 0
                    time_txt = f"WAKTU: {_esc(item.get('Waktu', ''))}" + (" [! BENTROK]" if is_conflict else "")
                    t_style = c_time_err if is_conflict else c_time_ok
                    bg_color = "#FEF2F2" if is_conflict else "#FFFFFF"
                    border_color = "#FCA5A5" if is_conflict else "#E2E8F0"

                    card_content = [
                        Paragraph(time_txt, t_style),
                        Spacer(1, 1.5),
                        Paragraph(f"<b>{_esc(item.get('Mata Kuliah', ''))}</b>", c_course),
                        Spacer(1, 1),
                        Paragraph(f"Dosen: {_esc(item.get('Dosen', ''))}", c_meta),
                        Paragraph(
                            f"Ruang: <b>{_esc(item.get('Ruangan', ''))}</b> | {_esc(item.get('Prodi', ''))} ({item.get('SKS', 2)} SKS)",
                            c_meta,
                        ),
                    ]
                    mini_t = Table([[card_content]], colWidths=[col_w - 6])
                    mini_t.setStyle(
                        TableStyle(
                            [
                                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor(bg_color)),
                                ("BOX", (0, 0), (-1, -1), 0.7, colors.HexColor(border_color)),
                                ("TOPPADDING", (0, 0), (-1, -1), 3),
                                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
                                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                            ]
                        )
                    )
                    row_cells.append(mini_t)
                else:
                    row_cells.append("")
            table_rows.append(row_cells)

    cal_table = Table(table_rows, colWidths=[col_w] * num_cols, repeatRows=1)
    cal_table.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E1B4B")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                ("TOPPADDING", (0, 0), (-1, -1), 2),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
                ("LEFTPADDING", (0, 0), (-1, -1), 2),
                ("RIGHTPADDING", (0, 0), (-1, -1), 2),
            ]
        )
    )
    elements.append(cal_table)

    doc.build(elements, canvasmaker=_NumberedCanvas)
    return buf.getvalue()
