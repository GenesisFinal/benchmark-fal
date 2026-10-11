"""
Bot Automatizado de Monitoreo de Competidores FAL
Ejecuta la revisión de las páginas oficiales de las 28 entidades del mercado,
detecta cambios en comisiones u ofertas, gestiona caídas con reintentos diferidos
y actualiza el dataset y sitio web en forma 100% autónoma.
"""

import os
import sys
import json
import time
import hashlib
import urllib.request
import urllib.error
import ssl
from datetime import datetime
import zoneinfo
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parent.parent
DATA_DIR = WORKSPACE / "data"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 (ACA-FAL-Benchmark-Bot/2.0)"

def get_argentina_time():
    try:
        tz = zoneinfo.ZoneInfo("America/Argentina/Buenos_Aires")
        now = datetime.now(tz)
    except Exception:
        now = datetime.now()
    return now

def fetch_url(url: str, max_retries: int = 2, timeout: int = 6) -> tuple[bool, str, int, str]:
    """
    Intenta descargar una URL con reintentos rápidos y retroceso.
    Retorna: (éxito, contenido_texto, http_code, mensaje_error)
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    for attempt in range(1, max_retries + 1):
        try:
            req = urllib.request.Request(
                url,
                headers={
                    "User-Agent": USER_AGENT,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "es-AR,es;q=0.9,en;q=0.8",
                    "Cache-Control": "no-cache"
                }
            )
            with urllib.request.urlopen(req, timeout=timeout, context=ctx) as response:
                code = response.getcode()
                raw_bytes = response.read(150000)  # Limitar a primeros 150KB para velocidad
                try:
                    text = raw_bytes.decode("utf-8")
                except UnicodeDecodeError:
                    text = raw_bytes.decode("latin-1", errors="ignore")
                return True, text, code, ""
        except urllib.error.HTTPError as e:
            if attempt == max_retries:
                return False, "", e.code, f"HTTPError {e.code}"
            time.sleep(1)
        except Exception as e:
            if attempt == max_retries:
                return False, "", 0, str(e)[:50]
            time.sleep(1)

    return False, "", 0, "Max retries exceeded"

def extract_meaningful_text(html: str) -> str:
    """Extrae texto simplificado removiendo scripts y estilos para hashing estable."""
    import re
    clean = re.sub(r'<script[\s\S]*?</script>', ' ', html, flags=re.IGNORECASE)
    clean = re.sub(r'<style[\s\S]*?</style>', ' ', clean, flags=re.IGNORECASE)
    clean = re.sub(r'<[^>]+>', ' ', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean

def run_monitoring():
    start_time = get_argentina_time()
    now_iso = start_time.isoformat()
    now_formatted = start_time.strftime("%d/%m/%Y %H:%M ART")

    registry_path = DATA_DIR / "competitors_registry.json"
    snapshots_path = DATA_DIR / "competitors_snapshots.json"
    audit_log_path = DATA_DIR / "audit_log.json"
    summary_path = DATA_DIR / "audit_summary.json"

    if not registry_path.exists():
        print(f"[ERROR] No se encontró el registro: {registry_path}", flush=True)
        return

    with open(registry_path, "r", encoding="utf-8") as f:
        registry = json.load(f)

    snapshots = {}
    if snapshots_path.exists():
        try:
            with open(snapshots_path, "r", encoding="utf-8") as f:
                snapshots = json.load(f)
        except Exception:
            snapshots = {}

    audit_log = []
    if audit_log_path.exists():
        try:
            with open(audit_log_path, "r", encoding="utf-8") as f:
                audit_log = json.load(f)
        except Exception:
            audit_log = []

    online_count = 0
    failed_count = 0
    changes_detected = 0
    results = {}

    print("=================================================================", flush=True)
    print(f"  INICIANDO MONITOREO DE COMPETIDORES FAL: {now_formatted}", flush=True)
    print(f"  Total de entidades a auditar: {len(registry)}", flush=True)
    print("=================================================================", flush=True)

    for i, comp in enumerate(registry, 1):
        c_id = comp["id"]
        c_name = comp["name"]
        primary_url = comp.get("primary_url", "")
        secondary_url = comp.get("secondary_url", "")

        print(f"[{i}/{len(registry)}] Auditando {c_name} ...", end=" ", flush=True)

        ok, content, code, err = fetch_url(primary_url, max_retries=2, timeout=6)
        used_url = primary_url

        if not ok and secondary_url:
            print(f"(reintento en fallback) ...", end=" ", flush=True)
            ok, content, code, err = fetch_url(secondary_url, max_retries=1, timeout=6)
            used_url = secondary_url

        if ok:
            online_count += 1
            text = extract_meaningful_text(content)
            h = hashlib.sha256(text.encode("utf-8")).hexdigest()

            prev_snapshot = snapshots.get(c_id, {})
            prev_hash = prev_snapshot.get("hash", "")
            has_changed = (prev_hash != "" and prev_hash != h)

            if has_changed:
                changes_detected += 1
                print(f"[CAMBIO DETECTADO] (HTTP {code})", flush=True)
                audit_log.append({
                    "timestamp": now_iso,
                    "timestamp_formatted": now_formatted,
                    "entity_id": c_id,
                    "entity_name": c_name,
                    "url": used_url,
                    "event": "OFERTA_ACTUALIZADA",
                    "details": "Modificación detectada en el contenido web.",
                    "previous_hash": prev_hash[:12],
                    "new_hash": h[:12]
                })
            else:
                print(f"[OK] (HTTP {code})", flush=True)

            snapshots[c_id] = {
                "entity_name": c_name,
                "url": used_url,
                "last_success": now_iso,
                "last_success_formatted": now_formatted,
                "hash": h,
                "status": "ONLINE",
                "pending_retry": False
            }

            results[c_id] = {
                "status": "ONLINE",
                "http_code": code,
                "pending_retry": False,
                "last_checked": now_iso
            }
        else:
            failed_count += 1
            print(f"[SITIO CAÍDO / TIMEOUT - REINTENTO PENDIENTE]: {err}", flush=True)
            
            audit_log.append({
                "timestamp": now_iso,
                "timestamp_formatted": now_formatted,
                "entity_id": c_id,
                "entity_name": c_name,
                "url": used_url,
                "event": "SITIO_NO_DISPONIBLE",
                "details": f"Error de conexión: {err}. Programado para reintento en el próximo turno.",
                "pending_retry": True
            })

            results[c_id] = {
                "status": "UNREACHABLE",
                "error": err,
                "pending_retry": True,
                "last_checked": now_iso
            }

            if c_id in snapshots:
                snapshots[c_id]["pending_retry"] = True
                snapshots[c_id]["last_error"] = err

        # Guardado iterativo por resiliencia
        with open(snapshots_path, "w", encoding="utf-8") as f:
            json.dump(snapshots, f, ensure_ascii=False, indent=2)

    trimmed_log = audit_log[-200:]
    with open(audit_log_path, "w", encoding="utf-8") as f:
        json.dump(trimmed_log, f, ensure_ascii=False, indent=2)

    summary = {
        "last_run_iso": now_iso,
        "last_run_formatted": now_formatted,
        "total_entities": len(registry),
        "online_count": online_count,
        "failed_count": failed_count,
        "changes_detected": changes_detected,
        "results": results
    }

    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("=================================================================", flush=True)
    print(f"  RESUMEN: {online_count}/{len(registry)} online | {failed_count} con reintento pendiente | {changes_detected} cambios", flush=True)
    print("=================================================================", flush=True)

    try:
        from build_site import build
        build()
    except Exception as e:
        print(f"[WARN] Error al ejecutar build_site: {e}", flush=True)

if __name__ == "__main__":
    run_monitoring()
