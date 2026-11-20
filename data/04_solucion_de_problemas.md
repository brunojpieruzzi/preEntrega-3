# Manual de Nimbus: Solución de problemas

Esta guía reúne los errores más frecuentes al usar Nimbus y los pasos recomendados para resolverlos.

## Cómo obtener diagnósticos

Antes de contactar con soporte, conviene ejecutar `nimbus doctor`. Este comando revisa la versión instalada, la conectividad con la API, la validez del token y la sintaxis de `nimbus.yaml`, y muestra un resumen con marcas de aprobado o fallo. Con la opción `--report` genera un archivo `nimbus-report.zip` que se puede adjuntar al ticket de soporte; el archivo nunca incluye los valores de las variables de entorno ni los tokens.

Los registros de la aplicación se consultan con `nimbus logs --follow`, que muestra las líneas en tiempo real. Con `--since 1h` se limita a la última hora y con `--level error` solo se muestran los errores.

## Errores de despliegue

### Error NMB-101: paquete demasiado grande

Aparece cuando el paquete supera los 500 MB. La causa habitual es incluir carpetas como `node_modules`, `.venv` o conjuntos de datos pesados. La solución es añadirlas al archivo `.nimbusignore` y volver a desplegar. Se puede inspeccionar el contenido del paquete sin subirlo usando `nimbus deploy --dry-run`.

### Error NMB-204: fallo de activación

Significa que la aplicación se subió correctamente pero no superó la comprobación de salud en los 90 segundos posteriores al arranque. Las causas más comunes son que la aplicación no escucha en el puerto indicado por la variable `PORT` o que falta alguna variable de entorno obligatoria. Nimbus revierte automáticamente a la versión anterior. Para depurar, hay que revisar `nimbus logs --since 10m --level error`.

### Error NMB-301: token inválido o vencido

Indica que el token de API no es válido, fue revocado o venció. Hay que comprobar que la variable `NIMBUS_TOKEN` esté definida y que el token siga activo con `nimbus token list`. Si se usa el inicio de sesión interactivo, basta con ejecutar `nimbus login` de nuevo.

### Error NMB-429: demasiadas peticiones

Se produce al superar el límite de 600 peticiones por minuto por token. Hay que esperar los segundos indicados en la cabecera `Retry-After` y, en scripts automáticos, implementar reintentos con espera exponencial: 1, 2, 4 y 8 segundos como máximo.

## Problemas de rendimiento

Si una aplicación responde con lentitud, el primer paso es mirar `nimbus status --metrics`, que muestra el uso de CPU y memoria de cada instancia. Si la memoria supera de forma sostenida el 85 % del límite del plan, la instancia puede ser reiniciada por el sistema; este reinicio se registra como el evento `OOM_KILLED`. La solución es optimizar el consumo de memoria o subir de plan.

Para escalar manualmente se usa `nimbus scale --instances 3`. El escalado automático se activa con `nimbus autoscale enable --min 2 --max 8` y está disponible solo en los planes Pro y Enterprise; reacciona cuando el uso medio de CPU supera el 70 % durante 3 minutos seguidos.

## Dominios y certificados

Después de añadir un dominio personalizado con `nimbus domain add ejemplo.com`, hay que crear en el proveedor de DNS un registro CNAME que apunte al valor que muestra la CLI. La propagación del DNS puede tardar hasta 48 horas, aunque normalmente ocurre en menos de una hora. Los certificados TLS se emiten y renuevan automáticamente; la emisión empieza cuando Nimbus detecta el registro DNS correcto y suele completarse en 5 minutos.

Si el certificado muestra el estado `PENDING` durante más de 2 horas, hay que verificar que no exista un registro CAA que impida la emisión a la autoridad certificadora Let's Encrypt.

## Contacto con soporte

Los clientes Pro pueden abrir tickets escribiendo a soporte@nimbus.example, indicando el identificador de la aplicación y adjuntando el informe de `nimbus doctor --report`. El plan Gratuito solo cuenta con el foro de la comunidad.
