# Auditoria Detallada Del XML - Fase 3

Archivo auditado: `data/output/Reto Diseño de Redes Fase 3 avance.xml`  
Archivo Packet Tracer asociado: `data/input/Reto Diseño de Redes Fase 3 avance.pkt`  
Fecha de auditoria: 2026-06-14

Metodo: lectura estructurada del XML con foco en `DEVICE`, `RUNNINGCONFIG`, `STARTUPCONFIG`, `VLANS`, `VTP`, `DHCP_SERVERS`, WLC/CAPWAP, WLANs, endpoints y enlaces fisicos.

## Resumen Ejecutivo

El avance actual ya corrige varios puntos criticos que estaban pendientes en la auditoria anterior. El router principal ahora usa `ip helper-address 172.23.45.130` hacia el servidor DHCP real en VLAN 10,20,30,40,50,60 y 80, y ya no se observa helper en VLAN 70. Tambien ya existe una ACL de Invitados aplicada inbound en `GigabitEthernet0/0/0.30`.

El switching avanzo bastante: los switches principales y de acceso ya tienen hostname real, VLAN 10-80 presentes, dominio VTP `OMI-REDES`, password `OMI2026`, modo cliente en la mayoria y trunks configurados con VLAN permitidas. El switch principal `SW-1ERA.1-42` conserva rol de servidor y aparecen bloques VTP con version 2.

Lo que todavia impide darlo por terminado es la capa wireless y la administracion: el WLC existe y tiene WLANs 10-60, pero no tiene interfaces dinamicas, no tiene APs asociados, no existe WLAN de Jueces VLAN 80 y la clave de Primaria esta mal escrita como `consurso123`. Ademas, los switches no tienen SVI de administracion VLAN 70 ni VTY usable para Telnet.

Estado general estimado:

| Area | Avance | Veredicto |
| --- | ---: | --- |
| Topologia fisica y objetos TIA/EIA | 82% | Parcialmente listo |
| VLSM y VLAN base | 90% | Bien encaminado |
| Router-on-a-stick | 90% | Casi listo |
| DHCP como servicio | 82% | Parcialmente listo |
| VTP | 72% | Parcial, validar version/propagacion |
| Switching backbone/acceso | 75% | Parcialmente listo |
| Wireless con WLC/LWAP | 45% | Pendiente operativo |
| Seguridad por ACL | 70% | ACL base presente |
| Administracion Telnet | 10% | Pendiente |
| Endpoints y pruebas | 15% | Pendiente |
| Export de configuraciones | 0% | Pendiente |

Conclusion: el core ya se ve mucho mas sano. La prioridad ya no es el router ni el DHCP relay; ahora es terminar WLC/APs, validar VTP/trunks de punta a punta, dar IP a clientes finales y preparar administracion remota.

## Inventario Detectado

El XML contiene 156 dispositivos/objetos.

| Tipo detectado | Cantidad |
| --- | ---: |
| Wall Mount | 33 |
| PC/Pc | 30 |
| Switch | 24 |
| Patch Panel | 20 |
| LightWeightAccessPoint | 16 |
| Power Distribution Device | 9 |
| Laptop | 9 |
| Pda / Smartphone | 7 |
| Printer | 4 |
| Server | 3 |
| Router | 2 |
| MultiLayerSwitch | 1 |
| WirelessLanController | 1 |

Nota: el XML conserva objetos genericos o de Packet Tracer que aparecen como `Switch`, `PC`, `Router` o `DNS-1ERA.1-36`; por eso la lectura fina se hizo por hostname/configuracion, no solo por tipo.

## Core De Red

### Router principal `RT-1ERA.1-45`

Veredicto: PASS parcial alto.

Evidencia positiva:

- Existe como router principal con `RUNNINGCONFIG` y `STARTUPCONFIG`.
- Tiene subinterfaces `GigabitEthernet0/0/0.10` a `.80`.
- Cada subinterfaz tiene `encapsulation dot1Q` correcto para VLAN 10,20,30,40,50,60,70,80.
- Las IP gateway coinciden con el VLSM definido en `172.23.40.0/21`.
- DHCP relay ya apunta al servidor correcto `172.23.45.130` en VLAN 10,20,30,40,50,60 y 80.
- VLAN 70 ya no muestra helper, correcto porque ahi vive el servidor DHCP y el gateway de gestion.
- `ACL_INVITADOS_IN` existe y esta aplicada inbound en `GigabitEthernet0/0/0.30`.

