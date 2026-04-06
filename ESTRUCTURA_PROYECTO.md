# 📂 Estructura del Proyecto iBot Enterprise

**Guía para entender cómo está organizado el proyecto y qué archivos actualizar/distribuir.**

---

## 🎯 Resumen Ejecutivo

| Categoría | Directorio | Propósito | ¿Distribuir? | ¿Actualizar? |
|-----------|-----------|----------|--------------|--------------|
| **Código Principal** | `src/` | Lógica de la app | ✅ Sí | ✅ Frecuente |
| **Módulos Críticos** | `core/` | Config + Licencias | ✅ Sí | ⚠️ Raramente |
| **Configuración** | `config/` | Templates de config | Parcial* | Según cambios |
| **Herramientas Admin** | `tools/` | Build, generador, tests | ❌ No | Por mantenimiento |
| **Documentación** | `docs/` | Guías y referencias | ✅ Sí (usuario) | Según cambios |
| **Datos Runtime** | `data/` | Caché, journal, logs | ❌ No | Auto-generado |
| **Build Artifacts** | `dist/`, `build/` | Ejecutables compilados | ✅ Sí (dist) | Auto-generado |

*`config.ini` sí, `credentials.py` no

---

## 📂 Estructura Detallada

### `src/` — CÓDIGO PRINCIPAL ⭐

Contiene toda la lógica de la aplicación. **Este es el código que se actualiza frecuentemente.**

```
src/
├── app.py                      Aplicación Streamlit principal
│                               ├─ Carga config.ini
│                               ├─ Valida licencia
│                               ├─ Inicializa servicios
│                               └─ Renderiza UI
│
├── anthropic_service.py        Integración Claude Haiku API
│                               ├─ Análisis de velas
│                               ├─ Recomendaciones de trade
│                               └─ Validación de setup
│
├── mt5_service.py              Conexión MetaTrader 5
│                               ├─ Conexión a cuenta
│                               ├─ Lectura de datos
│                               ├─ Ejecución de órdenes
│                               └─ Cierre de posiciones
│
├── news_service.py             Calendario económico
│                               ├─ Fetching de eventos
│                               ├─ News shield (protección)
│                               └─ Sentimiento de mercado
│
├── smc_service.py              Smart Money Concepts ⭐
│                               ├─ Detección de Order Blocks
│                               ├─ Fair Value Gaps
│                               ├─ Break of Structure
│                               └─ Visualización en gráficos
│
├── indicators_service.py       Indicadores técnicos
│                               ├─ ATR, RSI, MACD
│                               ├─ Bandas de Bollinger
│                               └─ Cálculos de volatilidad
│
├── feedback_service.py         Feedback y calibración
│                               ├─ Calidad de setup
│                               ├─ Mejora continua
│                               └─ Historial de feedback
│
├── risk_manager.py             Gestión de riesgo
│                               ├─ Cálculo de position size
│                               ├─ Validación de stops
│                               └─ Límites de pérdida diaria
│
├── ui_components.py            Componentes Streamlit
│                               ├─ Renderizado de gráficos
│                               ├─ Tablas y métricas
│                               └─ Widgets de control
│
├── logger_service.py           Sistema de logging
│                               ├─ Logs a archivo
│                               ├─ Rotación de archivos
│                               └─ Niveles de error
│
├── i18n.py                     Internacionalización
│                               ├─ Traducciones ES/EN
│                               ├─ Soporte multi-idioma
│                               └─ Términos de trading
│
└── __init__.py                 Marca directorio como paquete
```

**¿Cuándo actualizar `src/`?**
- Cuando agregues features nuevas
- Cuando corrijas bugs
- Cuando optimices rendimiento
- Cuando cambies la UI

---

### `core/` — MÓDULOS CRÍTICOS ⚙️

Módulos que **rara vez cambian** pero son críticos para la operación.

```
core/
├── config_loader.py            Lee y valida config.ini ⭐
│                               ├─ Busca config.ini en config/
│                               ├─ Valida todas las secciones
│                               ├─ Convierte tipos (str→int, list)
│                               └─ Lanza errores claros si falta algo
│
├── license_manager.py          Validación de licencias ⭐
│                               ├─ Descarga CSV de Google Sheets
│                               ├─ Valida licencia activa
│                               ├─ Comprueba fecha de expiración
│                               ├─ Guarda caché local (7 días)
│                               └─ Offline fallback
│
└── __init__.py                 Marca directorio como paquete
```

