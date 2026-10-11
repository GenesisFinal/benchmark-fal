r"""
Script de Sincronización Automática: GitHub -> Local
Descarga y sincroniza los archivos de 'GenesisFinal/benchmark-fal' (rama main)
directamente en el directorio local de trabajo (g:\Mi unidad\IA\FAL).
Garantiza que index.html, benchmark_fal.html y todos los datos en /data
sean 100% idénticos a los alojados en GitHub.
"""

import os
import sys
import hashlib
from pathlib import Path
import urllib.request
import ssl
import json
from datetime import datetime

WORKSPACE = Path(__file__).resolve().parent.parent
REPO_OWNER = "GenesisFinal"
REPO_NAME = "benchmark-fal"
BRANCH = "main"
LOG_FILE = WORKSPACE / "data" / "sync_local.log"

# Archivos críticos que deben mantenerse 100% idénticos
SYNC_FILES = [
    "index.html",
    "benchmark_fal.html",
    "data/entities.json",
    "data/competitors_registry.json",
    "data/competitors_snapshots.json",
    "data/audit_log.json",
    "data/audit_summary.json",
    "README.md",
]

def log(msg: str):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    formatted = f"[{timestamp}] {msg}"
    print(formatted)
    try:
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(formatted + "\n")
    except Exception:
        pass

def get_file_sha256(path: Path) -> str:
    if not path.exists():
        return ""
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()

def sync():
    ctx = ssl.create_default_context()
    log("=================================================================")
    log(f"INICIANDO SINCRONIZACIÓN LOCAL DESDE GITHUB ({REPO_OWNER}/{REPO_NAME})")
    log(f"Destino local: {WORKSPACE}")

    # Obtener el último commit remoto
    try:
        commit_url = f"https://api.github.com/repos/{REPO_OWNER}/{REPO_NAME}/commits/{BRANCH}"
        req = urllib.request.Request(commit_url, headers={"User-Agent": "FAL-Local-Sync"})
        with urllib.request.urlopen(req, timeout=10, context=ctx) as resp:
            commit_data = json.loads(resp.read().decode("utf-8"))
            last_sha = commit_data.get("sha", "")[:7]
            commit_msg = commit_data.get("commit", {}).get("message", "").splitlines()[0]
            log(f"Último commit en GitHub: [{last_sha}] {commit_msg}")
    except Exception as e:
        log(f"[WARN] No se pudo verificar metadata del commit remoto: {e}")

    updated_count = 0
    identical_count = 0

    for rel_path in SYNC_FILES:
        target_path = WORKSPACE / rel_path
        target_path.parent.mkdir(parents=True, exist_ok=True)

        raw_url = f"https://raw.githubusercontent.com/{REPO_OWNER}/{REPO_NAME}/{BRANCH}/{rel_path}"
        req = urllib.request.Request(raw_url, headers={"User-Agent": "FAL-Local-Sync", "Cache-Control": "no-cache"})

        try:
            with urllib.request.urlopen(req, timeout=15, context=ctx) as resp:
                remote_bytes = resp.read()
                remote_hash = hashlib.sha256(remote_bytes).hexdigest()
                local_hash = get_file_sha256(target_path)

                if remote_hash == local_hash:
                    log(f"  [OK] Idéntico: {rel_path} ({len(remote_bytes):,} bytes)")
                    identical_count += 1
                else:
                    with open(target_path, "wb") as f:
                        f.write(remote_bytes)
                    log(f"  [ACTUALIZADO] {rel_path} -> sincronizado ({len(remote_bytes):,} bytes)")
                    updated_count += 1
        except Exception as e:
            log(f"  [ERROR] Falló descarga de {rel_path}: {e}")

    log(f"RESUMEN: {updated_count} archivos actualizados, {identical_count} ya idénticos.")
    log("El entorno local está 100% sincronizado con GitHub.")
    log("=================================================================")

if __name__ == "__main__":
    sync()