Subinterfaces detectadas:

| VLAN | Gateway | Helper |
| ---: | --- | --- |
| 10 | `172.23.40.1/23` | `172.23.45.130` |
| 20 | `172.23.42.1/24` | `172.23.45.130` |
| 30 | `172.23.43.1/24` | `172.23.45.130` |
| 40 | `172.23.44.1/24` | `172.23.45.130` |
| 50 | `172.23.45.1/26` | `172.23.45.130` |
| 60 | `172.23.45.65/26` | `172.23.45.130` |
| 70 | `172.23.45.129/26` | Sin helper |
| 80 | `172.23.45.193/27` | `172.23.45.130` |

ACL detectada:

```ios
ip access-list extended ACL_INVITADOS_IN
 remark Invitados no puede entrar a redes internas OMI/Tec
 deny ip 172.23.43.0 0.0.0.255 172.23.40.0 0.0.7.255
 permit ip 172.23.43.0 0.0.0.255 any
interface GigabitEthernet0/0/0.30
 ip access-group ACL_INVITADOS_IN in
```

Pendiente:

- Probar desde Invitados que no alcance redes internas, y desde otras VLANs que si alcance servidor/DHCP segun la rubrica.
- Si la entrega pide Internet simulado, falta ruta default/NAT/enlace de salida; si no lo pide, no es bloqueo.
- Documentar pruebas `ping` y `ipconfig /renew`.

### Switch principal `SW-1ERA.1-42`

Veredicto: PASS parcial alto.

Evidencia:

- Existe como `MultiLayerSwitch`.
- VLAN 10,20,30,40,50,60,70,80 presentes.
- Tiene trunks hacia `SW-1ERA.1-43`, WLC y router.
- `Gi1/0/4` aparece como trunk hacia `RT-1ERA.1-45`.
- `Gi1/0/5` aparece en access VLAN 70 hacia `DHCP-1ERA.1-39`.
- VTP muestra dominio `OMI-REDES`, password `OMI2026`, modo numerico `0` y bloques con version 2.

Pendiente:

- En el bloque global del switch aun aparece una lectura VTP con `VERSION 1`, aunque los bloques de `vlan.dat`/flash traen version 2. Validar en Packet Tracer con `show vtp status`.
- No hay `interface Vlan70` con IP de administracion.
- Las lineas VTY siguen sin password Telnet util.

## VTP Y Switching

Veredicto: PASS parcial.

### VTP

Evidencia general:

- Todos los switches auditados tienen dominio `OMI-REDES`.
- Todos los switches auditados muestran password `OMI2026`.
- Los switches de acceso aparecen en modo numerico `1`, consistente con VTP client.
- Todos los switches relevantes ya muestran VLAN 10,20,30,40,50,60,70,80 en el XML.

Version 2 detectada:

| Switch | Estado VTP version 2 |
| --- | --- |
| `SW-1ERA.1-42` | Detectada en bloques internos; validar como servidor |
| `SW-1ERA.1-43` | Detectada en algunos bloques internos |

Switches que siguen mostrando solo version 1 en el XML:

| Switch |
| --- |
| `SW-1ERA.1-40` |
| `SW-2ERA.1-44` |
| `SW-2ERA.1-42` |
| `SW-3ERA.1-44` |
| `SW-3ERA.1-42` |
| `SW-1ERC.1-44` |
| `SW-1ERC.1-42` |
| `SW-1ERC.1-40` |
| `SW-4ERC.1-44` |
| `SW-4ERC.1-42` |
| `SW-1ERB.1-44` |
| `SW-1ERB.1-42` |
| `SW-2ERB.1-44` |
| `SW-2ERB.1-42` |
| `SW-2ERB.1-40` |
| `SW-2ERBA.1-44` |
| `SW-2ERBA.1-42` |
| `SW-2ERBL.1-44` |
| `SW-2ERBL.1-42` |

