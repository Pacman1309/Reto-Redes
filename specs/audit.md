# Auditoria Detallada Del XML - Fase 3 WLC Corr

Archivo auditado: `data/output/Reto Diseño de Redes Fase 3 WLC Corr.xml`
Archivo Packet Tracer asociado: `data/input/Reto Diseño de Redes Fase 3 WLC Corr.pkt`
Fecha de auditoria: 2026-06-14

Metodo: lectura estructurada del XML con foco en el camino DHCP completo:
cliente wireless, AP, puerto de switch, WLC, trunk WLC-switch, router-on-a-stick,
`ip helper-address`, servidor DHCP, pools y leases.

## Veredicto Ejecutivo

El WLC 3504, las interfaces dinamicas, los pools DHCP y los trunks principales
estan casi todos correctos. El problema que explica que los clientes no puedan
obtener IP es este:

**Las WLAN quedaron en modo `WLAN_SWITCH_MODE = 1` y todos los puertos de AP
siguen como `access vlan 70`.**

Con esa combinacion, el trafico de clientes sale por la VLAN de gestion del AP
en vez de salir por la VLAN del SSID. Resultado:

- Los clientes no llegan a su gateway real, por ejemplo `172.23.40.1`.
- DHCP no llega al pool correcto, por ejemplo `VLAN10_Primaria`.
- Los clientes que si reciben algo caen en `VLAN_GestionTI`.
- El pool `VLAN_GestionTI` ya esta lleno con 37 leases, asi que otros clientes
  muestran `DHCP request failed`.

Conclusion practica: el problema no esta en que falte el pool de DHCP, ni en el
router helper, ni en el trunk WLC-switch. El fallo esta en el modo de switching
wireless contra la configuracion access VLAN 70 de los puertos AP.

## Estado General

| Area | Estado | Veredicto |
| --- | --- | --- |
| WLC 3504 | Encendido, unico WLC activo | PASS |
| Interfaces dinamicas WLC | VLAN 10,20,30,40,50,60,80 creadas | PASS |
| WLANs | 7 WLANs activas y mapeadas a interfaces | PASS parcial |
| Modo WLAN | Todas con `WLAN_SWITCH_MODE = 1` | Riesgo principal |
| APs | 16 APs con primary controller `172.23.45.131` | PASS |
| Puertos AP | Todos en `access vlan 70` | OK solo sin local switching |
| Trunk WLC-switch | `Gi1/0/2` trunk native 70, allowed 10-80 | PASS |
| Trunks backbone | VLAN 10,20,30,40,50,60,70,80 permitidas | PASS |
| Router helpers | Helpers a `172.23.45.130` en VLAN de usuarios | PASS |
| DHCP pools | Pools correctos por VLAN | PASS |
| DHCP real de clientes | Clientes caen en GestionTI o fallan | FAIL |

## WLC 3504

Dispositivo activo:

| Campo | Valor |
| --- | --- |
| Nombre | `WLC-1ERA.1-35` |
| Modelo | `WLC-3504` |
| Power | `true` |
| Management IP | `172.23.45.131/26` |
| Gateway management | `172.23.45.129` |
| Interfaces WLC | 9 |
| WLANs | 7 |
| APs en WLC | 16 |

Ya no aparece el WLC-PT viejo como dispositivo activo. Esta parte esta bien.

## Interfaces Dinamicas Del WLC

| Interface | VLAN | IP | Mascara | Gateway | DHCP Server | Port | AP Mgmt |
| --- | ---: | --- | --- | --- | --- | ---: | --- |
| `management` | 0 | `172.23.45.131` | `255.255.255.192` | `172.23.45.129` | `0.0.0.0` | 1 | `true` |
| `virtual` | 0 | `192.0.2.1` | `255.255.255.255` | - | `0.0.0.0` | 0 | `false` |
| `vlan10_primaria` | 10 | `172.23.40.2` | `255.255.254.0` | `172.23.40.1` | `172.23.45.130` | 1 | `false` |
| `vlan20_secundaria` | 20 | `172.23.42.2` | `255.255.255.0` | `172.23.42.1` | `172.23.45.130` | 1 | `false` |
| `vlan30_invitados` | 30 | `172.23.43.2` | `255.255.255.0` | `172.23.43.1` | `172.23.45.130` | 1 | `false` |
| `vlan40_preparatoria` | 40 | `172.23.44.2` | `255.255.255.0` | `172.23.44.1` | `172.23.45.130` | 1 | `false` |
| `vlan50_entrenadores` | 50 | `172.23.45.2` | `255.255.255.192` | `172.23.45.1` | `172.23.45.130` | 1 | `false` |
| `vlan60_prensa` | 60 | `172.23.45.66` | `255.255.255.192` | `172.23.45.65` | `172.23.45.130` | 1 | `false` |
| `vlan80_jueces` | 80 | `172.23.45.199` | `255.255.255.224` | `172.23.45.193` | `172.23.45.130` | 1 | `false` |

