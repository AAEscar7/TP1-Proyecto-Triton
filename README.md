# Proyecto Tritón 🔱

**Sistema de Telemetría Multicloud y Observabilidad Asíncrona**

Aplicación CLI que consulta simultáneamente múltiples proveedores cloud (AWS, Azure, GCP) utilizando programación asíncrona con Python 3.11+, capturando y analizando telemetría en tiempo real.

---

## 📋 Descripción

Tritón es un monitor de telemetría que:

- Consulta proveedores cloud de forma **asíncrona y concurrente**
- Captura métricas y datos de observabilidad en **tiempo real**
- Proporciona manejo robusto de errores con **ExceptionGroups**
- Registra eventos en **JSON estructurado** de forma no bloqueante
- Simula fallos de red controlados en **modo caos** para pruebas de resiliencia

---

## 🏗️ Arquitectura

### Componentes Principales

```
src/
├── app_operator.py              # CLI y orquestación principal
└── triton_telemetry/
    ├── core.py                  # Lógica asíncrona de consultas
    ├── exceptions.py            # Excepciones personalizadas
    ├── logging_engine.py        # Pipeline de logging JSON
    └── sanitizer.py             # Validación de argumentos
```

### Flujo de Datos

1. **CLI Parser** → Valida argumentos del usuario
2. **Async Task Group** → Lanza consultas concurrentes a proveedores
3. **HTTP Client (httpx)** → Obtiene datos de endpoints
4. **Exception Handling** → Captura y reporta errores específicos
5. **Structured Logging** → Registra eventos en JSON

---

## 🚀 Características

### Consultas Asíncronas
- Manejo concurrente de múltiples proveedores cloud
- Operaciones no bloqueantes con `asyncio.TaskGroup`
- Timeout configurable por consulta

### Manejo de Errores Granular
- **ProviderTimeoutError**: Proveedor no respondió a tiempo
- **NetworkPeeringError**: Fallo de conectividad de red
- **CorruptedPayloadError**: Respuesta malformada o código HTTP erróneo

### Logging Estructurado
- Formato JSON con timestamps ISO 8601
- Serialización de excepciones anidadas (ExceptionGroups)
- Rotación automática con compresión gzip
- Acceso no bloqueante con `QueueListener`

### Validación de Entrada
- Cluster ID con patrón stricto: `cluster-[region]-[0-9]+`
- Timeout entre 0.1 y 10.0 segundos
- Modos operativos: nominal, debug, emergency

### Modo Caos
- Simula fallos controlados en proveedores
- Prueba la resiliencia del sistema ante errores
- Útil para validar manejo de excepciones

---

## 📦 Dependencias

- **httpx** ≥ 0.27.0 — Cliente HTTP asíncrono con soporte concurrente
- **Python** ≥ 3.11 — Para TaskGroup y ExceptionGroup

---

## 🛠️ Instalación

```bash
# Clonar repositorio
git clone https://github.com/AAEscar7/TP1-Proyecto-Triton.git
cd TP1-Proyecto-Triton

# Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## 🎯 Uso

### Consultar proveedores específicos
```bash
python -m src.app_operator AWS Azure --cluster-id cluster-us-east-1-1 --timeout 2.5
```

### Modo caos (simular fallos)
```bash
python -m src.app_operator GCP --cluster-id cluster-eu-west-1-2 --chaos
```

### Especificar modo operativo
```bash
python -m src.app_operator AWS Azure GCP \
    --cluster-id cluster-ap-south-1-3 \
    --timeout 5.0 \
    --mode debug
```

### Ver ayuda
```bash
python -m src.app_operator --help
```

---

## 📊 Ejemplo de Salida

```
============================================================
INICIANDO MONITOR DE TELEMETRÍA TRITÓN
Clúster Target: cluster-us-east-1-1
Modo de Operación: nominal
Proveedores Seleccionados: AWS, Azure, GCP
Timeout Configurado: 2.5 s
============================================================
EVALUACIÓN DE TELEMETRÍA COMPLETADA CON ÉXITO
Métricas [AWS]: {"userId": 1, "id": 1, "title": "...", "body": "..."}
Métricas [Azure]: {"userId": 1, "id": 2, "title": "...", "body": "..."}
Métricas [GCP]: {"userId": 1, "id": 3, "title": "...", "body": "..."}
============================================================
FINALIZANDO CICLO DE MONITOREO Y APAGANDO PIPELINE NO BLOQUEANTE
============================================================
```

---

## 📂 Estructura de Archivos

| Archivo | Propósito |
|---------|-----------|
| `src/app_operator.py` | Punto de entrada CLI y orquestación |
| `src/triton_telemetry/core.py` | Lógica asíncrona de consultas HTTP |
| `src/triton_telemetry/exceptions.py` | Excepciones personalizadas de Tritón |
| `src/triton_telemetry/logging_engine.py` | Pipeline de logging estructurado en JSON |
| `src/triton_telemetry/sanitizer.py` | Validadores de argumentos CLI |
| `triton_services.log` | Archivo de log generado (rotado y comprimido) |

---

## 🔧 Lógica Clave

### Consulta Asíncrona (`core.py`)
1. Selecciona endpoint según modo (normal/caos)
2. Realiza petición HTTP con timeout
3. Valida código HTTP y formato JSON
4. Captura excepciones específicas con context

### Orquestación (`app_operator.py`)
1. Parsea argumentos CLI
2. Crea tareas concurrentes para cada proveedor
3. Captura `ExceptionGroup` para manejo granular
4. Reporta errores detallados con forensics

### Logging (`logging_engine.py`)
- Formatea registros como JSON estructurado
- Serializa árboles de excepciones completos
- Usa `QueueListener` para acceso no bloqueante
- Rota logs automáticamente con compresión gzip

---

## 🧪 Testing

Prueba con modo caos para simular fallos:

```bash
python -m src.app_operator AWS Azure GCP --cluster-id cluster-test-1 --chaos
```

Esto desencadenará:
- Timeouts simulados (3s delay)
- Errores HTTP 504
- Payloads XML malformados

---

## 📝 Notas

- Los datos de telemetría se obtienen de `jsonplaceholder.typicode.com` para demostración
- El modo caos utiliza `httpbin.org` para inyectar fallos controlados
- Los logs se guardan en formato JSON en `triton_services.log`
- Se requiere Python 3.11+ para TaskGroup y ExceptionGroup

---

## 👤 Autor

### Grupo 7

```
Programación Para Automatización II - UPATECO - 2026
└── Grupo 7
    ├── Diego Cerrano                 # Integrante 1
    ├── Alejandro Escariz             # Integrante 1
    ├── Ignacio Aleman                # Integrante 1
    ├── Maria Belen Ferreyra          # Integrante 1
    ├── Enrique Marroquin             # Integrante 1
    └── Leonel Isasmendi              # Integrante 1
``` 

---
