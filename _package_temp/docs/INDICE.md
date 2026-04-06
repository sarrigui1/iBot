# 📚 Índice Completo de Documentación

**Bienvenido a iBot Enterprise**. Este índice te ayuda a navegar toda la documentación disponible.

---

## 🎯 ¿Por Dónde Empiezo?

### Si eres un USUARIO final
👉 Lee: **[USUARIO/README.txt](USUARIO/README.txt)**
- Configuración inicial
- Modos de operación
- Safety gates y monitoreo
- Troubleshooting

### Si eres un DESARROLLADOR
👉 Lee: **[IMPLEMENTACION/IMPLEMENTACION_FASE_1_2_3.md](IMPLEMENTACION/IMPLEMENTACION_FASE_1_2_3.md)**
- Estructura del código
- Fases de implementación
- Cómo compilar y distribuir

### Si necesitas ENTENDER la tecnología
👉 Lee: **[TECNICA/DOCUMENTO_TECNICO_IBOT.md](TECNICA/DOCUMENTO_TECNICO_IBOT.md)**
- Arquitectura SMC
- Integración con Claude API
- Flujos de análisis

---

## 📖 Documentación por Categoría

### 👤 Para Usuarios Finales

| Documento | Tema | Audiencia |
|-----------|------|-----------|
| [USUARIO/README.txt](USUARIO/README.txt) | Guía de inicio rápido | Usuarios nuevos |
| USUARIO/PRIMEROS_PASOS.txt* | Pasos después de instalación | Usuarios nuevos |
| USUARIO/TROUBLESHOOTING.txt* | Solución de problemas | Usuarios con dudas |

*Generado automáticamente por el instalador

---

### 🔧 Para Desarrolladores

| Documento | Tema | Descripción |
|-----------|------|-------------|
| [IMPLEMENTACION/IMPLEMENTACION_FASE_1_2_3.md](IMPLEMENTACION/IMPLEMENTACION_FASE_1_2_3.md) | ⭐ Estructura del proyecto | Cómo está organizado el código, qué se actualizó en cada fase |
| [IMPLEMENTACION/DISTRIBUCION_FINAL.md](IMPLEMENTACION/DISTRIBUCION_FINAL.md) | Distribución y licencias | Cómo compilar, distribuir y validar licencias |
| [IMPLEMENTACION/PLAN_COMERCIALIZACION_v1.md](IMPLEMENTACION/PLAN_COMERCIALIZACION_v1.md) | Plan comercial | Pricing, ROI, costos operativos |

---

### 📊 Para Arquitectos / Entendimiento Profundo

| Documento | Tema | Contenido |
|-----------|------|----------|
| [TECNICA/DOCUMENTO_TECNICO_IBOT.md](TECNICA/DOCUMENTO_TECNICO_IBOT.md) | ⭐ Arquitectura general | SMC, Claude API, flujos, diagrama |
| [TECNICA/FLUJO_ANALISIS_IA_DETALLADO.md](TECNICA/FLUJO_ANALISIS_IA_DETALLADO.md) | Análisis de IA paso a paso | Qué datos se envían a Claude, qué respuestas recibe |
| [TECNICA/EJEMPLOS_DATOS_ENVIADOS_A_CLAUDE.md](TECNICA/EJEMPLOS_DATOS_ENVIADOS_A_CLAUDE.md) | Ejemplos reales | Casos de uso, inputs/outputs concretos |
| [TECNICA/DIAGRAMA_FLUJO_VISUAL.txt](TECNICA/DIAGRAMA_FLUJO_VISUAL.txt) | Diagrama ASCII | Representación visual del flujo |

---

## 🗂️ Estructura del Proyecto