Esto esta correcto. Que las interfaces dinamicas usen `Port 1` esta bien porque
el enlace fisico del WLC al switch es trunk.

## WLANs

| WLAN | VLAN | Interface | Enabled | Switch mode | Clave | Estado |
| --- | ---: | --- | --- | ---: | --- | --- |
| `Primaria-Wifi` | 10 | `vlan10_primaria` | `true` | 1 | `concurso123` | Revisar local switching |
| `Secundaria-Wifi` | 20 | `vlan20_secundaria` | `true` | 1 | `concurso123` | Revisar local switching |
| `Invitados-Wifi` | 30 | `vlan30_invitados` | `true` | 1 | `concurso123` | Revisar local switching |
| `Preparatoria-Wifi` | 40 | `vlan40_preparatoria` | `true` | 1 | `concurso123` | Revisar local switching |
| `Entrenadores-Wifi` | 50 | `vlan50_entrenadores` | `true` | 1 | `concurso123` | Revisar local switching |
| `Prensa-Wifi` | 60 | `vlan60_prensa` | `true` | 1 | `concurso123` | Revisar local switching |
| `Jueces-Wifi` | 80 | `vlan80_jueces` | `true` | 1 | `concurso123` | Revisar local switching |

Antes `Primaria-Wifi` aparecia con switch mode `0`; ahora todas aparecen en
`1`. Por el comportamiento observado, trata ese modo como switching local /
FlexConnect local switching. Si las WLAN trabajan asi, los puertos AP deben ser
trunk. Si los puertos AP quedan access VLAN 70, el cliente cae en GestionTI.

## AP Group

El grupo `default-group` incluye:

- `Secundaria-Wifi`
- `Invitados-Wifi`
- `Preparatoria-Wifi`
- `Entrenadores-Wifi`
- `Prensa-Wifi`
- `Jueces-Wifi`
- `Primaria-Wifi`

Por eso el problema no parece ser que las WLAN no esten asignadas al AP group.

## APs Y Puertos De Switch

Todos los APs tienen `PRIMARY_AC 172.23.45.131`. Tambien todos sus puertos de
switch estan como access VLAN 70:

