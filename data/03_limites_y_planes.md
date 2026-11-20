# Manual de Nimbus: Planes, límites y facturación

Nimbus ofrece tres planes: Gratuito, Pro y Enterprise. Este documento resume los límites de cada uno y el funcionamiento de la facturación.

## Comparación de planes

### Plan Gratuito

El plan Gratuito está pensado para pruebas y proyectos personales. Permite hasta 2 aplicaciones por cuenta, con una sola instancia cada una y 256 MB de memoria por instancia. Las aplicaciones del plan Gratuito entran en suspensión tras 30 minutos sin tráfico y tardan unos 10 segundos en reactivarse con la primera petición. El ancho de banda incluido es de 10 GB al mes. No incluye dominios personalizados, registro de auditoría ni soporte técnico.

### Plan Pro

El plan Pro cuesta 25 dólares por mes por cada miembro del equipo con rol de Desarrollador o superior; los Lectores son gratuitos y no cuentan. Incluye hasta 50 aplicaciones, escalado de hasta 10 instancias por aplicación, 2 GB de memoria por instancia y 500 GB de ancho de banda al mes. Las aplicaciones nunca entran en suspensión. Incluye dominios personalizados con certificados TLS automáticos, registro de auditoría de 180 días y soporte por correo con un tiempo de respuesta objetivo de 24 horas hábiles.

### Plan Enterprise

El plan Enterprise se contrata a medida. Ofrece aplicaciones ilimitadas, hasta 100 instancias por aplicación, inicio de sesión único (SSO) mediante SAML, registro de auditoría de 365 días, y un acuerdo de nivel de servicio (SLA) del 99,95 % de disponibilidad mensual. El soporte es 24 horas al día, todos los días, con un tiempo de respuesta objetivo de 1 hora para incidentes críticos.

## Límites de uso comunes

Independientemente del plan, existen límites técnicos que no se pueden ampliar:

- El tamaño máximo de un paquete de despliegue es de 500 MB.
- El tiempo máximo de una petición HTTP es de 60 segundos; las peticiones más largas reciben el error 504.
- El tamaño máximo del cuerpo de una petición es de 32 MB.
- Se admiten como máximo 5 dominios personalizados por aplicación en el plan Pro.
- Los registros de la aplicación se conservan durante 7 días en el plan Gratuito y 30 días en los planes Pro y Enterprise.

La API de Nimbus aplica un límite de 600 peticiones por minuto por token. Al superarlo, la API responde con el código 429 y la cabecera `Retry-After` indica cuántos segundos hay que esperar.

## Facturación

La facturación es mensual y se cobra por adelantado el día en que se contrató el plan. Los métodos de pago aceptados son tarjeta de crédito y débito; las transferencias bancarias solo están disponibles en Enterprise. Los cargos por ancho de banda excedente se calculan al final de cada ciclo a razón de 0,08 dólares por GB adicional.

Si se añade un miembro a mitad de ciclo, el cargo se prorratea por los días restantes. Si se quita un miembro, no se emite reembolso, pero el crédito no se pierde: se aplica a la siguiente factura.

## Cancelación y reembolsos

Se puede cancelar el plan Pro en cualquier momento desde el panel de facturación o con `nimbus billing cancel`. La cancelación entra en vigor al final del ciclo ya pagado; las aplicaciones siguen funcionando hasta esa fecha y luego pasan al plan Gratuito. Si el equipo tiene más de 2 aplicaciones, se conservan las 2 más antiguas activas y el resto se suspende durante 30 días antes de ser eliminada. Nimbus ofrece reembolso completo dentro de los primeros 14 días posteriores a la primera contratación del plan Pro.