Lectura: esto no necesariamente rompe VTP en Packet Tracer si el servidor esta en version 2 y los clientes aprenden las VLAN. Para la rubrica, demuestra version 2 en `SW-1ERA.1-42` y demuestra en clientes que aprendieron VLAN 10-80.

### Trunks Y Access Ports

Evidencia positiva:

- `SW-1ERA.1-43` ya tiene 6 trunks con VLAN permitidas.
- Los switches `.44` de distribucion/fibra ya tienen trunks hacia sus pares.
- Los switches `.42` y `.40` ya tienen trunks de uplink y varios puertos access.
- El XML ya muestra `switchport trunk allowed vlan 10,20,30,40,50,60,70,80` en los enlaces principales.

Resumen de trunks detectados:

| Switch | Trunks detectados |
| --- | ---: |
| `SW-1ERA.1-42` | 3 |
| `SW-1ERA.1-43` | 6 |
| `SW-1ERB.1-44` | 6 |
| `SW-1ERC.1-44` | 4 |
| `.44` restantes | 2 cada uno |
| Switches `.42`/`.40` de acceso | 1 a 2 cada uno |

Pendiente:

- Verificar en Packet Tracer con `show interfaces trunk` que los trunks esten up/up, no solo configurados.
- Confirmar que los puertos access correspondan a los dispositivos reales conectados.
- Guardar cambios con `write memory` en todos los switches.

## DHCP

Veredicto: PASS parcial alto.

Servidor principal:

- `DHCP-1ERA.1-39`
- IP: `172.23.45.130`
- Mascara: `255.255.255.192`
- Gateway: `172.23.45.129`
- Conectado por el switch principal en VLAN 70.

Pools detectados:

| Pool | Red | Gateway | Rango dinamico |
| --- | --- | --- | --- |
| `VLAN10_Primaria` | `172.23.40.0/23` | `172.23.40.1` | `172.23.40.3 - 172.23.41.255` |
| `VLAN_Secundaria` | `172.23.42.0/24` | `172.23.42.1` | `172.23.42.3 - 172.23.42.255` |
| `VLAN_Invitados` | `172.23.43.0/24` | `172.23.43.1` | `172.23.43.3 - 172.23.43.255` |
| `VLAN_Preparatoria` | `172.23.44.0/24` | `172.23.44.1` | `172.23.44.3 - 172.23.44.255` |
| `VLAN_Entrenadores` | `172.23.45.0/26` | `172.23.45.1` | `172.23.45.3 - 172.23.45.63` |
| `VLAN_Prensa` | `172.23.45.64/26` | `172.23.45.65` | `172.23.45.67 - 172.23.45.127` |
| `VLAN_GestionTI` | `172.23.45.128/26` | `172.23.45.129` | `172.23.45.154 - 172.23.45.190` |
| `VLAN_Jueces` | `172.23.45.192/27` | `172.23.45.193` | `172.23.45.200 - 172.23.45.222` |

Pendiente:

- Sigue existiendo un `serverPool` generico con gateway `0.0.0.0`, inicio `172.23.45.128` y fin `172.23.47.127`; conviene eliminarlo o desactivarlo para que no confunda.
- Los pools tienen `DNS_SERVER 0.0.0.0`; si el DNS `DNS-1ERA.1-36` se va a usar, falta poner su IP.
- Los campos `WLC_ADDRESS` de los pools estan en `0.0.0.0`; si se quiere descubrimiento CAPWAP por DHCP, configurar opcion/direccion WLC o definir el controlador manualmente en APs.

## WLC Y Wireless

Veredicto: FAIL operativo, con base creada.

### WLC `WLC-1ERA.1-35`

Evidencia:

- IP de gestion: `172.23.45.131/26`.
- Gateway: `172.23.45.129`.
- WLANs creadas para VLAN 10,20,30,40,50,60.
- WLANs habilitadas (`ENABLED true`).

WLANs detectadas:

| WLAN | SSID | VLAN | Observacion |
| --- | --- | ---: | --- |
| Primaria | `Primaria-Wifi` | 10 | Clave escrita `consurso123` |
| Secundaria | `Secundaria-Wifi` | 20 | Creada |
| Invitados | `Invitados-Wifi` | 30 | Creada |
| Preparatoria | `Preparatoria-Wifi` | 40 | Creada |
| Entrenadores | `Entrenadores-Wifi` | 50 | Creada |
| Prensa | `Prensa-Wifi` | 60 | Creada |

