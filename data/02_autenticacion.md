# Manual de Nimbus: Autenticación y permisos

Este documento describe cómo se autentican los usuarios y las máquinas contra la plataforma Nimbus, y cómo se administran los permisos dentro de un equipo.

## Inicio de sesión interactivo

El comando `nimbus login` abre el navegador para completar el inicio de sesión mediante OAuth 2.0 con el flujo de código de autorización y PKCE. Al finalizar, la CLI guarda un token de acceso en el almacén de credenciales del sistema operativo: el Administrador de credenciales en Windows, Keychain en macOS y libsecret en Linux. El token de acceso interactivo dura 12 horas; después de ese tiempo la CLI renueva el token automáticamente usando un token de refresco válido por 30 días.

Si el usuario no ha usado la CLI durante más de 30 días, el token de refresco expira y es necesario volver a ejecutar `nimbus login`. Para cerrar la sesión y borrar las credenciales locales se usa `nimbus logout`.

## Tokens de API para automatización

En entornos no interactivos, como servidores de integración continua, no se debe usar el inicio de sesión por navegador. En su lugar se crean tokens de API con el comando `nimbus token create --name ci-github --scope deploy`. El token se muestra una única vez en pantalla y no puede recuperarse después; si se pierde hay que revocarlo y crear uno nuevo.

Los tokens de API tienen el prefijo `nmb_` seguido de 40 caracteres. Se pasan a la CLI mediante la variable de entorno `NIMBUS_TOKEN`. Por defecto un token de API vence a los 90 días, aunque puede configurarse un vencimiento de entre 1 y 365 días con la opción `--expires-in`. Cada cuenta puede tener como máximo 20 tokens activos al mismo tiempo.

Los alcances (scopes) disponibles son:

- `read`: permite consultar el estado, los registros y la configuración.
- `deploy`: incluye `read` y además permite desplegar y revertir versiones.
- `admin`: incluye `deploy` y además permite gestionar miembros, facturación y destruir aplicaciones.

Se recomienda siempre usar el alcance mínimo necesario. Un pipeline de despliegue normalmente solo necesita `deploy`.

## Roles dentro de un equipo

Cada equipo en Nimbus tiene cuatro roles: Propietario, Administrador, Desarrollador y Lector. El Propietario es único por equipo y es el único que puede eliminar el equipo o transferir la propiedad. Los Administradores pueden invitar y quitar miembros y modificar la facturación. Los Desarrolladores pueden desplegar y gestionar variables de entorno. Los Lectores solo tienen acceso de lectura.

Las invitaciones se envían con `nimbus team invite correo@ejemplo.com --role developer` y caducan a los 7 días si no son aceptadas.

## Autenticación en dos pasos

La autenticación en dos pasos (2FA) es obligatoria para los roles Propietario y Administrador desde la versión 3.0. Nimbus admite aplicaciones TOTP como método principal y claves de seguridad FIDO2 como alternativa. Al activar la 2FA se generan 10 códigos de recuperación de un solo uso; se aconseja guardarlos en un lugar seguro. SMS no es un método soportado porque se considera inseguro.

## Registro de auditoría

Todas las acciones sensibles quedan registradas en el registro de auditoría: inicios de sesión, creación y revocación de tokens, cambios de roles y despliegues. El registro se conserva durante 180 días en el plan Pro y 365 días en el plan Enterprise. El plan Gratuito no incluye registro de auditoría. Los administradores pueden consultarlo con `nimbus audit list --since 7d`.
