# 🌾 Benchmark de Mercado: Fondo de Asistencia Laboral (FAL) 2026

[![Auditoría Diaria Automatizada del Mercado FAL](https://github.com/GenesisFinal/benchmark-fal/actions/workflows/fal_competitors_monitor.yml/badge.svg)](https://github.com/GenesisFinal/benchmark-fal/actions/workflows/fal_competitors_monitor.yml)
[![GitHub Pages](https://img.shields.io/badge/Deploy-GitHub%20Pages-173b94?logo=github)](https://genesisfinal.github.io/benchmark-fal/)
[![Vigencia](https://img.shields.io/badge/Vigencia-1%20de%20Noviembre%202026-95ca3c)](https://genesisfinal.github.io/benchmark-fal/)

Plataforma analítica y comparativa integral del **Fondo de Asistencia Laboral (FAL)** regulado por la **Ley N° 27.802**, el **Decreto N° 408/2026**, la **RG ARCA N° 5907/2026** y la **RG CNV N° 1167/2026**, brandeada oficialmente con la identidad visual corporativa de **ACA Valores S.A.** (ALyC Propio N° 1304 y ACyDI N° 173 de la CNV).

🌐 **Acceso Público Online:** [https://genesisfinal.github.io/benchmark-fal/](https://genesisfinal.github.io/benchmark-fal/)

---

## 🚀 Funcionalidades Principales

1. **Matriz Comparativa de Mercado (28 Entidades Relevadas):**
   - Análisis de comisiones anuales, vehículos FCI (T+0 / T+1), tiempos de alta de ID FAL, requisitos de reciprocidad y sinergias aseguradoras.
   - Detalle exhaustivo de las ofertas publicadas y las exigencias de *Cuenta Sueldo* impuestas por la banca tradicional.
2. **Comparador Interactivo Uno a Uno (Head-to-Head):**
   - Selector dinámico de los 27 competidores frente a la propuesta superadora de **ACA Valores**.
   - Tres argumentos técnicos, financieros y operativos estructurados por cada entidad.
3. **Simulador de Ahorro y Eficiencia Patronal:**
   - Cálculo en tiempo real de la masa salarial, detracción SIPA (costo patronal $0) y proyección acumulada.
   - Cuantificación del ahorro anual por comisión bonificada al 0% y cálculo exacto de la póliza de Seguro de Vida Colectivo Obligatorio (LCT 20.744) 100% bonificada por 6 meses con **La Segunda Seguros**:
     $$\text{Ahorro Seguro Vida} = \frac{\text{Empleados} \times \text{Salario Promedio} \times 7 \times 6}{1000} \times 0,30$$
4. **Cronograma y Checklist Operativo con Asistencia Humana:**
   - Fechas críticas previas al 1 de Noviembre de 2026.
   - Diferencial exclusivo de ACA Valores: **Oficial Corporativo Humano Asignado 1 a 1** y acompañamiento asistido en tiempo real para la obtención del **ID FAL** (emitido y certificado por medio de **BIND**) y su registración en *Simplificación Registral* de ARCA.
   - Checklist interactivo de 5 pasos con barra de progreso en vivo.
5. **Directorio de 28 Fichas Técnicas:**
   - Resúmenes ejecutivos, perfiles de inversor y pros/contras individuales.
6. **Repositorio Normativo Oficial:**
   - Enlaces directos a los textos completos y vigentes en el Boletín Oficial, InfoLEG y CNV.

---

## 🤖 Sistema de Monitoreo Automatizado 100% Desatendido

El repositorio cuenta con una rutina desatendida ejecutada mediante **GitHub Actions** (`fal_competitors_monitor.yml`) encargada de auditar continuamente la oferta comercial de los 28 participantes:

### Cronograma de Monitoreo:
- **Turno Mañana (09:00 ART / 12:00 UTC):** Barrido completo de las 28 páginas web oficiales.
- **Turno Tarde/Noche (21:00 ART / 00:00 UTC):** Segunda auditoría diaria para capturar actualizaciones vespertinas.
- **Ventanas de Catch-Up y Reintento (15:00 ART y 03:00 ART):** Ejecuciones intermedias dirigidas a reintentar la conexión con cualquier sitio que hubiese presentado caídas o timeouts durante los turnos regulares.
- **Disparador Manual (`workflow_dispatch`):** Permite forzar la auditoría con un solo clic desde la pestaña de Actions en GitHub.

### Tolerancia a Fallos y Resiliencia:
- Cada URL se consulta con hasta **3 reintentos inmediatos con retroceso exponencial** (exponential backoff).
- Si la URL primaria no responde, el bot recurre automáticamente a la URL secundaria de respaldo del operador.
- Si un sitio persiste inaccesible, se registra en `data/audit_log.json` en estado `PENDING_RETRY` y se reintenta en el próximo turno programado, sin detener la auditoría de los demás operadores.
- Al detectarse un cambio en aranceles o promociones, el bot actualiza `data/entities.json`, regenera `index.html` con el timestamp de la última auditoría exitosa y efectúa commit y push automático a la rama `main`, actualizando el sitio de GitHub Pages en tiempo real.

---

## 🏛️ Entidades Relevadas

| Categoría | Entidades |
| :--- | :--- |
| **Líder Recomendado** | **ACA Valores** (Grupo Cooperativo ACA • La Segunda • BIND) |
| **Banca Privada** | BBVA, Galicia, Banco Macro, Santander, Banco Patagonia, ICBC, Supervielle, Credicoop, Banco del Sol, Hipotecario, Banco Coinag |
| **Banca Pública** | Banco Nación, Banco Provincia, Banco Ciudad, Bancor (Córdoba) |
| **ALyCs de Mercado** | Allaria, Balanz, PPI, Consultatio (One 618), SBS Fondos, Mariva Asset Management |
| **Fintechs** | Cocos Capital, IOL InvertirOnline, Bull Market Brokers |
| **Gestoras Boutique** | Toronto Trust, Compass Group, Adcap Asset Management |

---

## 🛠️ Estructura del Repositorio

```
benchmark-fal/
├── index.html                           <- Aplicación web oficial lista para GitHub Pages
├── benchmark_fal.html                   <- Master local sincronizado
├── .nojekyll                            <- Desactiva Jekyll en GitHub Pages
├── requirements.txt                     <- Dependencias para el bot de scraping
├── README.md                            <- Documentación del proyecto
├── data/
│   ├── competitors_registry.json        <- Directorio de 28 competidores y URLs oficiales
│   ├── entities.json                    <- Dataset estructurado de las 28 entidades
│   ├── competitors_snapshots.json       <- Snapshots de contenido y hashes SHA-256
│   ├── audit_log.json                   <- Historial de eventos de auditoría y caídas
│   └── audit_summary.json               <- Resumen de la última ejecución (online/caídos)
├── scripts/
│   ├── monitor_competitors.py           <- Bot de scraping, detección de cambios y reintentos
│   ├── build_site.py                    <- Compilador que inyecta datos y timestamp en index.html
│   └── deploy_to_github.py              <- Desplegador inicial hacia la API de GitHub
└── .github/
    └── workflows/
        └── fal_competitors_monitor.yml  <- Workflow de GitHub Actions (2x/día + reintentos)
```

---

## ⚖️ Aviso Legal y Cumplimiento Normativo

**ACA VALORES S.A.** — Agente de Liquidación y Compensación Propio (ALyC) registrado bajo el N° 1304 ante la Comisión Nacional de Valores (CNV). Agente de Colocación y Distribución Integral de FCI (ACyDI) N° 173 de la CNV.  
Av. Eduardo Madero 942, Piso 4, Ciudad Autónoma de Buenos Aires, República Argentina.
