# Requisitos - Fase 3: Configuracion Logica e Implementacion de Red

## Proposito

Implementar en Cisco Packet Tracer la infraestructura temporal de red local para la Olimpiada Mexicana de Informatica (OMI), integrada a la red actual del Tecnologico de Monterrey, Campus Chihuahua, sin afectar la continuidad operativa institucional.

La Fase 3 se enfoca en configuracion logica, segmentacion, servicios, seguridad y pruebas de conectividad. Queda fuera de alcance la re-encriptacion del XML a `.pkt` y la redaccion de conclusiones finales de Fase 4.

## Decisiones Inamovibles

- Distribucion fisica oficial: Alternativa A, usando edificios de Ingenieria, Humanidades y CIT.
- Bloque IPv4 asignado: `172.23.40.0/21`.
- Tabla VLSM aprobada, reflejada en el XML actual para VLAN 10 a VLAN 80.
- Uso de Cisco IOS CLI como mecanismo de configuracion.
- Cableado estructurado conforme a TIA/EIA-568 y documentacion fisica conforme a TIA/EIA-606-B.

## Segmentos De Servicio

| VLAN | Nombre | Usuarios/servicio | Subred | Gateway | Capacidad DHCP |
| --- | --- | --- | --- | --- | --- |
| 10 | Primaria | 264 laptops inalambricas rentadas en Sala de Congresos CIT | `172.23.40.0/23` | `172.23.40.1` | 510 hosts |
| 20 | Secundaria | 198 equipos rentados en 5 salones de Humanidades via AP | `172.23.42.0/24` | `172.23.42.1` | 254 hosts |
| 30 | Invitados | Aproximadamente 250 acompanantes en planta baja CIT | `172.23.43.0/24` | `172.23.43.1` | 254 hosts |
| 40 | Preparatoria | 132 competidores en laboratorios cableados | `172.23.44.0/24` | `172.23.44.1` | 254 hosts |
| 50 | Entrenadores | 40 conexiones mixtas en salon 7201 CIT | `172.23.45.0/26` | `172.23.45.1` | 62 hosts |
| 60 | Prensa | 32 reporteros via Wi-Fi en Sala Borrego | `172.23.45.64/26` | `172.23.45.65` | 62 hosts |
| 70 | GestionTI | Administracion, DHCP y servicios de soporte | `172.23.45.128/26` | `172.23.45.129` | 62 hosts |
| 80 | Jueces | 10 PCs criticas, impresoras y servidor local de evaluacion | `172.23.45.192/27` | `172.23.45.193` | 30 hosts |

## Requisitos Funcionales

- RF-01: El router 4331 principal debe enrutar entre VLANs mediante subinterfaces `dot1Q`.
- RF-02: Cada VLAN debe usar su gateway VLSM aprobado dentro de `172.23.40.0/21`.
- RF-03: Los clientes autorizados deben obtener IP dinamica desde el servidor DHCP `DHCP-1ERA.1-39`.
- RF-04: Los switches de distribucion y acceso deben transportar VLAN 10,20,30,40,50,60,70,80 en enlaces troncales.
- RF-05: Los puertos de usuario final deben configurarse como acceso en la VLAN del area correspondiente.
- RF-06: La VLAN de Invitados debe quedar aislada de la red interna y del segmento de Jueces.
- RF-07: Los segmentos de competidores autorizados deben alcanzar el Servidor Local de evaluacion.
- RF-08: La red de Prensa e Invitados debe tener salida controlada a Internet cuando el escenario de Packet Tracer incluya ese enlace.

## Requisitos No Funcionales

- RNF-01: Priorizar seguridad del examen y aislamiento del servidor local.
- RNF-02: Mantener estabilidad en zonas inalambricas de alta densidad, especialmente Primaria.
- RNF-03: Conservar claridad academica: nombres de VLAN, descripciones de interfaces y trazabilidad por edificio.
- RNF-04: No cargar el XML completo en herramientas de contexto; auditar por bloques de configuracion, VLAN, IP y dispositivos.
- RNF-05: Mantener compatibilidad con Cisco Packet Tracer 9.0 y comandos IOS soportados por ISR4331, Catalyst 3650 y 2960.

## Auditoria Inicial Del XML

Archivo auditado: `data/output/Reto-Redes.xml`.

- PASS parcial: existe router ISR4331 `RT-1ERA.1-45` con subinterfaces `GigabitEthernet0/0/0.10` a `.80`, encapsulacion `dot1Q` e IPs VLSM (`lineas 36899-36937`).
- PASS parcial: existe switch multilayer `SW-1ERA.1-42` con VLAN 10,20,30,40,50,60,70,80 en `vlan.dat` y configuracion global (`lineas 43280-43427`).
- PASS parcial: existe trunk de `SW-1ERA.1-42` hacia `RT-1ERA.1-45` por `GigabitEthernet1/0/4` con VLANs permitidas 10-80 (`lineas 43050-43053`).
- PASS parcial: existe servidor `DHCP-1ERA.1-39` con IP `172.23.45.130/26` y gateway `172.23.45.129` (`lineas 83714-83803`).
- PASS parcial: existen pools DHCP para VLAN 10,20,30,40,50,60,70,80 (`lineas 85189-85314`).
- FAIL pendiente: no se encontro ACL aplicada para aislar Invitados de Jueces/red interna.
- FAIL pendiente: la mayoria de switches de acceso siguen con VLAN 1 por defecto y sin trunks/puertos de acceso documentados.
- FAIL pendiente: no hay evidencia exportada de pruebas ping 100% exitosas hacia el Servidor Local.