Problemas:

- `WLC_INTERFACES` esta vacio.
- Cada WLAN tiene `INTERFACE_NAME` vacio.
- `APS` esta vacio: ningun AP aparece asociado al WLC.
- `PRIMARY_AC` del WLC aparece como `0.0.0.0`.
- No hay WLAN de Jueces / VLAN 80.
- La clave de Primaria esta mal escrita: `consurso123`; deberia ser `concurso123`.

Accion recomendada:

- En WLC, si Packet Tracer muestra `Interfaces`, crear interfaces dinamicas para VLAN 10,20,30,40,50,60 y 80.
- Corregir la clave de Primaria.
- Crear WLAN `Jueces-Wifi` VLAN 80 si la rubrica pide jueces inalambricos.
- Asociar APs al WLC y comprobar que aparezcan en la lista de APs.

### AP ligeros

Veredicto: FAIL pendiente.

Se detectan 16 LWAP 3702i con nombres TIA en varios casos, pero sin asociacion CAPWAP.

Problemas comunes:

- Todos los APs revisados tienen `PRIMARY_AC 0.0.0.0`.
- Los puertos de los APs no muestran IP, mascara ni gateway.
- Los APs tienen `WLANS` vacio.
- El WLC tiene `APS` vacio.

Accion recomendada:

- Configurar los puertos donde conectan APs en VLAN 70 o como lo requiera el modelo WLC de Packet Tracer.
- Dar DHCP/IP de gestion a cada AP.
- Definir controlador primario `172.23.45.131` en cada LWAP si no descubren el WLC automaticamente.
- Verificar que cada AP aparezca registrado en el WLC antes de probar clientes Wi-Fi.

## Administracion Telnet

Veredicto: FAIL pendiente.

Evidencia:

- Existen lineas VTY en router y switches.
- No se detecta `password OMItelnet2026`.
- No se detecta `transport input telnet`.
- No se detecta `interface Vlan70` con IP de administracion en switches.
- No se detecta `enable secret OMIenable2026`.

Accion recomendada:

- Configurar `enable secret OMIenable2026`.
- Configurar VTY con `password OMItelnet2026`, `login` y `transport input telnet`.
- Asignar IP unica en `interface vlan 70` a cada switch de acceso/distribucion.
- Configurar `ip default-gateway 172.23.45.129` en switches capa 2.
- Probar Telnet desde VLAN 70 y confirmar que Invitados no puede abrir Telnet.

## Endpoints

Veredicto: FAIL pendiente.

Estado detectado:

- Endpoints tipo PC/Laptop/Pda/Printer/Server auditados: 53.
- Con IP valida `172.23.x.x`: 2.
- Con APIPA `169.254.x.x`: 0.
- Sin IP registrada en el XML: 51.

Endpoints con IP valida:

| Dispositivo | IP |
| --- | --- |
| `DHCP-1ERA.1-39` | `172.23.45.130/26` |
| `ING-04SRV-01` | `172.23.45.194/27` |

Pendiente:

- Renovar DHCP en clientes despues de terminar trunks/access VLANs/APs.
- Asignar IPs estaticas a impresoras y DNS si se requiere.
- Verificar que Jueces, Invitados, Prensa, Entrenadores, Primaria/Secundaria y Preparatoria reciban direccion correcta.
- Ejecutar pings al servidor local `172.23.45.194`.

## Seguridad

Veredicto: PASS parcial.

Lo positivo:

- Ya existe `ACL_INVITADOS_IN`.
- Ya esta aplicada en VLAN 30 inbound.
- La regla bloquea Invitados `172.23.43.0/24` hacia todo el bloque interno `172.23.40.0/21`.
- Despues permite salida hacia `any`.

Pendiente:

- Probar que Invitados no llegue a VLAN 10,20,40,50,60,70,80.
- Probar que Invitados aun tenga salida permitida hacia lo que la rubrica considere externo.
- Si la rubrica pide proteger Jueces/Servidor Local con mas detalle, agregar ACL adicional.