**¿Cuándo actualizar `core/`?**
- Raramente (en fase de desarrollo solo)
- Si cambias el formato de config.ini → actualiza config_loader.py
- Si cambias Google Sheets → actualiza license_manager.py
- Si cambias sistema de licencias → actualiza license_manager.py

**NO actualizar core/ sin razón fuerte** (evita romper la validación de licencias).

---

### `config/` — CONFIGURACIÓN 🔐

```
config/
├── config.ini                  Template de configuración ✅ DISTRIBUIR
│                               ├─ [LICENSE]
│                               ├─ [MT5_ACCOUNT]
│                               ├─ [TRADING_PARAMETERS]
│                               ├─ [TIMEZONE]
│                               ├─ [REFRESH_TIMING]
│                               └─ [NEWS_CONFIG]
│
├── credentials.py              API keys locales ❌ NO DISTRIBUIR
│                               ├─ ANTHROPIC_API_KEY
│                               └─ FINNHUB_API_KEY
│
└── requirements.txt            Dependencias Python ✅ DISTRIBUIR
                                ├─ streamlit
                                ├─ MetaTrader5
                                ├─ anthropic
                                ├─ gspread
                                ├─ pandas
                                └─ etc.
```

**¿Qué distribuir?**
- ✅ `config.ini` — Cliente lo edita con sus valores
- ✅ `requirements.txt` — Script de install necesita esto
- ❌ `credentials.py` — Información sensible de desarrollo

---

### `tools/` — HERRAMIENTAS ADMINISTRATIVAS 🛠️

**No se distribuyen a clientes.** Solo para administración interna.

```
tools/
├── generate_licenses.py        Genera license keys
│                               ├─ Formato: IBOT-YYYY-NNN
│                               ├─ Salida: tab-separated para Google Sheets
│                               ├─ Uso: python tools/generate_licenses.py 10
│                               └─ Admin solo
│
├── build_exe.py                Compila a ejecutable Windows
│                               ├─ Ejecuta pyinstaller
│                               ├─ Organiza estructura dist/
│                               ├─ Copia config.ini, data/
│                               └─ Genera iBot_Enterprise/ folder
│
├── build_exe.spec              Spec para PyInstaller
│                               ├─ Define qué incluir en exe
│                               ├─ Especifica hidden imports
│                               └─ Configura output
│
├── installer.py                Script de instalación automática
│                               ├─ Verifica Python
│                               ├─ Instala dependencias
│                               ├─ Crea shortcuts
│                               ├─ Genera PRIMEROS_PASOS.txt
│                               └─ Log: instalacion.log
│
├── iBot_Enterprise_Setup.spec   Spec para compilar installer
│                               ├─ Empaqueta installer.py
│                               ├─ Genera iBot_Enterprise_Setup.exe
│                               └─ Tamaño: ~6.9 MB
│
└── test_indicators.py          Tests unitarios
                                ├─ Verifica indicadores
                                └─ Validación de cálculos
```

**¿Cuándo usar `tools/`?**
- `generate_licenses.py` — Antes de vender a nuevo cliente
- `build_exe.py` — Cuando compilas release nuevo
- `installer.py` — Para mantenerlo/mejorar instalación
- `test_indicators.py` — Cuando cambies indicadores

---

### `docs/` — DOCUMENTACIÓN 📚

```
docs/
├── INDICE.md                   Índice maestro ← EMPIEZA AQUÍ
│
├── USUARIO/
│   └── README.txt              Guía de usuario final ✅ DISTRIBUIR
│                               ├─ Requisitos previos
│                               ├─ Configuración inicial
│                               ├─ Ejecución
│                               ├─ Troubleshooting
│                               └─ Disclaimer
│
├── TECNICA/
│   ├── DOCUMENTO_TECNICO_IBOT.md
│   │                           ├─ Arquitectura general
│   │                           ├─ SMC explicado
│   │                           ├─ Claude API integration
│   │                           └─ Flujo completo
│   │
│   ├── FLUJO_ANALISIS_IA_DETALLADO.md
│   │                           ├─ Qué datos se envían a Claude
│   │                           ├─ Qué Claude responde
│   │                           └─ Paso a paso del análisis
│   │
│   ├── EJEMPLOS_DATOS_ENVIADOS_A_CLAUDE.md
│   │                           ├─ Casos de uso reales
│   │                           ├─ JSON de entrada/salida
│   │                           └─ Ejemplos concretos
│   │
│   └── DIAGRAMA_FLUJO_VISUAL.txt
│                               └─ Diagrama ASCII del flujo
│
└── IMPLEMENTACION/
    ├── IMPLEMENTACION_FASE_1_2_3.md
    │                           ├─ Estructura de Fases
    │                           ├─ Archivos modificados
    │                           ├─ Flujo de ejecución
    │                           └─ Tests de verificación
    │
    ├── DISTRIBUCION_FINAL.md
    │                           ├─ Cómo distribuir
    │                           ├─ Opciones (installer vs exe)
    │                           ├─ Sistema de licencias
    │                           └─ ROI y pricing
    │
    └── PLAN_COMERCIALIZACION_v1.md
                                ├─ Análisis de mercado
                                ├─ Modelo de precios
                                ├─ Costos operativos
                                └─ Proyecciones
```

