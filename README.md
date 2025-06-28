# ModelSwap 🔄

[English](#english) | [Español](#español)

---

## English

### 🚀 Overview

**ModelSwap** is a modern, web-based 3D model converter that allows you to convert between different 3D file formats with ease. Built with Python Flask and Trimesh, it provides a beautiful, responsive interface with real-time progress tracking and support for multiple file formats.

### ✨ Features

- **🔄 Multi-Format Conversion**: Convert between OBJ, STL, PLY, COLLADA (.dae), glTF (.gltf), GLB (.glb), and OFF formats
- **📁 Drag & Drop**: Upload files by dragging them anywhere on the page
- **📊 Real-Time Progress**: Individual progress bars for each file with live status updates
- **🎨 Modern UI**: Beautiful, responsive design with light/dark mode support
- **🌍 Bilingual**: Full English and Spanish language support
- **⚡ Fast Processing**: Optimized conversion engine with Trimesh
- **🔒 Privacy-First**: All processing happens locally, files are automatically deleted after conversion
- **📱 Mobile-Friendly**: Responsive design that works on all devices
- **🎯 Smart Limits**: Maximum 10 files per session, 100MB per file
- **🛡️ Rate Limiting**: Built-in protection against abuse

### 🛠️ Supported Formats

| Format | Extension | Description |
|--------|-----------|-------------|
| OBJ | .obj | Wavefront Object - Most widely supported |
| STL | .stl | Stereolithography - 3D printing standard |
| PLY | .ply | Stanford Polygon - Point cloud support |
| COLLADA | .dae | 3D Asset Exchange - Industry standard |
| glTF | .gltf | Web 3D Standard - Modern web format |
| GLB | .glb | Binary glTF - Compact web format |
| OFF | .off | Object File Format - Simple geometry |

### 🚀 Quick Start

#### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

#### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/FLucena/model-swap.git
   cd model-swap
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open your browser**
   Navigate to `http://localhost:5000`

### 📖 Usage

1. **Upload Files**: Drag and drop your 3D model files anywhere on the page, or click to browse
2. **Select Format**: Choose your desired output format from the dropdown
3. **Convert**: Click "Convert Files" to start the conversion process
4. **Monitor Progress**: Watch real-time progress bars for each file
5. **Download**: Click the download link when conversion is complete
6. **Clean Up**: Use "Clean Up Files" to remove temporary files

### ⌨️ Keyboard Shortcuts

- **Ctrl/Cmd + Enter**: Start conversion
- **Escape**: Clear file selection or go back to upload
- **T**: Toggle theme (light/dark)
- **L**: Toggle language (English/Spanish)
- **F**: Open FAQ section
- **Arrow Keys**: Navigate format carousel

### 🏗️ Architecture

- **Backend**: Python Flask with Trimesh for 3D processing
- **Frontend**: Vanilla JavaScript with modern CSS
- **File Processing**: Individual file uploads with progress tracking
- **Security**: Rate limiting and file size validation
- **Storage**: Temporary local storage with automatic cleanup

### 🔧 Configuration

The application can be configured through environment variables or by modifying `app.py`:

- `MAX_CONTENT_LENGTH`: Maximum request size (default: 1GB)
- `MAX_FILES_PER_REQUEST`: Maximum files per upload (default: 10)
- Rate limiting: 10 uploads per minute, 50 per hour, 200 per day

### 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

### 🙏 Acknowledgments

- **Trimesh**: 3D mesh processing library
- **Flask**: Web framework
- **FL Automatons**: Development team

---

## Español

### 🚀 Descripción General

**ModelSwap** es un convertidor de modelos 3D moderno y basado en web que te permite convertir entre diferentes formatos de archivos 3D con facilidad. Construido con Python Flask y Trimesh, proporciona una interfaz hermosa y responsiva con seguimiento de progreso en tiempo real y soporte para múltiples formatos de archivo.

### ✨ Características

- **🔄 Conversión Multi-Formato**: Convierte entre formatos OBJ, STL, PLY, COLLADA (.dae), glTF (.gltf), GLB (.glb) y OFF
- **📁 Arrastrar y Soltar**: Sube archivos arrastrándolos a cualquier parte de la página, o haz clic para explorar
- **📊 Progreso en Tiempo Real**: Barras de progreso individuales para cada archivo con actualizaciones de estado en vivo
- **🎨 UI Moderna**: Diseño hermoso y responsivo con soporte para modo claro/oscuro
- **🌍 Bilingüe**: Soporte completo en inglés y español
- **⚡ Procesamiento Rápido**: Motor de conversión optimizado con Trimesh
- **🔒 Privacidad Primero**: Todo el procesamiento ocurre localmente, los archivos se eliminan automáticamente después de la conversión
- **📱 Compatible con Móviles**: Diseño responsivo que funciona en todos los dispositivos
- **🎯 Límites Inteligentes**: Máximo 10 archivos por sesión, 100MB por archivo
- **🛡️ Limitación de Tasa**: Protección integrada contra abuso

### 🛠️ Formatos Soportados

| Formato | Extensión | Descripción |
|---------|-----------|-------------|
| OBJ | .obj | Objeto Wavefront - Más ampliamente soportado |
| STL | .stl | Estereolitografía - Estándar de impresión 3D |
| PLY | .ply | Polígono Stanford - Soporte para nube de puntos |
| COLLADA | .dae | Intercambio de Activos 3D - Estándar de la industria |
| glTF | .gltf | Estándar Web 3D - Formato web moderno |
| GLB | .glb | glTF Binario - Formato web compacto |
| OFF | .off | Formato de Archivo Objeto - Geometría simple |

### 🚀 Inicio Rápido

#### Prerrequisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

#### Instalación

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/FLucena/model-swap.git
   cd model-swap
   ```

2. **Crear un entorno virtual**
   ```bash
   python -m venv venv
   ```

3. **Activar el entorno virtual**
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

4. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

5. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

6. **Abrir tu navegador**
   Navega a `http://localhost:5000`

### 📖 Uso

1. **Subir Archivos**: Arrastra y suelta tus archivos de modelo 3D en cualquier parte de la página, o haz clic para explorar
2. **Seleccionar Formato**: Elige tu formato de salida deseado del menú desplegable
3. **Convertir**: Haz clic en "Convertir Archivos" para iniciar el proceso de conversión
4. **Monitorear Progreso**: Observa las barras de progreso en tiempo real para cada archivo
5. **Descargar**: Haz clic en el enlace de descarga cuando la conversión esté completa
6. **Limpiar**: Usa "Limpiar Archivos" para eliminar archivos temporales

### ⌨️ Atajos de Teclado

- **Ctrl/Cmd + Enter**: Iniciar conversión
- **Escape**: Limpiar selección de archivos o volver a subir
- **T**: Cambiar tema (claro/oscuro)
- **L**: Cambiar idioma (Inglés/Español)
- **F**: Abrir sección FAQ
- **Teclas de Flecha**: Navegar carrusel de formatos

### 🏗️ Arquitectura

- **Backend**: Python Flask con Trimesh para procesamiento 3D
- **Frontend**: JavaScript vanilla con CSS moderno
- **Procesamiento de Archivos**: Subidas individuales con seguimiento de progreso
- **Seguridad**: Limitación de tasa y validación de tamaño de archivo
- **Almacenamiento**: Almacenamiento local temporal con limpieza automática

### 🔧 Configuración

La aplicación se puede configurar a través de variables de entorno o modificando `app.py`:

- `MAX_CONTENT_LENGTH`: Tamaño máximo de solicitud (predeterminado: 1GB)
- `MAX_FILES_PER_REQUEST`: Archivos máximos por subida (predeterminado: 10)
- Limitación de tasa: 10 subidas por minuto, 50 por hora, 200 por día

### 🤝 Contribuir

1. Haz fork del repositorio
2. Crea una rama de características (`git checkout -b feature/caracteristica-increible`)
3. Haz commit de tus cambios (`git commit -m 'Agregar característica increíble'`)
4. Haz push a la rama (`git push origin feature/caracteristica-increible`)
5. Abre un Pull Request

### 📄 Licencia

Este proyecto está licenciado bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

### 🙏 Agradecimientos

- **Trimesh**: Biblioteca de procesamiento de mallas 3D
- **Flask**: Framework web
- **FL Automatons**: Equipo de desarrollo

---

## 📞 Contact

**FL Automatons**  
🌐 [Portfolio](https://flucena.vercel.app/)  
🐙 [GitHub](https://github.com/FLucena)  
💼 [LinkedIn](https://www.linkedin.com/in/franciscoivanlucena/)  
✉️ [Email](mailto:franciscolucena90@gmail.com)

---

<div align="center">
  <p>Built by <a href="https://flucena.vercel.app/">FL Automatons</a></p>
  <p>Construido por <a href="https://flucena.vercel.app/">FL Automatons</a></p>
</div> 