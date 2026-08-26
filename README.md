# TP1 - Proyecto Triton

## Programación para Automatización II

**Alumnos:**
 - Alejandro Escariz
 - 
 - 
 -  
**Proyecto:** TP-1 - Sistema de Telemetría Multicloud y Observabilidad Asíncrona  
**Nombre del sistema:** Proyecto Tritón  
**Modalidad:** Grupal  
**Año:** 2026  

---

## 1. Descripción del proyecto

Proyecto Tritón es un sistema desarrollado en Python para simular la recolección de telemetría desde distintos proveedores de infraestructura cloud.

El sistema trabaja con tres proveedores: AWS, zure y GCP

La aplicación permite además simular condiciones de falla para verificar el comportamiento del sistema ante problemas de red, timeouts, respuestas HTTP inesperadas y payloads inválidos.


---

## 2. Arquitectura


```text
TP1-Proyecto-Triton/
│
├── src/
│   ├── app_operator.py
│   │
│   └── triton_telemetry/
│       ├── __init__.py
│       ├── core.py
│       ├── exceptions.py
│       ├── logging_engine.py
│       └── sanitizer.py
│
├── requirements.txt
├── README.md
├── triton_services.log
```

### Responsabilidad de cada módulo

**app_operator.py**  
Es el punto de entrada de la aplicación. Procesa los argumentos ingresados por consola, ejecuta el escaneo, controla las modalidades de salida y gestiona los distintos grupos de excepciones.

**core.py**  
Contiene la lógica principal para consultar los proveedores y ejecutar las tareas concurrentemente mediante `asyncio`.

**exceptions.py**  
Define las excepciones personalizadas utilizadas por Proyecto Tritón para clasificar los distintos tipos de fallas.

**sanitizer.py**  
Valida y sanitiza los parámetros ingresados por el usuario, como el timeout y el identificador del clúster.

**logging_engine.py**  
Implementa el sistema de logging estructurado, escritura no bloqueante, rotación de archivos y compresión de logs históricos.

---

## 3. Diagrama de arquitectura

---

## 4. Instalación


### Instalar las dependencias

```bash
pip install -r requirements.txt
```

---

## 5. Ejecución

Posicionarse en la raiz del proyecto.

### Ayuda de la interfaz CLI

```bash
python src/app_operator.py --help
```

---

### Escenario nominal

```bash
python src/app_operator.py AWS Azure GCP -c cluster-us-east-01 -t 3.0
```

Este escenario realiza el escaneo concurrente de los tres proveedores con un timeout normal de 3 segundos

Una ejecución correcta informa:

```text
ESCANEO COMPLETADO SIN ANOMALÍAS
```

y presenta el estado, latencia y Payload ID correspondiente a cada proveedor.

---