```
trading_bot_mt5/
│
├── src/                          ⭐ CÓDIGO PRINCIPAL (actualizar frecuentemente)
│   ├── app.py                    Aplicación Streamlit principal
│   ├── anthropic_service.py      Integración Claude API
│   ├── mt5_service.py            Conexión MetaTrader 5
│   ├── news_service.py           Calendario económico
│   ├── smc_service.py            Análisis Smart Money Concepts
│   ├── indicators_service.py     Indicadores técnicos
│   ├── feedback_service.py       Feedback del bot
│   ├── risk_manager.py           Gestión de riesgo
│   ├── ui_components.py          Componentes Streamlit
│   ├── logger_service.py         Sistema de logging
│   └── i18n.py                   Internacionalización
│
├── core/                         ⚙️ MÓDULOS CRÍTICOS (actualizar raramente)
│   ├── config_loader.py          Lee y valida config.ini
│   └── license_manager.py        Valida licencias contra Google Sheets
│
├── config/                       🔐 CONFIGURACIÓN
│   ├── config.ini                Template para cliente (DISTRIBUIDO)
│   ├── credentials.py            API keys locales (NO distribuir)
│   └── requirements.txt          Dependencias Python (DISTRIBUIDO)
│
├── tools/                        🛠️ HERRAMIENTAS ADMINISTRATIVAS (NO distribuir)
│   ├── generate_licenses.py      Genera license keys
│   ├── build_exe.py              Compila a ejecutable
│   ├── build_exe.spec            Spec para PyInstaller
│   ├── installer.py              Script de instalación automática
│   ├── iBot_Enterprise_Setup.spec Spec para instalador
│   └── test_indicators.py        Tests unitarios
│
├── docs/                         📚 DOCUMENTACIÓN
│   ├── USUARIO/                  Para usuarios finales
│   │   └── README.txt
│   ├── TECNICA/                  Para arquitectos
│   │   ├── DOCUMENTO_TECNICO_IBOT.md
│   │   ├── FLUJO_ANALISIS_IA_DETALLADO.md
│   │   ├── EJEMPLOS_DATOS_ENVIADOS_A_CLAUDE.md
│   │   └── DIAGRAMA_FLUJO_VISUAL.txt
│   ├── IMPLEMENTACION/           Para desarrolladores
│   │   ├── IMPLEMENTACION_FASE_1_2_3.md
│   │   ├── DISTRIBUCION_FINAL.md
│   │   └── PLAN_COMERCIALIZACION_v1.md
│   └── INDICE.md                 ← TÚ ESTÁS AQUÍ
│
├── data/                         📊 DATOS EN RUNTIME (generado por app)
│   ├── license_cache.json        Caché de validación de licencia
│   ├── trading_journal.csv       Registro de trades
│   └── strategy_memory.json      Memoria del bot
│
├── dist/                         📦 DISTRIBUCIÓN (generado por build)
│   └── iBot_Enterprise_Setup.exe Instalador para clientes
│
├── build/                        🔨 BUILD ARTIFACTS (ignorar)
│
├── app_main.py                   🚀 Punto de entrada para Streamlit
├── README_DOCUMENTACION.md       Deprecated - usar INDICE.md
└── .gitignore                    Archivos a ignorar

```

---

## 🎬 Quick Start

### Para Usuarios

```bash
# 1. Descarga e instala
iBot_Enterprise_Setup.exe

# 2. Edita config.ini con tus credenciales MT5

# 3. Inicia la app
launcher.bat

# 4. Abre en navegador
http://localhost:8501
```

### Para Desarrolladores

```bash
# 1. Instala dependencias
pip install -r config/requirements.txt

# 2. Inicia la app
streamlit run app_main.py

# 3. Compila a ejecutable
python tools/build_exe.py

# 4. Crea el instalador
pyinstaller tools/iBot_Enterprise_Setup.spec
```

---

## 🔑 Conceptos Clave

### Fases de Implementación

- **Fase 1**: Restructuración de código con ConfigLoader
- **Fase 2**: Compilación a ejecutable (PyInstaller)
- **Fase 3**: Sistema de licencias (Google Sheets)
- **Fase 4**: Monetización (Stripe + landing page) — Pendiente

### Archivos Críticos a Actualizar

Estos archivos cambian cuando se agrega funcionalidad:
- `src/app.py` — Lógica principal, UI
- `src/smc_service.py` — Análisis técnico
- `src/anthropic_service.py` — Integración Claude
- `core/config_loader.py` — Si se agregan nuevas configs
- `config/config.ini` — Template si hay nuevos parámetros

