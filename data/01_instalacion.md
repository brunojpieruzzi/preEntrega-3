# Manual de Nimbus CLI: Instalación y primeros pasos

Nimbus es una plataforma ficticia de despliegue de aplicaciones usada en este repositorio como dataset de ejemplo. Su herramienta de línea de comandos se llama `nimbus` y permite crear proyectos, desplegarlos y consultar su estado.

## Requisitos del sistema

Nimbus CLI versión 3.2 requiere Python 3.10 o superior y al menos 512 MB de memoria RAM libre. Es compatible con Windows 10 u 11, macOS 12 o superior y las distribuciones Linux con glibc 2.31 o más reciente. En Windows se recomienda usar PowerShell 7. El espacio en disco necesario es de 200 MB para la instalación base y 1 GB adicional si se habilita la caché local de imágenes.

## Instalación

La forma oficial de instalar la herramienta es mediante pip:

```
pip install nimbus-cli==3.2.0
```

Para verificar la instalación se ejecuta `nimbus --version`, que debe imprimir `nimbus 3.2.0`. Si el comando no es reconocido, hay que comprobar que el directorio de scripts de Python esté incluido en la variable de entorno PATH. En entornos de integración continua se aconseja instalar la versión fijada para evitar cambios inesperados entre ejecuciones.

También existe una imagen de Docker llamada `nimbus/cli:3.2`, útil para pipelines que no tienen Python instalado. La imagen pesa aproximadamente 140 MB y ya incluye todos los plugins oficiales.

## Inicializar un proyecto

Para crear un proyecto nuevo se usa el comando `nimbus init nombre-del-proyecto`. Este comando genera una carpeta con la siguiente estructura:

- `nimbus.yaml`: archivo principal de configuración del proyecto.
- `src/`: carpeta donde vive el código de la aplicación.
- `.nimbusignore`: lista de archivos que no deben subirse al desplegar.

El archivo `nimbus.yaml` define el nombre de la aplicación, la región de despliegue y el comando de arranque. La región por defecto es `sa-east-1` (São Paulo). Otras regiones disponibles son `us-east-1`, `eu-west-1` y `ap-south-1`. Cambiar la región después del primer despliegue obliga a recrear la aplicación y provoca una interrupción de entre 2 y 5 minutos.

## Primer despliegue

Una vez configurado el proyecto, el despliegue se lanza con `nimbus deploy`. El proceso tiene tres fases: empaquetado, subida y activación. En un proyecto pequeño de menos de 50 MB el despliegue completo tarda en promedio 40 segundos. Si el despliegue falla en la fase de activación, Nimbus revierte automáticamente a la versión anterior, siempre que exista una.

Para ver el estado de la aplicación se usa `nimbus status`, que muestra la versión activa, el número de instancias en ejecución y el último código de salud. Los códigos de salud posibles son `OK`, `DEGRADED` y `DOWN`.

## Variables de entorno de la aplicación

Las variables de entorno de la aplicación desplegada se gestionan con `nimbus env set CLAVE=valor`. Los valores se almacenan cifrados con AES-256 y nunca se muestran completos en los registros. Para listar las variables definidas se usa `nimbus env list`, que oculta todos los valores salvo los primeros cuatro caracteres. El máximo de variables por aplicación es de 100, y cada valor puede tener hasta 4 KB.

## Desinstalación

Para desinstalar la herramienta se ejecuta `pip uninstall nimbus-cli`. Esto no elimina las aplicaciones ya desplegadas ni los datos de la cuenta; solo elimina el cliente local. Para borrar una aplicación de forma definitiva hay que ejecutar `nimbus destroy nombre-de-la-app` y confirmar escribiendo el nombre completo de la aplicación.