**¿Qué distribuir?**
- ✅ `docs/USUARIO/README.txt` — Cliente debe leer esto
- ❌ `docs/TECNICA/*` — Internal only (pero disponible para partner devs)
- ❌ `docs/IMPLEMENTACION/*` — Internal only

---

### `data/` — DATOS EN RUNTIME 📊

**Generado automáticamente por la aplicación.** No editar manualmente.

```
data/
├── license_cache.json          Caché de validación de licencia
│                               ├─ Generado en runtime
│                               ├─ TTL: 7 días
│                               ├─ No distribuir
│                               └─ Se crea automáticamente
│
├── trading_journal.csv         Registro de todos los trades
│                               ├─ Generado en runtime
│                               ├─ Append-only
│                               ├─ Cliente lo descarga
│                               └─ Historial completo
│
└── strategy_memory.json        Memoria del bot
                                ├─ Feedback del bot
                                ├─ Calibración
                                ├─ Notas por sesión
                                └─ Generado en runtime
```

---

### `dist/` — DISTRIBUCIÓN 📦

**Generado automáticamente por scripts de build.** No editar.

```
dist/
└── iBot_Enterprise_Setup.exe    Instalador para clientes ✅ DISTRIBUIR
                                ├─ Tamaño: 6.9 MB
                                ├─ Standalone (no requiere Python)
                                ├─ Instalación automática
                                └─ Generado por:
                                   pyinstaller iBot_Enterprise_Setup.spec
```

---

### `build/` — BUILD ARTIFACTS 🔨

**Auto-generado.** Ignorar/eliminar sin problemas.

```
build/
└── (artifacts intermedios de PyInstaller)
```

---

## 🎯 Matriz: Qué Actualizar vs Qué No

### ✅ ACTUALIZAR FRECUENTEMENTE

| Archivo | Cuándo | Por Qué |
|---------|--------|--------|
| `src/app.py` | Nueva feature o bug fix | Lógica principal |
| `src/smc_service.py` | Mejora análisis SMC | Mejora la detección |
| `src/anthropic_service.py` | Cambio en Claude prompts | Mejora respuestas IA |
| `config/config.ini` | Nuevo parámetro | Cliente lo edita |
| `docs/USUARIO/README.txt` | Cambio en UI o flujo | Usuario necesita documentación |

### ⚠️ ACTUALIZAR RARAMENTE

| Archivo | Cuándo | Por Qué |
|---------|--------|--------|
| `core/config_loader.py` | Nuevo campo en config | Soporte para nueva config |
| `core/license_manager.py` | Cambio Google Sheets | Cambio en sistema de licencias |
| `config/requirements.txt` | Nueva dependencia | Nueva librería necesaria |

### ❌ NO ACTUALIZAR (excepto fixes críticos)

| Archivo | Por Qué |
|---------|--------|
| `tools/build_exe.py` | Es un script de build |
| `tools/generate_licenses.py` | Es herramienta admin |
| `tools/installer.py` | Script de instalación |
| `config/credentials.py` | Información sensible |
| `.gitignore` | Rara vez cambia |

---

## 🚀 Flujos de Trabajo

### Agregar Nueva Feature

```
1. Editar src/app.py o src/smc_service.py
2. Probar: streamlit run app_main.py
3. Commit y push
4. (Opcional) Compilar: python tools/build_exe.py
5. (Opcional) Distribuir: dist/iBot_Enterprise_Setup.exe
```

### Compilar Release Nuevo

```
1. Asegurar que src/ está finalizado y testeado
2. Actualizar config/requirements.txt si hay nuevas deps
3. Ejecutar: python tools/build_exe.py
4. Resultado: dist/iBot_Enterprise/ (exe)
5. Compilar installer: pyinstaller tools/iBot_Enterprise_Setup.spec
6. Resultado: dist/iBot_Enterprise_Setup.exe
```