### Archivos que NO cambian

Estos se actualizan RARAMENTE:
- `core/license_manager.py` — Validación de licencias
- `config/requirements.txt` — Dependencias
- `tools/build_exe.py` — Scripts de compilación

---

## 🚀 Próximos Pasos

### Corto Plazo
1. [ ] Agregar 10 licenses de ejemplo a Google Sheet
2. [ ] Probar instalador en PC limpia
3. [ ] Verificar flujo de usuario (config → launcher → app)

### Mediano Plazo (Fase 4)
1. [ ] Landing page con información de producto
2. [ ] Integración Stripe para pagos
3. [ ] Dashboard de administración de licencias
4. [ ] Sistema de soporte (ticketing)

### Largo Plazo
1. [ ] Actualizaciones automáticas (sin compilar nuevo exe)
2. [ ] Análisis mejorado con modelos más grandes
3. [ ] Soporte para múltiples brokers
4. [ ] API para integradores

---

## 📞 Soporte Rápido

**¿Cómo instalo?**
→ Ver: [USUARIO/README.txt](USUARIO/README.txt)

**¿Cómo compilo a ejecutable?**
→ Ver: [IMPLEMENTACION/DISTRIBUCION_FINAL.md](IMPLEMENTACION/DISTRIBUCION_FINAL.md)

**¿Cómo funciona el sistema de licencias?**
→ Ver: [IMPLEMENTACION/IMPLEMENTACION_FASE_1_2_3.md](IMPLEMENTACION/IMPLEMENTACION_FASE_1_2_3.md) → Sección Fase 3

**¿Cómo funciona el análisis de IA?**
→ Ver: [TECNICA/DOCUMENTO_TECNICO_IBOT.md](TECNICA/DOCUMENTO_TECNICO_IBOT.md)

**¿Qué es SMC?**
→ Ver: [TECNICA/DOCUMENTO_TECNICO_IBOT.md](TECNICA/DOCUMENTO_TECNICO_IBOT.md) → Sección SMC

---

## 🎓 Navegación por Rol

### Soy Usuario
1. Leo: README.txt
2. Descargo: iBot_Enterprise_Setup.exe
3. Ejecuto: installer → config.ini → launcher.bat
4. Si tengo dudas: Consulto README.txt → Troubleshooting

### Soy Desarrollador Junior
1. Leo: IMPLEMENTACION_FASE_1_2_3.md (entender qué hay)
2. Exploro: src/ → entiender estructura
3. Bajo cambio: app.py → Streamlit + Python
4. Pruebo: streamlit run app_main.py
5. Compilo: python tools/build_exe.py

### Soy Arquitecto
1. Leo: DOCUMENTO_TECNICO_IBOT.md (visión general)
2. Leo: FLUJO_ANALISIS_IA_DETALLADO.md (cómo funciona)
3. Exploro: src/smc_service.py → core de análisis
4. Valido: EJEMPLOS_DATOS_ENVIADOS_A_CLAUDE.md → casos reales

### Soy DevOps
1. Leo: DISTRIBUCION_FINAL.md (cómo se distribuye)
2. Estudio: tools/build_exe.py (compilación)
3. Entiendo: tools/installer.py (instalación en cliente)
4. Creo: Pipeline CI/CD para generar releases

---

## 📋 Checklist de Documentación

- [x] README para usuarios (`USUARIO/README.txt`)
- [x] Documento técnico (`TECNICA/DOCUMENTO_TECNICO_IBOT.md`)
- [x] Implementación (`IMPLEMENTACION/IMPLEMENTACION_FASE_1_2_3.md`)
- [x] Distribución (`IMPLEMENTACION/DISTRIBUCION_FINAL.md`)
- [x] Flujos de IA (`TECNICA/FLUJO_ANALISIS_IA_DETALLADO.md`)
- [x] Ejemplos (`TECNICA/EJEMPLOS_DATOS_ENVIADOS_A_CLAUDE.md`)
- [x] Índice de docs (`docs/INDICE.md`)

---

**Última actualización:** 5 de Abril de 2026
**Documentación completa para:** Usuarios, Desarrolladores, Arquitectos, DevOps
