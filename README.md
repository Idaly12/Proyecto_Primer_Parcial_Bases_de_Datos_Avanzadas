# Proyecto Blog de Recetas

Una aplicación inspirada en un blog de recetas, desarrollada en Python con una interfaz gráfica creada con CustomTkinter y conectada a una base de datos Oracle SQL, para la materia Bases de Datos Avanzadas.

---

##  Integrantes

**Castillo Castillo Joel Omar**
**Morales Robredo Idaly Guadalupe**
**Sandoval Granados Paloma Ivonne**


---
## Características Principales


* **Autenticación de Usuarios:** Sistema de inicio de sesión y registro.
* **Visualización de Articulos:** Pantalla principal que muestra los ultimos articulos (recetas) publicadas por los usuarios.
* **Panel de Categorías:** Panel lateral que permite filtrar las recetas por categorías.
* **Artiulos:** Contenido completo de la receta.
* **Sistema de Comentarios:** Comentarios realizados por usuarios en cada articulo.
* **Publicación de Recetas:** Los usuarios pueden subir sus propios articulos (recetas) a través de un formulario integrado.
* **Perfiles de Usuario:** Es posible ver el perfil de un autor y todas las recetas que ha publicado.

---

## Tecnologías Utilizadas

* **Lenguaje:** Python
* **Interfaz Gráfica (GUI):** CustomTkinter
* **Base de Datos:** Oracle Database
* **Driver de Oracle:** `oracledb`
* **Manejo de Imágenes:** Pillow

---

## Requisitos Previos

Antes de ejecutar el proyecto, tener instalado lo siguiente:

* **Python 3.8** o superior.
* Una instancia de **Oracle Database** (por ejemplo, Oracle Database Express Edition "XE").
* El **Oracle Instant Client**, necesario para que la librería `oracledb` se conecte correctamente.

---

## Instalación y Configuración


1.  **Clonar el Repositorio**.
    ```bash
    git clone <URL_DEL_REPOSITORIO>
    cd <NOMBRE_CARPETA_PROYECTO>
    ```

2.  **Instalar las Dependencias de Python**
    Abre una terminal en el CMD y ejecutar:
    ```bash
    pip install customtkinter oracledb pillow
    ```

3.  **Configurar la Conexión a la Base de Datos**
    * En el archivo `ConexionBDD.py`.
    * Modifica las siguientes variables con tus credenciales de Oracle:
    ```python
    DB_USER = "tu_usuario_oracle"
    DB_PASS = "tu_contraseña"
    DB_DSN = "localhost/XEPDB1" # o el DSN que corresponda a tu instancia
    ```

4.  **Crear el Esquema de la Base de Datos**
    * Ejecuta los scripts SQL de tu proyecto en tu instancia de Oracle. Esto creará las tablas necesarias (`users`, `articles`, `comments`, `categories`, etc.) y los procedimientos almacenados (`add_user`, `add_article`, `add_comment`, etc.).

5.  **Verificar la Carpeta de Imágenes**
    * La carpeta `Imagenes` se debe encontrar en el mismo directorio que los archivos `.py` y que contenga los archivos `adorno.png` y `fondo.png`.

---

## Cómo Ejecutar la Aplicación

Una vez que todo esté configurado, ejecutar el archivo `app.py`:

```bash
python app.py