### Agregar Nueva Configuración

```
1. Editar config/config.ini (template)
2. Editar core/config_loader.py (validación)
3. Usar config en src/*.py (lógica)
4. Actualizar docs/USUARIO/README.txt
5. Documentar en docs/TECNICA/
```

### Vender Nueva Licencia

```
1. python tools/generate_licenses.py 5
2. Copiar output a Google Sheet (celda A2)
3. Enviar IBOT-2026-NNN a cliente
4. Cliente edita config.ini
5. Cliente ejecuta iBot_Enterprise_Setup.exe
```

---

## 📋 Resumen para Diferentes Roles

### 👨‍💻 Desarrollador

**Carpetas que tocas:**
- `src/` — aquí pasas ~90% del tiempo
- `docs/` — actualizar si cambias features

**Carpetas que NO tocas:**
- `tools/` — solo si necesitas mejorar build
- `core/` — muy raramente
- `config/` — solo template

**Comando para desarrollar:**
```bash
streamlit run app_main.py
```

### 🔨 DevOps / Release Manager

**Carpetas importantes:**
- `tools/` — scripts de build aquí
- `config/requirements.txt` — dependencias
- `dist/` — outputs

**Comandos clave:**
```bash
python tools/build_exe.py
pyinstaller tools/iBot_Enterprise_Setup.spec
```

### 📊 Product Manager

**Carpetas importantes:**
- `docs/USUARIO/` — guía para clientes
- `docs/IMPLEMENTACION/` — plan comercial
- `config/config.ini` — parámetros

**Qué revisar:**
- README.txt antes de distribuir
- Cambios en config.ini antes de release

### 🏢 Ejecutivo

**Lo que importa:**
- `ESTRUCTURA_PROYECTO.md` ← estás aquí
- `docs/IMPLEMENTACION/PLAN_COMERCIALIZACION_v1.md`
- `docs/IMPLEMENTACION/DISTRIBUCION_FINAL.md`

---

## 🔒 Seguridad: Qué NO Distribuir

| Archivo | Razón | Acción |
|---------|-------|--------|
| `config/credentials.py` | API keys sensibles | .gitignore ✅ |
| `.env` | Variables de entorno | .gitignore ✅ |
| `build/`, `dist/` (intermedios) | Build artifacts | .gitignore ✅ |
| `__pycache__/` | Cache Python | .gitignore ✅ |
| `.git/` | Historial Git | Solo repo |

---

## 📦 Distribución Final

**Para clientes:**
```
iBot_Enterprise_Setup.exe (6.9 MB)
  ↓ Cliente ejecuta
  ↓ Instalación automática
  ↓ Crea: config/, launcher.bat, shortcuts
  ↓ Cliente edita: config/config.ini
  ↓ Cliente ejecuta: launcher.bat
  ✅ App inicia
```

---

## 🎓 Ejemplo: Agregar Nueva Configuración

Supongamos que quieres agregar `TELEGRAM_WEBHOOK` para notificaciones.

### Paso 1: Actualizar Template

**`config/config.ini`**
```ini
[NOTIFICATIONS]
TELEGRAM_WEBHOOK = https://api.telegram.org/...
```

### Paso 2: Actualizar Validador

**`core/config_loader.py`**
```python
required_sections = {
    ...
    "NOTIFICATIONS": ["TELEGRAM_WEBHOOK"],
}
```

### Paso 3: Usar en Código

**`src/app.py`**
```python
config = ConfigLoader()
telegram_url = config.telegram_webhook
```

### Paso 4: Documentar

**`docs/USUARIO/README.txt`**
```
[NOTIFICATIONS]
TELEGRAM_WEBHOOK = tu_webhook_aqui (opcional)
```

### Paso 5: Compilar

```bash
python tools/build_exe.py
pyinstaller tools/iBot_Enterprise_Setup.spec
```

---

## ✅ Checklist Antes de Distribuir

- [ ] src/ compilado y testeado
- [ ] config/config.ini actualizado
- [ ] docs/USUARIO/README.txt actualizado
- [ ] requirements.txt tiene todas las deps
- [ ] credentials.py está en .gitignore
- [ ] dist/iBot_Enterprise_Setup.exe generado
- [ ] Prueba con licencia de test
- [ ] Prueba offline (sin internet)
- [ ] Verificar: installer crea shortcuts ✅
- [ ] Verificar: config.ini se edita fácil ✅

---

**Última actualización:** 5 de Abril de 2026
**Mantenedor:** Claude Haiku 4.5