| AP | Camino fisico | Puerto switch | Modo |
| --- | --- | --- | --- |
| `CIT-PBAP-02` | `1ERA.1-41:01-02:Jack1` -> `PP-1ERA.1-41:PunchDown1` | `SW-1ERA.1-40 Fa0/1` | access VLAN 70 |
| `CIT-PBAP-01` | `1ERA.1-41:01-02:Jack2` -> `PP-1ERA.1-41:PunchDown2` | `SW-1ERA.1-40 Fa0/2` | access VLAN 70 |
| `CIT-02AP-01` | `2ERA.1-43:01-04:Jack1` -> `PP-2ERA.1-43:PunchDown1` | `SW-2ERA.1-42 Fa0/1` | access VLAN 70 |
| `CIT-03AP-01` | `3ERA.1-43:01-03:Jack1` -> `PP-3ERA.1-43:PunchDown1` | `SW-3ERA.1-42 Fa0/1` | access VLAN 70 |
| `CIT-03AP-02` | `3ERA.1-43:01-03:Jack2` -> `PP-3ERA.1-43:PunchDown2` | `SW-3ERA.1-42 Fa0/2` | access VLAN 70 |
| `CIT-03AP-03` | `3ERA.1-43:01-03:Jack3` -> `PP-3ERA.1-43:PunchDown3` | `SW-3ERA.1-42 Fa0/3` | access VLAN 70 |
| `HUM-02AP-05` | `2ERB.1-41:17:Jack1` -> `PP-2ERB.1-41:PunchDown17` | `SW-2ERB.1-40 Fa0/17` | access VLAN 70 |
| `HUM-PBAP-01` | `1ERB.1-43:01:Jack1` -> `PP-1ERB.1-43:PunchDown1` | `SW-1ERB.1-42 Fa0/1` | access VLAN 70 |
| `HUM-PBAP-02` | `1ERB.1-43:02:Jack1` -> `PP-1ERB.1-43:PunchDown2` | `SW-1ERB.1-42 Fa0/2` | access VLAN 70 |
| `HUM-02AP-01` | `2ERBA.1-43:01:Jack1` -> `PP-2ERBA.1-43:PunchDown1` | `SW-2ERBA.1-42 Fa0/1` | access VLAN 70 |
| `HUM-02AP-02` | `2ERBA.1-43:02:Jack1` -> `PP-2ERBA.1-43:PunchDown2` | `SW-2ERBA.1-42 Fa0/2` | access VLAN 70 |
| `HUM-02AP-03` | `2ERBA.1-43:03:Jack1` -> `PP-2ERBA.1-43:PunchDown3` | `SW-2ERBA.1-42 Fa0/3` | access VLAN 70 |
| `HUM-02AP-04` | `2ERBA.1-43:04:Jack1` -> `PP-2ERBA.1-43:PunchDown4` | `SW-2ERBA.1-42 Fa0/4` | access VLAN 70 |
| `HUM-PBAP-03` | `2ERBL.1-43:01:Jack1` -> `PP-2ERBL.1-43:PunchDown1` | `SW-2ERBL.1-42 Fa0/1` | access VLAN 70 |
| `ING-04AP-01` | `4ERC.1-43:01:Jack1` -> `PP-4ERC.1-43:PunchDown1` | `SW-4ERC.1-42 Fa0/1` | access VLAN 70 |
| `ING-PBAP-01` | `1ERC.1-41:01:Jack1` -> `PP-1ERC.1-41:PunchDown1` | `SW-1ERC.1-40 Fa0/1` | access VLAN 70 |

Esta tabla es el dato decisivo. Access VLAN 70 esta bien para APs ligeros con
switching centralizado. Pero si la WLAN hace local switching, esos puertos
deben transportar las VLAN de usuarios.

## Trunks Principales

El trunk del WLC esta bien:

```ios
interface GigabitEthernet1/0/2
 description TRUNK_hacia_WLC-1ERA.1-35
 switchport access vlan 70
 switchport trunk native vlan 70
 switchport trunk allowed vlan 10,20,30,40,50,60,70,80
 switchport mode trunk
```

El router tambien esta conectado por trunk:

```ios
interface GigabitEthernet1/0/4
 description TRUNK_hacia_RT-1ERA.1-45
 switchport trunk allowed vlan 10,20,30,40,50,60,70,80
 switchport mode trunk
```

Y los trunks de backbone auditados permiten las VLAN `10,20,30,40,50,60,70,80`.
No veo un trunk principal cortando VLAN 10 o VLAN 70.

## Router-On-A-Stick

El router `RT-1ERA.1-45` tiene subinterfaces correctas:

| VLAN | Gateway | Helper DHCP |
| ---: | --- | --- |
| 10 | `172.23.40.1/23` | `172.23.45.130` |
| 20 | `172.23.42.1/24` | `172.23.45.130` |
| 30 | `172.23.43.1/24` | `172.23.45.130` |
| 40 | `172.23.44.1/24` | `172.23.45.130` |
| 50 | `172.23.45.1/26` | `172.23.45.130` |
| 60 | `172.23.45.65/26` | `172.23.45.130` |
| 70 | `172.23.45.129/26` | sin helper, correcto para gestion |
| 80 | `172.23.45.193/27` | `172.23.45.130` |

Si el cliente realmente entrara a VLAN 10, deberia poder llegar a
`172.23.40.1`. Como no llega, el problema esta antes del router: en el camino
wireless/VLAN.

## DHCP Del Servidor

Servidor: `DHCP-1ERA.1-39`.