## Enlaces Fisicos

Veredicto: PASS fisico, PASS parcial logico.

El XML conserva 268 enlaces. La topologia fisica de backbone sigue armada y ahora la configuracion de trunks ya aparece en switches principales y closets.

Pendiente:

- Validar estado up/up de trunks en Packet Tracer.
- Revisar que no haya puertos de usuario mezclados dentro de rangos trunk.
- Confirmar que los puertos de APs queden en VLAN 70 para CAPWAP/gestion.

## Checklist De Aceptacion

| Criterio | Estado | Evidencia/pendiente |
| --- | --- | --- |
| Subinterfaces dot1Q en router | PASS | VLAN 10-80 presentes |
| Gateways VLSM correctos | PASS | Coinciden con `172.23.40.0/21` |
| DHCP helper correcto | PASS | Helper `172.23.45.130`; VLAN 70 sin helper |
| DHCP pools por VLAN | PASS parcial | Pools correctos, queda `serverPool` generico |
| ACL Invitados | PASS parcial | ACL creada y aplicada; faltan pruebas |
| VTP dominio/password | PASS | `OMI-REDES` / `OMI2026` detectado |
| VTP version 2 | PASS parcial | Server y `SW-1ERA.1-43` con version 2; clientes muestran 1 |
| VLANs en switches | PASS parcial | VLAN 10-80 detectadas en todos los switches auditados |
| Trunks backbone | PASS parcial | Configurados; falta verificar up/up |
| Access ports por area | PASS parcial | Hay puertos access; falta validar contra conexiones reales |
| WLC gestion | PASS | `172.23.45.131/26` |
| WLANs 10-60 | PASS parcial | Creadas; Primaria tiene password mal escrito |
| WLAN Jueces VLAN 80 | FAIL | No detectada |
| Interfaces dinamicas WLC | FAIL | `WLC_INTERFACES` vacio |
| APs unidos al WLC | FAIL | `APS` vacio y APs con `PRIMARY_AC 0.0.0.0` |
| Telnet administracion | FAIL | Sin SVI VLAN 70 ni VTY completo |
| Clientes con IP | FAIL | Solo 2 endpoints con IP valida |
| Pings finales | Pendiente | No demostrable desde XML |
| Export configs | Pendiente | Falta generar archivos finales |

## Lo Que Hace Falta En Orden De Prioridad

1. Validar `show vtp status` en `SW-1ERA.1-42`: debe verse Server, dominio `OMI-REDES`, version 2.
2. Validar `show vlan brief` y `show interfaces trunk` en todos los switches clave.
3. Eliminar/desactivar `serverPool` generico del DHCP.
4. Corregir clave de Primaria en WLC: `concurso123`.
5. Crear WLAN `Jueces-Wifi` VLAN 80 si se requiere.
6. Resolver Paso 8.2: crear interfaces dinamicas del WLC si Packet Tracer muestra esa pantalla; si no, usar VLAN ID en cada WLAN.
7. Asociar los 16 LWAP al WLC con controlador `172.23.45.131`.
8. Configurar/validar puertos de APs en VLAN 70.
9. Configurar SVIs VLAN 70 e IP de gestion en switches.
10. Habilitar Telnet de laboratorio con password y `transport input telnet`.
11. Renovar DHCP en clientes y verificar que ya no queden sin IP.
12. Configurar IPs estaticas para DNS/impresoras si la rubrica las pide.
13. Probar ACL de Invitados.
14. Ejecutar pings por VLAN hacia `ING-04SRV-01` (`172.23.45.194`).
15. Exportar configuraciones finales y capturas/evidencias.

## Veredicto Actual

El avance ya paso de "maqueta fisica con core incompleto" a "core casi listo con switching parcialmente configurado". Muy buen salto: helpers corregidos, ACL aplicada, VLANs/trunks distribuidos y servidor local con IP valida.

El bloqueo real ahora esta en wireless y administracion. Mientras los APs no se unan al WLC y los clientes no reciban IP, la red todavia no queda demostrable de punta a punta. La siguiente sesion deberia enfocarse en WLC/APs, luego SVIs/Telnet, y finalmente pruebas de DHCP/ping por cada VLAN.
