# Plan de Comercialización y Distribución
## iBot · Intelligence Trading — Modelo SaaS/Suscripción

**Fecha:** 03 de Abril de 2026
**Versión:** 1.0 — Plan de Lanzamiento
**Objetivo:** Pasar de software interno → Producto comercial con pago mensual

---

## Tabla de Contenido

1. [Fase 1: Preparación (2-3 semanas)](#fase-1-preparación)
2. [Fase 2: Protección y Ejecutable (3-4 semanas)](#fase-2-protección-y-ejecutable)
3. [Fase 3: Sistema de Licencias (2-3 semanas)](#fase-3-sistema-de-licencias)
4. [Fase 4: Modelo de Precios y Planes](#fase-4-modelo-de-precios)
5. [Fase 5: Onboarding y Soporte](#fase-5-onboarding-y-soporte)
6. [Fase 6: Seguridad y Compliance](#fase-6-seguridad-y-compliance)
7. [Resumen: Timeline y Costos](#resumen-timeline-y-costos)

---

## FASE 1: Preparación (2-3 semanas)

### 1.1 Estructura de Carpetas para Distribución

```
iBot_Enterprise/
├── ibot.exe              ← ejecutable compilado (PyInstaller)
├── config/
│   └── config.ini        ← ÚNICO archivo editable por cliente
├── data/
│   ├── trading_journal.csv
│   ├── trading_decisions.csv
│   ├── strategy_memory.json
│   └── trade_context.csv
├── logs/
│   └── ibot_runtime.log
├── LICENSE.txt           ← licencia y términos
├── README_CLIENTE.txt    ← instrucciones rápidas
└── .env.encrypted        ← credenciales encriptadas (NO tocable)
```

### 1.2 Configuración Permitida (config.ini)

**Solo estos parámetros serán editables por el cliente:**

```ini
[TRADING_PARAMETERS]
# Monedas a operar
SYMBOLS = EURUSD,GBPUSD,USDJPY,XAUUSD,BTCUSD

# Control de riesgo
AUTONOMOUS_CONFIDENCE_THRESHOLD = 0.85
MAX_DAILY_LOSS_PCT = 3.0
MAX_SPREAD_POINTS = 30

[TIMEZONE]
LOCAL_UTC_OFFSET = -5
LOCAL_TZ_NAME = Colombia

[REFRESH_INTERVAL]
DEFAULT_REFRESH_SECONDS = 60
AI_MIN_INTERVAL_MINS = 5

[NEWS_SHIELD]
NEWS_SHIELD_MINUTES = 60
NEWS_CACHE_TTL = 1800

[LANGUAGE]
UI_LANGUAGE = es
# es = Español, en = English

[ACCOUNT]
MT5_LOGIN = [SOLO LECTURA - configurar en primer inicio]
MT5_SERVER = [SOLO LECTURA - configurar en primer inicio]
```

### 1.3 Cambios en Code Base (Seguridad)

#### A. Separar credenciales de configuración

**Antes (config.py):**
```python
LOGIN = int(os.getenv("MT5_LOGIN", 0))
PASSWORD = os.getenv("MT5_PASSWORD", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
```

**Después (crear `credentials.py` — NO DISTRIBUIDA):**
```python
# credentials.py — LOCAL ONLY, .gitignore
import os
from cryptography.fernet import Fernet

class Credentials:
    @staticmethod
    def get_encrypted_key(key_name: str) -> str:
        """Lee credenciales del almacén encriptado del sistema"""
        encrypted = os.getenv(f"IBOT_{key_name}_ENC")
        if not encrypted:
            return ""
        cipher = Fernet(os.getenv("IBOT_CIPHER_KEY"))
        return cipher.decrypt(encrypted.encode()).decode()

    @staticmethod
    def mt5_login() -> int:
        return int(Credentials.get_encrypted_key("MT5_LOGIN"))

    @staticmethod
    def mt5_password() -> str:
        return Credentials.get_encrypted_key("MT5_PASSWORD")

    @staticmethod
    def anthropic_key() -> str:
        return Credentials.get_encrypted_key("ANTHROPIC_KEY")
```

#### B. Crear `config_loader.py`

```python
# config_loader.py — distribuida, lee config.ini
import configparser
from pathlib import Path

class ConfigLoader:
    def __init__(self, config_file: str = "config/config.ini"):
        self.parser = configparser.ConfigParser()
        self.config_path = Path(config_file)

        if not self.config_path.exists():
            self._create_default_config()

        self.parser.read(self.config_path, encoding='utf-8')

    def _create_default_config(self):
        """Genera config.ini por defecto en primer inicio"""
        defaults = {
            'TRADING_PARAMETERS': {
                'SYMBOLS': 'EURUSD,GBPUSD,USDJPY,XAUUSD,BTCUSD',
                'AUTONOMOUS_CONFIDENCE_THRESHOLD': '0.85',
                'MAX_DAILY_LOSS_PCT': '3.0',
            },
            'TIMEZONE': {
                'LOCAL_UTC_OFFSET': '-5',
                'LOCAL_TZ_NAME': 'Colombia',
            }
        }

        for section, options in defaults.items():
            self.parser.add_section(section)
            for key, value in options.items():
                self.parser.set(section, key, value)

        self.config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            self.parser.write(f)

    def get(self, section: str, key: str, fallback=None):
        try:
            return self.parser.get(section, key)
        except:
            return fallback
```

#### C. Modificar `app.py` para usar ConfigLoader

```python
# app.py — top
from config_loader import ConfigLoader

config = ConfigLoader()

SYMBOLS = config.get('TRADING_PARAMETERS', 'SYMBOLS', 'EURUSD,GBPUSD').split(',')
AUTONOMOUS_CONFIDENCE_THRESHOLD = float(
    config.get('TRADING_PARAMETERS', 'AUTONOMOUS_CONFIDENCE_THRESHOLD', '0.85')
)
MAX_DAILY_LOSS_PCT = float(
    config.get('TRADING_PARAMETERS', 'MAX_DAILY_LOSS_PCT', '3.0')
)
LOCAL_TZ_NAME = config.get('TIMEZONE', 'LOCAL_TZ_NAME', 'Colombia')
```

---

## FASE 2: Protección y Ejecutable (3-4 semanas)

### 2.1 Compilar a EXE con PyInstaller

**Paso 1: Crear `build_spec.spec`**

```python
# build_spec.spec
a = Analysis(
    ['app.py'],
    pathex=['C:\\Users\\sergi\\OneDrive\\Escritorio\\trading_bot_mt5'],
    binaries=[],
    datas=[
        ('config/', 'config/'),
        ('LICENSE.txt', '.'),
        ('README_CLIENTE.txt', '.'),
    ],
    hiddenimports=['streamlit', 'MetaTrader5', 'pandas_ta', 'anthropic'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludedimports=['matplotlib', 'pytest'],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='ibot',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,  ← sin ventana de consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico',  ← icono personalizado
)

coll = Collection(exe, a.binaries, a.zipfiles, a.datas,
   strip=False,
   upx=True,
   upx_exclude=[],
   name='ibot_distribution'
)
```

**Paso 2: Compilar**

```bash
# En terminal (Windows)
pip install pyinstaller
pyinstaller build_spec.spec --distpath ./dist --buildpath ./build

# Resultado: dist/ibot/ibot.exe
```

**Paso 3: Crear ZIP distribución**

```bash
# Organizar
mkdir dist/iBot_v1.0_Enterprise
cp -r dist/ibot/* dist/iBot_v1.0_Enterprise/
cp config/config.ini.template dist/iBot_v1.0_Enterprise/config/
cp LICENSE.txt dist/iBot_v1.0_Enterprise/
cp README_CLIENTE.txt dist/iBot_v1.0_Enterprise/

# Empaquetar
cd dist
zip -r iBot_v1.0_Enterprise.zip iBot_v1.0_Enterprise/

# Resultado: iBot_v1.0_Enterprise.zip (~150-200 MB)
```

### 2.2 Obfuscar Código Python

Para proteger la lógica de negocio, obfuscar el código compilado:

```bash
# Opción 1: PyArmor (recomienda)
pip install pyarmor
pyarmor obfuscate --restrict app.py anthropic_service.py smc_service.py

# Resultado: código ilegible en bytecode, pero sigue funcionando igual
```

### 2.3 Firma Digital del EXE

Para que Windows confíe en el ejecutable (sin "Unknown Publisher"):

```bash
# Necesitas certificado SSL (o crear self-signed)
# Usar Signtool (Windows SDK)
signtool sign /f certificate.pfx /p password /t http://timestamp.server ibot.exe

# Resultado: exe firmado, Windows no muestra warning
```

---

## FASE 3: Sistema de Licencias (2-3 semanas)

### 3.1 Arquitectura de Validación de Licencia

```
CLIENTE DESCARGA iBot.exe
         │
         ▼
PRIMER INICIO
         │
         ├─ Pide: email + license key
         │
         ▼
VALIDA CONTRA SERVIDOR (request HTTP)
         │
    ┌────┴────┐
   SÍ         NO
    │          │
    ▼          ▼
 VÁLIDA     INVÁLIDA
    │          │
    ├─ Guardar  └─ Mostrar error
    │  license       "Contacta soporte"
    │  (encriptada)
    │
    ├─ Descargar setup MT5
    │  (si primera vez)
    │
    └─ OPERAR (con validación monthly)
```

### 3.2 Backend de Validación (Node.js + Express)

**Crear API simple en servidor:**

```javascript
// license-api.js — Node.js
const express = require('express');
const stripe = require('stripe')(process.env.STRIPE_SECRET_KEY);
const app = express();

app.post('/api/validate-license', async (req, res) => {
  const { email, license_key, version } = req.body;

  try {
    // 1. Validar contra DB de clientes
    const customer = await db.customers.findOne({ email });
    if (!customer) return res.status(404).json({ valid: false, error: "Cliente no encontrado" });

    // 2. Validar license key
    if (customer.license_key !== hashKey(license_key)) {
      return res.status(401).json({ valid: false, error: "Clave inválida" });
    }

    // 3. Validar suscripción activa en Stripe
    const subscription = await stripe.subscriptions.retrieve(customer.stripe_subscription_id);
    const is_active = subscription.status === 'active';

    if (!is_active) {
      return res.json({
        valid: false,
        error: "Suscripción expirada",
        renewal_url: `https://billing.ibotapp.com/renew?email=${email}`
      });
    }

    // 4. OK — devolver token de sesión
    const session_token = generateToken(email, 30); // válido 30 días

    return res.json({
      valid: true,
      session_token,
      expires_in_days: 30,
      features: customer.plan.features,
    });

  } catch (err) {
    return res.status(500).json({ valid: false, error: "Error del servidor" });
  }
});

app.listen(3000);
```

### 3.3 Cliente Python: License Manager

```python
# license_manager.py
import requests
import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

class LicenseManager:
    API_URL = "https://api.ibotapp.com"
    LICENSE_FILE = Path("~/.ibot/license.json").expanduser()

    @staticmethod
    def first_time_setup():
        """Ejecuta en primer inicio"""
        print("╔═══════════════════════════════════════╗")
        print("║ iBot · Intelligence Trading v1.0       ║")
        print("║ Configuración Inicial                  ║")
        print("╚═══════════════════════════════════════╝")

        email = input("📧 Email de la cuenta: ").strip()
        license_key = input("🔑 Clave de licencia: ").strip()

        # Validar contra servidor
        valid, response = LicenseManager.validate(email, license_key)

        if not valid:
            print(f"❌ {response.get('error', 'Error desconocido')}")
            if "renewal_url" in response:
                print(f"Renueva tu suscripción: {response['renewal_url']}")
            return False

        # Guardar licencia encriptada
        LicenseManager.save_license(email, license_key, response['session_token'])
        print(f"✅ Licencia activada para {email}")
        print(f"⏰ Válida hasta: {response.get('expires_date')}")
        return True

    @staticmethod
    def validate(email: str, license_key: str) -> tuple:
        """Valida contra API"""
        try:
            resp = requests.post(
                f"{LicenseManager.API_URL}/validate-license",
                json={
                    "email": email,
                    "license_key": license_key,
                    "version": "1.0",
                },
                timeout=10,
            )
            data = resp.json()

            if data.get('valid'):
                return True, data
            else:
                return False, data
        except Exception as e:
            return False, {"error": f"Error conexión: {str(e)}"}

    @staticmethod
    def save_license(email: str, license_key: str, session_token: str):
        """Guarda licencia encriptada localmente"""
        LicenseManager.LICENSE_FILE.parent.mkdir(parents=True, exist_ok=True)

        license_data = {
            "email": email,
            "license_key_hash": hashlib.sha256(license_key.encode()).hexdigest(),
            "session_token": session_token,
            "created": datetime.now().isoformat(),
        }

        with open(LicenseManager.LICENSE_FILE, 'w') as f:
            json.dump(license_data, f)

        os.chmod(LicenseManager.LICENSE_FILE, 0o600)  # solo lectura

    @staticmethod
    def check_license() -> bool:
        """Verifica en cada inicio si licencia sigue válida"""
        if not LicenseManager.LICENSE_FILE.exists():
            return LicenseManager.first_time_setup()

        with open(LicenseManager.LICENSE_FILE) as f:
            license_data = json.load(f)

        # Validar contra servidor (cada 7 días, o diario si es demo)
        email = license_data['email']
        license_key = license_data['license_key_hash']

        valid, response = LicenseManager.validate(email, license_key)

        if not valid:
            print("⚠️ Licencia expirada o inválida")
            print(response.get('error'))
            return False

        return True
```

### 3.4 Integración en `app.py`

```python
# app.py — líneas iniciales
from license_manager import LicenseManager
import sys

# VALIDAR LICENCIA ANTES DE CARGAR STREAMLIT
if not LicenseManager.check_license():
    sys.exit(1)  # cerrar si no hay licencia válida

# Después de esto, cargar Streamlit normalmente
import streamlit as st
```

---

## FASE 4: Modelo de Precios

### 4.1 Estructura de Planes

```
╔════════════════════════════════════════════════════════════════╗
║             PLANES DE SUSCRIPCIÓN MENSUAL                      ║
╚════════════════════════════════════════════════════════════════╝

PLAN BÁSICO — $99 USD/mes
├─ 1 usuario
├─ 5 instrumentos (EURUSD, GBPUSD, USDJPY, XAUUSD, BTCUSD)
├─ Análisis ilimitado
├─ Dashboard en tiempo real
├─ Soporte por email (48h respuesta)
├─ Actualizaciones automáticas
└─ Histórico de operaciones (últimos 6 meses)

PLAN PROFESIONAL — $299 USD/mes ⭐ RECOMENDADO
├─ 2 usuarios simultáneos
├─ 10 instrumentos (agregar más pares)
├─ Análisis avanzado (backtesting básico)
├─ Alertas por Telegram/WhatsApp
├─ Soporte por email + chat (4h respuesta)
├─ Actualizaciones automáticas
├─ Histórico ilimitado
├─ API para integración externa
└─ Customización de parámetros SMC

PLAN ENTERPRISE — $999 USD/mes + setup $500
├─ Usuarios ilimitados
├─ Instrumentos ilimitados
├─ Backtesting completo
├─ Alertas multi-canal
├─ Soporte 24/7 (phone + email + chat)
├─ Actualizaciones priority
├─ Histórico ilimitado
├─ API completa
├─ Customización total
├─ Reportes automáticos
├─ Hosting dedicado (opcional +$200/mes)
└─ SLA 99.9% uptime

PLAN TRIAL — GRATIS, 14 días
├─ Acceso total Plan Profesional
├─ Sin tarjeta de crédito requerida
├─ Automático a Basic si no upgradea
└─ Cancelable en cualquier momento
```

### 4.2 Modelo de Pago (Stripe)

**Implementar suscripciones en Stripe Dashboard:**

```
Producto 1: iBot Basic
  Price: $99/mes
  Billing: Monthly

Producto 2: iBot Professional
  Price: $299/mes
  Billing: Monthly

Producto 3: iBot Enterprise
  Price: $999/mes + $500 setup
  Billing: Monthly
```

**API para crear cliente:**

```javascript
// Crear cliente en Stripe
const customer = await stripe.customers.create({
  email: email,
  name: company_name,
  metadata: { plan: 'professional' }
});

// Crear suscripción
const subscription = await stripe.subscriptions.create({
  customer: customer.id,
  items: [{ price: 'price_professional_monthly' }],
});

// Guardar en DB
db.customers.insert({
  email,
  company_name,
  stripe_customer_id: customer.id,
  stripe_subscription_id: subscription.id,
  plan: 'professional',
  license_key: generateLicenseKey(),
  created_at: new Date(),
});
```

### 4.3 Flujo de Compra

```
CLIENTE VISITA: https://ibotapp.com/pricing

ELIGE PLAN → CLICK "COMPRAR AHORA"
       │
       ▼
STRIPE CHECKOUT (email, tarjeta, etc.)
       │
       ▼
PAGO EXITOSO
       │
       ├─ Email confirmación
       ├─ Link descarga iBot.exe
       ├─ License Key generada
       ├─ Acceso al dashboard de billing
       └─ Crear cuenta en plataforma
       │
       ▼
CLIENTE DESCARGA iBot.exe
       │
       ▼
PRIMER INICIO
  - Email: [el que usó en compra]
  - License Key: [recibido en email]
       │
       ▼
LICENCIA VALIDADA
       │
       ▼
✅ OPERAR (con renovación automática cada mes)
```

---

## FASE 5: Onboarding y Soporte

### 5.1 Dashboard Web para Clientes

**URL:** `https://dashboard.ibotapp.com`

```
PANEL DEL CLIENTE
├─ Suscripción
│  ├─ Plan actual (Basic/Professional/Enterprise)
│  ├─ Fecha renovación
│  ├─ Historial de pagos
│  └─ Botón: Upgrade/Downgrade
│
├─ Licencias
│  ├─ License Key (copiar al clipboard)
│  ├─ Dispositivos autorizados
│  └─ Revocar acceso desde otros dispositivos
│
├─ Análisis
│  ├─ Total operaciones (mes/año/all-time)
│  ├─ Win rate
│  ├─ Profit total
│  ├─ Best trade / Worst trade
│  └─ Exportar CSV/PDF
│
├─ Soporte
│  ├─ Tickets abiertos
│  ├─ Base de conocimiento (FAQ)
│  ├─ Crear nuevo ticket
│  └─ Chat en vivo (si plan Professional+)
│
└─ Ajustes
   ├─ Email notificaciones
   ├─ Cambiar contraseña
   ├─ Información de perfil
   └─ Dos factores (2FA)
```

### 5.2 Centro de Ayuda (Selfservice)

**URL:** `https://help.ibotapp.com`

```
DOCUMENTACIÓN PÚBLICA
├─ Getting Started
│  ├─ Instalación paso a paso
│  ├─ Configuración MT5
│  ├─ Primeras operaciones
│  └─ FAQ básicas
│
├─ Guías
│  ├─ SMC Framework explicado
│  ├─ Safety Gates y riesgos
│  ├─ Ajustar parámetros
│  ├─ Interpretar señales IA
│  └─ Troubleshooting común
│
├─ Vídeos (YouTube)
│  ├─ Instalación (3 min)
│  ├─ Tutorial completo (15 min)
│  ├─ Best practices (10 min)
│  └─ Q&A sesiones (30 min, mensual)
│
└─ API Documentation (para Plan Enterprise)
   ├─ Autenticación
   ├─ Endpoints disponibles
   ├─ Ejemplos de integración
   └─ Rate limits
```

### 5.3 Sistema de Soporte

```
TICKETS (Zendesk, Intercom, etc.)
├─ Plan Basic: respuesta 48h
├─ Plan Professional: respuesta 4h
└─ Plan Enterprise: respuesta 1h + chat 24/7

CANALES SOPORTE
├─ Email: support@ibotapp.com
├─ Chat en vivo: (Professional+ only)
├─ Telegram Bot: @ibotapp_support (notificaciones)
└─ WhatsApp: +1-555-0123 (Enterprise only)
```

---

## FASE 6: Seguridad y Compliance

### 6.1 Protecciones de Seguridad

```
NIVEL 1: CLIENTE
├─ HTTPS para todo (no HTTP)
├─ Credenciales MT5 encriptadas (AES-256)
├─ API keys no se guardan en disco (solo en memoria)
├─ Validación de licencia local + remota
└─ Auto-logout después de 30 min inactividad

NIVEL 2: TRANSMISIÓN
├─ TLS 1.3 para todas las conexiones
├─ Pinning de certificados
├─ Rate limiting (10 requests/segundo por IP)
├─ CORS restringido a dominio propio
└─ User-Agent validation

NIVEL 3: SERVIDOR
├─ WAF (Web Application Firewall)
├─ DDoS protection (Cloudflare, etc.)
├─ Logs encriptados
├─ Backups diarios + snapshots
├─ Monitoreo 24/7
└─ Incident response plan
```

### 6.2 Cumplimiento Legal

```
DOCUMENTOS REQUERIDOS
├─ Terms of Service (TOS)
│  ├─ Disclaimer de riesgo (IMPORTANTE)
│  ├─ No es asesoría financiera
│  ├─ Responsabilidad limitada
│  └─ Indemnización
│
├─ Privacy Policy
│  ├─ Qué datos recolectamos
│  ├─ Cómo los usamos
│  ├─ GDPR compliance
│  ├─ CCPA compliance
│  └─ Data retention
│
├─ Risk Disclosure
│  ├─ Trading es riesgoso
│  ├─ Posibilidad de pérdida total
│  ├─ Limitaciones del sistema
│  ├─ Backtesting ≠ desempeño futuro
│  └─ Botones de pánico (qué hace)
│
└─ AML/KYC (Anti-Money Laundering)
   ├─ Verificación de identidad
   ├─ Límites de deposito iniciales
   ├─ Monitoreo de transacciones sospechosas
   └─ Compliance officer
```

### 6.3 Warnings y Disclaimers

**En la aplicación:**

```
🚨 IMPORTANTE:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Trading en mercados de divisas y criptomonedas conlleva
RIESGO SIGNIFICATIVO DE PÉRDIDA FINANCIERA.

Este software NO es asesoría financiera. Es una herramienta
de ANÁLISIS TÉCNICO asistida por IA. Las decisiones finales
son RESPONSABILIDAD DEL USUARIO.

• Posibilidad de pérdida total de capital
• Volatilidad impredecible
• Errores técnicos
• Desconexiones del broker

SIEMPRE usa:
✓ Stop Loss en cada operación
✓ Gestión de riesgo (máx 1-2% por trade)
✓ Supervisión humana
✓ Demo account ANTES de real

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[ ] Entiendo y acepto los riesgos
[ Continuar ]
```

---

## Resumen: Timeline y Costos

### Timeline de Implementación

```
FASE 1: PREPARACIÓN (2-3 semanas)
├─ Separar código / credenciales
├─ Crear config.ini template
└─ Documentación para clientes

FASE 2: PROTECCIÓN (3-4 semanas)
├─ PyInstaller setup
├─ Obfuscar código
├─ Firma digital
└─ Testing en máquinas limpias

FASE 3: LICENCIAS (2-3 semanas)
├─ API validación
├─ License Manager
├─ Integración app
└─ Testing de flujos

FASE 4: PAGOS (1-2 semanas)
├─ Integración Stripe
├─ Dashboard web básico
├─ Emails automáticos
└─ Testing de pagos

FASE 5: SOPORTE (2-3 semanas)
├─ Documentación
├─ Vídeos tutoriales
├─ Sistema de tickets
└─ FAQ base

FASE 6: SEGURIDAD (1-2 semanas)
├─ Audit de código
├─ Penetration testing
├─ Legal review
└─ Documentos compliance

════════════════════════════════════════════════════════
TOTAL: 12-18 SEMANAS (3-4 meses) HASTA LANZAMIENTO
════════════════════════════════════════════════════════
```

### Costos de Implementación

| Concepto | Costo | Notas |
|----------|-------|-------|
| **Desarrollo** | $0 | Ya existe código |
| **Infraestructura** | | |
| — Servidor API (AWS/Heroku) | $200/mes | License validation |
| — Base datos (AWS RDS) | $100/mes | Clientes + transacciones |
| — Dominio + SSL | $150/año | ibotapp.com, renewals |
| — CDN (Cloudflare) | $50/mes | DDoS, SSL, performance |
| **Servicios 3ros** | | |
| — Stripe (payment processor) | 2.9% + $0.30/trans | Automático |
| — Zendesk (ticketing) | $49/mes | Soporte hasta 50 clientes |
| — Sentry (error tracking) | $29/mes | Monitoreo |
| — SendGrid (email) | $30/mes | Transaccional + marketing |
| **Legal** | | |
| — Abogado (TOS + Privacy) | $1,500 | Una sola vez |
| — Compliance audit | $2,000 | Inicial |
| **Marketing** | | |
| — Website | $200 | Dominio + hosting |
| — Vídeos (contratar editor) | $500 | 5 vídeos tutoriales |
| **TOTAL MENSUAL** | **~$700** | Después de lanzamiento |
| **TOTAL INICIAL** | **~$4,000** | Setup + legal |

### Proyección de Ingresos (Modelo Base)

```
Escenario: 20 clientes en Mes 1

MES 1: 20 clientes
├─ 15 clientes @ $99/mes (Basic)      = $1,485
├─ 4 clientes @ $299/mes (Professional) = $1,196
├─ 1 cliente @ $999/mes (Enterprise)   = $999
├─ Setup fees (Enterprise)              = $500
│
INGRESOS BRUTOS MES 1: $4,180
MENOS Stripe fees (3%)  = -$125
MENOS costo operación   = -$700
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
UTILIDAD MES 1:         = $3,355

────────────────────────────────────

MES 6 (crecimiento 10% mensual):
├─ 32 clientes Basic    = $3,168
├─ 8 clientes Professional = $2,392
├─ 2 clientes Enterprise = $1,998
│
INGRESOS BRUTOS: $7,558
MENOS gastos:   -$700
┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄
UTILIDAD:       $6,858

────────────────────────────────────

PAYBACK PERIOD: ~1 mes (recupera $4k inicial)
MARGIN: 85% (después de costos variables)
```

---

## Proceso de Distribución

### Descargas

```
Opción 1: Self-Service en Web
https://ibotapp.com/download
├─ Elige plan
├─ Completa compra
├─ Descarga .zip automática
└─ Link válido 48h (seguridad)

Opción 2: Distribución Directa
├─ Vendedor envía link
├─ Cliente activa licencia
└─ Descarga activada
```

### Actualizaciones

```
MODELO: Auto-update con opt-in

Sistema detecta:
  Versión nueva disponible
       │
       ▼
  Notifica al usuario
       │
       ▼
  "Descargar actualización"
  └─ Descarga en background
  └─ Instala en reinicio
  └─ Preserva config.ini + datos

NUNCA: fuerza actualización
       (cliente controla cuándo actualizar)
```

---

## Checklist Pre-Lanzamiento

```
☐ Ejecutable compilado y testeado
☐ Código obfuscado
☐ EXE firmado digitalmente
☐ License manager integrado
☐ API de validación funcionando
☐ Stripe configurado
☐ Dashboard web operativo
☐ Documentación completa
☐ Vídeos tutoriales listos
☐ TOS, Privacy Policy, Disclaimers legales
☐ Penetration testing completado
☐ Soporte setup (tickets, email)
☐ Monitoreo 24/7 (Sentry, etc.)
☐ Backups configurados
☐ Email transaccional automático
☐ Landing page en sitio web
☐ Presupuesto marketing definido
☐ Documentos AML/KYC preparados
```

---

## Comunicación al Cliente

**Email de bienvenida:**

```
Asunto: ¡Bienvenido a iBot · Intelligence Trading! 🚀

Hola [Nombre],

¡Gracias por suscribirte a iBot Professional!

PRÓXIMOS PASOS:

1. Descarga e instala:
   Enlace: [descarga-directa]

2. Configuración inicial (3 minutos):
   • Email: [el-que-usaste-para-compra]
   • License Key: IBPRO-2026-XXXXX (en el archivo adjunto)

3. Conecta tu cuenta MT5:
   • Tutorial: [enlace-video]

4. Primeras operaciones:
   • Guía rápida: [enlace-docs]

RECURSOS:
📖 Documentación: https://help.ibotapp.com
🎬 Vídeos: https://youtube.com/@ibotapp
💬 Soporte: support@ibotapp.com (respuesta 4h)

AVISO IMPORTANTE:
⚠️ Trading es riesgoso. Siempre usa Stop Loss.
⚠️ Este software NO es asesoría financiera.
⚠️ Demo account ANTES de dinero real.

¿Preguntas? Contacta soporte.

¡A operar! 🎯
```

---

*Plan de comercialización preparado por equipo iBot*
*Versión 1.0 — Abril 2026*
*Flexible y adaptable según feedback de mercado*