| Pool | Red | Rango | Gateway | WLC Address | Leases |
| --- | --- | --- | --- | --- | ---: |
| `serverPool` | `192.0.2.0/24` | `192.0.2.10-192.0.2.72` | `0.0.0.0` | `0.0.0.0` | 0 |
| `VLAN_GestionTI` | `172.23.45.128/26` | `172.23.45.154-172.23.45.190` | `172.23.45.129` | `172.23.45.131` | 37 |
| `VLAN_Jueces` | `172.23.45.192/27` | `172.23.45.200-172.23.45.222` | `172.23.45.193` | `172.23.45.131` | 0 |
| `VLAN_Prensa` | `172.23.45.64/26` | `172.23.45.67-172.23.45.127` | `172.23.45.65` | `172.23.45.131` | 0 |
| `VLAN_Entrenadores` | `172.23.45.0/26` | `172.23.45.3-172.23.45.63` | `172.23.45.1` | `172.23.45.131` | 0 |
| `VLAN_Preparatoria` | `172.23.44.0/24` | `172.23.44.3-172.23.44.255` | `172.23.44.1` | `172.23.45.131` | 0 |
| `VLAN_Invitados` | `172.23.43.0/24` | `172.23.43.3-172.23.43.255` | `172.23.43.1` | `172.23.45.131` | 0 |
| `VLAN_Secundaria` | `172.23.42.0/24` | `172.23.42.3-172.23.42.255` | `172.23.42.1` | `172.23.45.131` | 0 |
| `VLAN10_Primaria` | `172.23.40.0/23` | `172.23.40.3-172.23.41.255` | `172.23.40.1` | `172.23.45.131` | 0 |

Los pools por VLAN estan bien. El problema es que los clientes no estan llegando
a esos pools. `VLAN_GestionTI` ya tiene 37 leases, que coincide con su maximo.
Eso explica `DHCP request failed` para nuevos clientes que siguen cayendo en
GestionTI.

## Clientes Wireless En El XML

| Estado | Cantidad |
| --- | ---: |
| IP correcta | 1 |
| IP de GestionTI | 21 |
| Sin IP | 2 |
| APIPA | 2 |

Detalle:

| Cliente | SSID | IP actual | Esperado | Estado |
| --- | --- | --- | --- | --- |
| `PartPri3` | `Primaria-Wifi` | `172.23.40.10/23` | `172.23.40.0/23` | OK, parece estatica |
| `PartPri2` | `Primaria-Wifi` | `172.23.45.179/26` | `172.23.40.0/23` | GestionTI |
| `PartPri1` | `Primaria-Wifi` | sin IP | `172.23.40.0/23` | DHCP fail |
| `Laptop3` | `Secundaria-Wifi` | `172.23.45.164/26` | `172.23.42.0/24` | GestionTI |
| `Laptop4` | `Secundaria-Wifi` | `172.23.45.189/26` | `172.23.42.0/24` | GestionTI |
| `1208` | `Secundaria-Wifi` | `172.23.45.171/26` | `172.23.42.0/24` | GestionTI |
| `Laptop6` | `Secundaria-Wifi` | `172.23.45.170/26` | `172.23.42.0/24` | GestionTI |
| `Laptop7` | `Secundaria-Wifi` | `172.23.45.183/26` | `172.23.42.0/24` | GestionTI |
| `PC10` | `Preparatoria-Wifi` | `172.23.45.188/26` | `172.23.44.0/24` | GestionTI |
| `PC11` | `Preparatoria-Wifi` | `172.23.45.185/26` | `172.23.44.0/24` | GestionTI |
| `PC12` | `Preparatoria-Wifi` | `172.23.45.184/26` | `172.23.44.0/24` | GestionTI |
| `1101` | `Preparatoria-Wifi` | `172.23.45.178/26` | `172.23.44.0/24` | GestionTI |
| `PC24` | `Preparatoria-Wifi` | `172.23.45.190/26` | `172.23.44.0/24` | GestionTI |
| `PC25` | `Preparatoria-Wifi` | `172.23.45.176/26` | `172.23.44.0/24` | GestionTI |
| `PC26` | `Preparatoria-Wifi` | `169.254.87.229/16` | `172.23.44.0/24` | APIPA |
| `Smartphone0` | `Prensa-Wifi` | `172.23.45.174/26` | `172.23.45.64/26` | GestionTI |
| `Smartphone2` | `Prensa-Wifi` | `172.23.45.164/26` | `172.23.45.64/26` | GestionTI |
| `Juez01` | `Jueces-Wifi` | `169.254.61.168/16` | `172.23.45.192/27` | APIPA |
| `Juez02` | `Jueces-Wifi` | `172.23.45.181/26` | `172.23.45.192/27` | GestionTI |
| `Invitado1` | `Invitados-Wifi` | `172.23.45.177/26` | `172.23.43.0/24` | GestionTI |
| `Invitado3` | `Invitados-Wifi` | `172.23.45.159/26` | `172.23.43.0/24` | GestionTI |
| `Invitado5` | `Invitados-Wifi` | `172.23.45.173/26` | `172.23.43.0/24` | GestionTI |
| `Invitado2` | `Invitados-Wifi` | `172.23.45.180/26` | `172.23.43.0/24` | GestionTI |
| `Invitado4` | `Invitados-Wifi` | `172.23.45.175/26` | `172.23.43.0/24` | GestionTI |
| `Entr2-i` | `Entrenadores-Wifi` | sin IP | `172.23.45.0/26` | DHCP fail |
| `Entr1-i` | `Entrenadores-Wifi` | `172.23.45.182/26` | `172.23.45.0/26` | GestionTI |

