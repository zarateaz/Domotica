# 🛡️ ZARATE OS | SISTEMA DE DOMÓTICA BIOMÉTRICA
> **Carrera:** Ingeniería en Ciberseguridad - V Semestre
> **Institución:** SENATI Huancayo (Pilcomayo)
> **Desarrollador:** Ángel Filadelfio Zárate Granados (@zarateaz)
> **Target OS:** Kali Linux / Arch Linux / Debian

Este proyecto es una solución de seguridad perimetral basada en **Reconocimiento Facial (Computer Vision)** y **Criptografía Simétrica**, diseñada para entornos de domótica avanzada.

---

## 🛠️ ARQUITECTURA DEL SISTEMA

El sistema se divide en tres capas principales:
1.  **Capa de Adquisición:** Captura de frames mediante OpenCV.
2.  **Capa de Procesamiento:** Extracción de características biométricas.
3.  **Capa de Persistencia:** Almacenamiento cifrado en `database.json` protegido por `master.key`.

---

## 📋 GUÍA DE INSTALACIÓN PASO A PASO (KALI LINUX)

Para que el proyecto funcione en Kali sin conflictos de paquetes "externally-managed", sigue estos comandos exactos:

### 1. Preparación del Sistema Operativo
Actualiza los repositorios e instala las dependencias de visión artificial:
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3-venv python3-opencv libopencv-dev build-essential -y
2. Clonación y Aislamiento (VENV)Bash# Clonar repositorio
git clone [https://github.com/zarateaz/Domotica.git](https://github.com/zarateaz/Domotica.git)
cd Domotica

# Crear entorno virtual para evitar romper el Python de Kali
python3 -m venv venv

# Activar el entorno virtual
source venv/bin/activate
3. Instalación de Librerías de PythonCon el (venv) activo en tu terminal, instala los módulos necesarios:Bashpip install --upgrade pip
pip install opencv-python numpy
🚀 GUÍA DE USO Y EJECUCIÓNEl sistema requiere dos fases: Registro y Monitoreo.Fase A: Registro de Nuevos UsuariosPara dar de alta a un estudiante o usuario en la base de datos:Bash./venv/bin/python registrar.py
Instrucción: Sigue las indicaciones en pantalla para capturar el rostro.Fase B: Inicio del Reconocimiento (Main)Para activar la vigilancia y el control de acceso:Bash./venv/bin/python main.py
📂 DICCIONARIO DE ARCHIVOSArchivo/CarpetaDescripciónmain.pyScript principal de reconocimiento y lógica de acceso.registrar.pyMódulo de enrolamiento biométrico.database.jsonBase de datos donde se cruzan los IDs de rostros.master.keyCRÍTICO: Llave AES/Fernet para cifrar los registros./rostrosAlmacena los templates procesados (entrenamiento)./logsHistorial detallado de accesos (Fecha, Hora, Usuario).__pycache__Archivos de compilación de Python (no editar).
