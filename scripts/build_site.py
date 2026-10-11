"""
Script para sincronizar y compilar index.html con el dataset de entities.json
y los datos del último escaneo de auditoría automatizada.
"""

import json
import re
from datetime import datetime
import zoneinfo
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
DATA_DIR = WORKSPACE / "data"

def get_argentina_time() -> str:
    try:
        tz = zoneinfo.ZoneInfo("America/Argentina/Buenos_Aires")
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()
    return now.strftime("%d/%m/%Y %H:%M ART")

def build():
    entities_path = DATA_DIR / "entities.json"
    summary_path = DATA_DIR / "audit_summary.json"
    index_path = WORKSPACE / "index.html"

    if not entities_path.exists():
        print(f"[ERROR] {entities_path} no existe.")
        return False

    with open(entities_path, "r", encoding="utf-8") as f:
        entities = json.load(f)

    audit_time = get_argentina_time()
    online_count = len(entities)
    failed_count = 0

    if summary_path.exists():
        try:
            with open(summary_path, "r", encoding="utf-8") as f:
                summary = json.load(f)
                audit_time = summary.get("last_run_formatted", audit_time)
                online_count = summary.get("online_count", online_count)
                failed_count = summary.get("failed_count", 0)
        except Exception as e:
            print(f"[WARN] Error leyendo audit_summary.json: {e}")

    with open(index_path, "r", encoding="utf-8") as f:
        html = f.read()

    # 1. Inyectar dataset entitiesData
    entities_json_str = json.dumps(entities, ensure_ascii=False, indent=6)
    pattern = r'(const entitiesData = )\[[\s\S]*?\];(\s*//)'
    if re.search(pattern, html):
        html = re.sub(pattern, f'\\1{entities_json_str};\\2', html, count=1)
    else:
        print("[WARN] No se encontró el bloque const entitiesData en index.html")

    # 2. Inyectar o actualizar badge de auditoría en la franja y subheader
    status_label = f"{online_count}/{len(entities)} online"
    if failed_count > 0:
        status_label += f" ({failed_count} reintento diferido)"

    audit_html_snippet = f"""<div class="text-[11px] text-slate-500 flex flex-col sm:flex-row sm:items-center justify-between gap-1 pt-2">
          <div class="flex items-center gap-2 flex-wrap">
            <span class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-emerald-50 text-emerald-800 text-[10px] font-bold border border-emerald-200">
              <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 animate-pulse"></span>
              <span>Bot Scraper Activo: Monitoreo Diario 2x/día</span>
            </span>
            <span class="text-slate-400">•</span>
            <span class="text-slate-600 text-[10px] font-medium">Última auditoría: <strong>{audit_time}</strong> ({status_label})</span>
          </div>
          <span id="rowCount" class="font-extrabold text-[#0e2e73]">Mostrando {len(entities)} entidades</span>
        </div>"""

    # Reemplazar la barra de recuento anterior
    old_row_count_regex = r'<div class="text-\[11px\] text-slate-400 flex items-center justify-between">[\s\S]*?</div>'
    if re.search(old_row_count_regex, html):
        html = re.sub(old_row_count_regex, audit_html_snippet, html, count=1)
    elif '<div class="text-[11px] text-slate-500 flex flex-col sm:flex-row' in html:
        sub_regex = r'<div class="text-\[11px\] text-slate-500 flex flex-col sm:flex-row[\s\S]*?</div>\s*</div>'
        html = re.sub(sub_regex, audit_html_snippet + '\n      </div>', html, count=1)

    with open(index_path, "w", encoding="utf-8") as f:
        f.write(html)

    # Mantener sincronizado benchmark_fal.html
    bench_path = WORKSPACE / "benchmark_fal.html"
    if bench_path.exists():
        with open(bench_path, "w", encoding="utf-8") as f:
            f.write(html)

    print(f"[OK] index.html y benchmark_fal.html actualizados con éxito. Timestamp: {audit_time}")
    return True

if __name__ == "__main__":
    build()
