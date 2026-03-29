# 🚀 GUÍA RÁPIDA DE DESPLIEGUE (KALI LINUX)
> **Sigue este orden exacto de comandos para ejecutar el sistema.**

---

### 1️⃣ CLONACIÓN Y SISTEMA
```bash
git clone [https://github.com/zarateaz/Domotica.git](https://github.com/zarateaz/Domotica.git)
cd Domotica
sudo apt update && sudo apt install python3-venv python3-opencv -y
2️⃣ ENTORNO VIRTUAL Y LIBRERÍAS
Bash
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install opencv-python numpy
3️⃣ CÓMO EJECUTAR EL SISTEMA (DEMO)
Paso A: Registrar un nuevo rostro

Bash
./venv/bin/python registrar.py
Paso B: Iniciar el Reconocimiento (Main)

Bash
./venv/bin/python main.py
📂 REQUISITOS PARA QUE FUNCIONE:
Tener conectada la Webcam (si usas VM, actívala en el menú Dispositivos).

No borrar el archivo master.key (es la llave de seguridad).

La carpeta venv debe estar creada para que corra el comando ./venv/bin/python.
