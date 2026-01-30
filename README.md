# 🔒 Simulador de Bloqueo Justo de Archivos (Fair RWLock)

Este proyecto es una herramienta educativa diseñada para visualizar y comprender el problema de **lectores y escritores** en sistemas operativos y programación concurrente. Utiliza una implementación de **Bloqueo Justo (Fair Read-Write Lock)** para garantizar que ni los lectores ni los escritores sufran de inanición (*starvation*).

## 📋 Resumen de Elaboración

El programa está desarrollado en **Python**, utilizando la biblioteca gráfica **Tkinter** para la interfaz y el módulo **threading** para la gestión de procesos simultáneos. Se diseñó bajo un esquema de programación orientada a objetos (POO), separando la lógica de sincronización de bajo nivel de la representación visual.

## 🚀 Características Principales

* **Gestión de Concurrencia Real:** Simula el acceso a un archivo físico (`archivo_critico.txt`).
* **Fair Lock Logic:** Implementa una cola de espera donde los escritores tienen prioridad ante nuevos lectores para evitar bloqueos infinitos.
* **Visualización en Tiempo Real:** Un Canvas dinámico muestra qué hilos están dentro de la sección crítica.
* **Consola de Eventos:** Registro detallado con marcas de tiempo y colores para distinguir roles (Lectores vs. Escritores).

---

## 🏗️ Estructura del Programa

El código se divide en cuatro bloques fundamentales:

### 1. Lógica de Bloqueo (`FairRWLock`)

Es el motor de sincronización. Utiliza `threading.Condition` para gestionar:

* **Lectura Compartida:** Múltiples lectores pueden entrar si no hay escritores escribiendo ni esperando.
* **Escritura Exclusiva:** Solo un escritor a la vez, bloqueando cualquier otro acceso.
* **Justicia (Fairness):** Si un escritor solicita acceso, los nuevos lectores deben esperar hasta que el escritor termine.

### 2. Interfaz Gráfica (`AppConcurrencia`)

Maneja la ventana principal de simulación, incluyendo:

* **Canvas:** Representación visual del "archivo" donde aparecen y desaparecen los hilos.
* **Control de Logs:** Una zona de texto con scroll que reporta cada acción del sistema.
* **Botones de Acción:** Permiten generar hilos de lectura o escritura de forma aleatoria y asíncrona.
* **Gráfica de Actividad:** Monitorización mediante una gráfica de líneas que registra la carga de hilos activos.

### 3. Pantalla de Inicio (`StartScreen`)

Una interfaz de bienvenida profesional que permite:

* Navegar hacia la simulación.
* Acceder a un menú de ayuda rápida.
* Enlazar a documentación o soporte externo.

### 4. Ciclo de Vida del Hilo

Cada hilo (lector o escritor) sigue este ciclo:

1. **Solicitud:** Intenta adquirir el bloqueo.
2. **Entrada:** Se dibuja en el Canvas y registra su entrada.
3. **Operación:** Lee o escribe en el archivo físico.
4. **Salida:** Libera el bloqueo y se elimina visualmente.

---

## 🛠️ Instalación y Uso

**Opción A)**
1. **Requisitos:** Tener instalado Python 3.x.
2. **Ejecución:**
```bash
python ProcessLock.py
```
**Opción B)**
1. **Abrir el archivo ejecutable (.exe)**
```bash
TrafficController.exe
```


3. **Interacción:**
* Haz clic en **"Iniciar"** en la pantalla de bienvenida.
* Usa **"Añadir Lector"** para ver accesos simultáneos (Azul).
* Usa **"Añadir Escritor"** para ver accesos exclusivos (Rojo).



---

## 📊 Especificaciones Técnicas

| Componente | Tecnología |
| --- | --- |
| Lenguaje | Python 3.x |
| GUI | Tkinter |
| Concurrencia | Threading (Threads, Locks, Conditions) |
| Almacenamiento | Archivo de texto plano (.txt) |

> **Nota:** El archivo `archivo_critico.txt` se limpia automáticamente cada vez que se inicia la aplicación para mantener la simulación fresca.