`PartPri3` tiene una IP correcta, pero por el contexto parece una IP estatica de
prueba (`172.23.40.10`), no una concesion DHCP del pool `VLAN10_Primaria`,
porque ese pool tiene 0 leases.

## Causa Mas Probable

La causa mas probable es:

1. WLANs con local switching/FlexConnect activo (`WLAN_SWITCH_MODE = 1`).
2. APs conectados a puertos access VLAN 70.
3. Cliente wireless sale por el AP sin etiqueta de VLAN de usuario.
4. El switch recibe ese trafico como VLAN 70.
5. El cliente intenta DHCP en GestionTI, no en su VLAN.
6. Como `VLAN_GestionTI` esta llena, algunos clientes ya fallan DHCP.

Esta explicacion tambien coincide con tu prueba: una IP estatica en Primaria no
puede hacer ping a `172.23.40.1`, porque realmente el trafico no esta entrando a
VLAN 10.

## Correccion Recomendada

### Opcion A: Recomendada

Dejar las WLAN en switching centralizado y mantener APs como access VLAN 70.

En el WLC, para cada WLAN:

1. `WLANs`
2. Abrir la WLAN, por ejemplo `Primaria-Wifi`
3. Revisar `Advanced` o `FlexConnect`
4. Desactivar `FlexConnect Local Switching`
5. Guardar/aplicar
6. Repetir para las 7 WLANs

Despues reinicia/renueva un solo cliente:

1. Conectar `PartPri3` a `Primaria-Wifi`
2. Desktop > IP Configuration > DHCP
3. Debe recibir `172.23.40.x`
4. El pool `VLAN10_Primaria` debe empezar a mostrar leases

### Opcion B: Si Packet Tracer Te Obliga A Local Switching

Convierte el puerto del AP de prueba a trunk. Hazlo solo con un AP primero.

Ejemplo para `CIT-03AP-01`, conectado a `SW-3ERA.1-42 Fa0/1`:

```ios
enable
configure terminal
interface fa0/1
 description LWAP_TRUNK_PRUEBA
 switchport mode trunk
 switchport trunk native vlan 70
 switchport trunk allowed vlan 10,20,30,40,50,60,70,80
 spanning-tree portfast trunk
end
write memory
```

Luego conecta una laptop a `Primaria-Wifi`, renueva DHCP y prueba:

```text
IP esperada: 172.23.40.x
Gateway esperado: 172.23.40.1
ping 172.23.40.1
```

Si funciona, entonces aplica la misma logica a los puertos de los APs que van a
transportar clientes con local switching.

## No Perder Tiempo En Esto

- No cambies los pools DHCP de las VLAN de usuarios; se ven correctos.
- No cambies el `ip helper-address`; se ve correcto.
- No actives Dynamic AP Management en interfaces de usuario; ya esta apagado y
  asi debe quedarse.
- No cambies el trunk WLC-switch; se ve correcto.
- No persigas el ping desde switches sin SVI de administracion; eso pertenece a
  Telnet/gestion, no al DHCP wireless.

## Siguiente Prueba Decisiva

Haz una sola prueba:

1. En el WLC, apaga `FlexConnect Local Switching` en `Primaria-Wifi`.
2. Deja `CIT-03AP-01` en access VLAN 70.
3. Conecta `PartPri3` por DHCP.
4. Si no funciona, cambia `SW-3ERA.1-42 Fa0/1` a trunk como AP piloto.
5. Vuelve a renovar DHCP.

Resultado esperado:

- Si con local switching apagado funciona, deja todos los APs access VLAN 70.
- Si solo funciona con el puerto AP en trunk, entonces tu WLC/PT esta trabajando
  en local switching y necesitas trunk en los puertos AP.
