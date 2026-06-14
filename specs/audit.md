# Auditoria Detallada Del XML - Fase 3

Archivo auditado: `data/output/Reto Diseño de Redes Fase 3 avance 2.xml`
Archivo Packet Tracer asociado: `data/input/Reto Diseño de Redes Fase 3 avance 2.pkt`
Fecha de auditoria: 2026-06-14

Metodo: lectura estructurada del XML con foco en `DEVICE`, `RUNNINGCONFIG`, `STARTUPCONFIG`, `VLANS`, `VTP`, `DHCP_SERVERS`, WLC/CAPWAP, WLANs, APs, perfiles wireless de clientes, leases DHCP y enlaces fisicos.

## Resumen Ejecutivo

El avance nuevo ya muestra que la parte inalambrica fue conectada mejor: el WLC tiene WLANs para VLAN 10,20,30,40,50,60 y 80, la clave de `Primaria-Wifi` ya fue corregida a `concurso123`, y los 16 AP ligeros ya tienen controlador primario `172.23.45.131`. El WLC tambien muestra 16 APs en su bloque de CAPWAP.

El problema principal ahora es DHCP en wireless: los clientes inalambricos si estan recibiendo IP, pero casi todos reciben direccion del `serverPool` generico, no del pool que corresponde a su SSID/VLAN. Ejemplo: clientes de `Primaria-Wifi` deberian recibir `172.23.40.x/23`, pero estan recibiendo `172.23.45.159/26`, `172.23.45.172/26`, etc. Eso indica que el trafico wireless esta cayendo en la VLAN de gestion/native o en el pool por defecto, no en la VLAN del SSID.

El core sigue bien: router-on-a-stick, helpers a `172.23.45.130`, ACL de Invitados y VLANs/trunks principales permanecen configurados. La pasada exhaustiva agrega una senal importante: el controlador usado es `WLC-PT`, no un 2504/3504, y el XML trae `WLC_INTERFACES` vacio con `INTERFACE_NAME` vacio en todas las WLAN. Eso explica por que, aunque el switch tenga trunk correcto, las WLAN pueden seguir saliendo por la VLAN native/gestion.

Estado general estimado:

| Area | Avance | Veredicto |
| --- | ---: | --- |
| Topologia fisica y objetos TIA/EIA | 85% | Parcialmente listo |
| VLSM y VLAN base | 90% | Bien encaminado |
| Router-on-a-stick | 90% | Casi listo |
| DHCP como servicio | 70% | Funciona, pero wireless usa pool incorrecto |
| VTP | 72% | Parcial, validar version/propagacion |
| Switching backbone/acceso | 78% | Parcialmente listo |
| Wireless con WLC/LWAP | 68% | APs/WLANs avanzaron; falta VLAN correcta por SSID |
| Seguridad por ACL | 70% | ACL base presente |
| Administracion Telnet | 10% | Pendiente |
| Endpoints y pruebas | 45% | Wireless conectado, IPs incorrectas |
| Export de configuraciones | 0% | Pendiente |

## Hallazgo Critico: DHCP Wireless En Pool Incorrecto

Veredicto: FAIL funcional para 10.2.

El XML muestra 26 clientes conectados a SSID wireless con IP en su perfil actual. Ninguno esta recibiendo una IP dentro de la red esperada para su SSID:

| Estado | Cantidad |
| --- | ---: |
| Clientes wireless con IP correcta segun SSID | 0 |
| Clientes wireless con IP de pool incorrecto | 24 |
| Clientes wireless en APIPA | 2 |

Patron observado:

- Muchos clientes wireless reciben `172.23.45.154-190/26`.
- Esa red corresponde a GestionTI / VLAN 70, no a Primaria, Secundaria, Invitados, Preparatoria, Prensa o Jueces.
- En el servidor DHCP hay 41 leases dentro del `serverPool` generico.
- `serverPool` esta configurado con gateway `0.0.0.0`, inicio `172.23.45.128` y fin `172.23.47.127`.

Interpretacion:

El DHCP no esta "inventando" IPs: esta usando el `serverPool` generico porque las solicitudes wireless estan llegando como si fueran de la red de gestion/native, o porque ese pool por defecto esta capturando solicitudes que no deberia. Mientras esto siga asi, el Paso 10.2 puede mostrar conexion Wi-Fi, pero no conectividad correcta por VLAN.

## Clientes Wireless Detectados

| Cliente | SSID | IP actual | Red esperada | Estado |
| --- | --- | --- | --- | --- |
| `PartPri3` | Primaria-Wifi | `172.23.45.159/26` | `172.23.40.0/23` | Pool incorrecto |
| `PartPri2` | Primaria-Wifi | `172.23.45.172/26` | `172.23.40.0/23` | Pool incorrecto |
| `PartPri1` | Primaria-Wifi | `172.23.45.169/26` | `172.23.40.0/23` | Pool incorrecto |
| `Laptop3` | Secundaria-Wifi | `172.23.45.178/26` | `172.23.42.0/24` | Pool incorrecto |
| `Laptop4` | Secundaria-Wifi | `172.23.45.177/26` | `172.23.42.0/24` | Pool incorrecto |
| `1208` | Secundaria-Wifi | `172.23.45.187/26` | `172.23.42.0/24` | Pool incorrecto |
| `Laptop6` | Secundaria-Wifi | `172.23.45.188/26` | `172.23.42.0/24` | Pool incorrecto |
| `Laptop7` | Secundaria-Wifi | `172.23.45.189/26` | `172.23.42.0/24` | Pool incorrecto |
| `PC10` | Preparatoria-Wifi | `172.23.45.190/26` | `172.23.44.0/24` | Pool incorrecto |
| `PC11` | Preparatoria-Wifi | `169.254.214.45/16` | `172.23.44.0/24` | APIPA |
| `PC12` | Preparatoria-Wifi | `169.254.48.6/16` | `172.23.44.0/24` | APIPA |
| `1101` | Preparatoria-Wifi | `172.23.45.185/26` | `172.23.44.0/24` | Pool incorrecto |
| `PC24` | Preparatoria-Wifi | `172.23.45.160/26` | `172.23.44.0/24` | Pool incorrecto |
| `PC25` | Preparatoria-Wifi | `172.23.45.182/26` | `172.23.44.0/24` | Pool incorrecto |
| `PC26` | Preparatoria-Wifi | `172.23.45.184/26` | `172.23.44.0/24` | Pool incorrecto |
| `Smartphone0` | Prensa-Wifi | `172.23.45.179/26` | `172.23.45.64/26` | Pool incorrecto |
| `Smartphone2` | Prensa-Wifi | `172.23.45.162/26` | `172.23.45.64/26` | Pool incorrecto |
| `Juez01` | Jueces-Wifi | `172.23.45.170/26` | `172.23.45.192/27` | Pool incorrecto |
| `Juez02` | Jueces-Wifi | `172.23.45.164/26` | `172.23.45.192/27` | Pool incorrecto |
| `Invitado1` | Invitados-Wifi | `172.23.45.180/26` | `172.23.43.0/24` | Pool incorrecto |
| `Invitado3` | Invitados-Wifi | `172.23.45.181/26` | `172.23.43.0/24` | Pool incorrecto |
| `Invitado5` | Invitados-Wifi | `172.23.45.175/26` | `172.23.43.0/24` | Pool incorrecto |
| `Invitado2` | Invitados-Wifi | `172.23.45.174/26` | `172.23.43.0/24` | Pool incorrecto |
| `Invitado4` | Invitados-Wifi | `172.23.45.176/26` | `172.23.43.0/24` | Pool incorrecto |
| `Entr2-i` | Entrenadores-Wifi | `172.23.45.158/26` | `172.23.45.0/26` | Pool incorrecto |
| `Entr1-i` | Entrenadores-Wifi | `172.23.45.157/26` | `172.23.45.0/26` | Pool incorrecto |

## Causa Probable

Hay tres senales combinadas:

1. En el XML auditado, `serverPool` generico sigue activo en `DHCP-1ERA.1-39`.
   - Tiene red `172.23.45.128`.
   - Mascara `255.255.255.192`.
   - Gateway `0.0.0.0`.
   - Rango enorme `172.23.45.128 - 172.23.47.127`.
   - Esta entregando 41 leases, incluyendo APs y muchos clientes wireless.
   - Si ya lo cambiaste despues de exportar este XML, hay que generar un XML nuevo para confirmar el estado actual.

2. Los SSID no estan separando trafico hacia sus VLAN esperadas.
   - El WLC tiene VLAN ID por WLAN, pero `WLC_INTERFACES` sigue vacio.
   - Todas las WLAN tienen `INTERFACE_NAME` vacio.
   - El WLC es modelo `WLC-PT`, que en esta interfaz no muestra las pantallas de interfaces dinamicas/trunk que normalmente se usan para mapear WLAN -> VLAN.
   - Tu salida de `show interfaces trunk` en `SW-1ERA.1-42` ya muestra `Gi1/0/2` en trunk y permitiendo VLAN 10,20,30,40,50,60,70,80; por eso el bloqueo principal ya apunta mas al WLC que al switch.

3. Si despues de cambiar `serverPool` un cliente como `PartPri1` sigue tomando `172.23.45.x`, entonces ya no parece un problema de `serverPool`.
   - Puede estar conservando una concesion vieja hasta renovar/desconectar bien.
   - O el WLC esta mandando el trafico de clientes como VLAN 70/native, donde cae en GestionTI.
   - En ese caso, cambiar pools no arregla la causa; hay que corregir el modelo/configuracion del WLC.

## Busqueda Exhaustiva Adicional

### Modelo Del WLC

El XML identifica el controlador como:

```xml
<TYPE customModel="" model="WLC-PT">WirelessLanController</TYPE>
```

No aparece como `2504` ni como `3504`. Los textos `2504`/`3504` aparecen en el XML por coordenadas/valores internos, no como modelo del WLC.

Veredicto: si Packet Tracer te deja cambiarlo, conviene usar un WLC 2504 o 3504 para este reto. El `WLC-PT` que tienes no necesariamente esta "mal" para una red simple, pero por las opciones que muestras le falta justo la parte que necesitamos: interfaces dinamicas o mapeo claro de WLAN a VLAN.

### Campo `WLC Address` En DHCP

Los pools DHCP tienen `WLC_ADDRESS 0.0.0.0`. Ese campo ayuda a que los AP descubran el controlador, parecido a una opcion de descubrimiento, pero no decide que pool reciben los clientes finales.

Conclusion:

- Si tus APs ya aparecen asociados al WLC y tienen `PRIMARY_AC 172.23.45.131`, entonces `WLC Address` no es la causa de que `PartPri1` reciba `172.23.45.x`.
- Aun asi, es recomendable poner `172.23.45.131` como `WLC Address` en el pool de GestionTI/VLAN 70, especialmente si los AP reciben IP por DHCP.
- No hace falta configurar DHCP en el WLC para los clientes si ya existe `DHCP-1ERA.1-39`; tener dos DHCP activos puede confundirte mas.

### Otros Hallazgos

- Existe `SW-1ERA.1-37` en el XML y aparece como switch sin configuracion util. Si forma parte real de la topologia, falta configurarlo; si es un objeto sobrante, no bloquea el avance.
- No se detectan `ip default-gateway`, `enable secret` ni `transport input telnet` en las configuraciones exportadas. La administracion Telnet sigue pendiente.
- Ningun switch muestra SVI de administracion VLAN 70 en el XML. Esto tambien pertenece al bloque de administracion, no al problema DHCP wireless.
- VTP sigue siendo aceptable si el servidor queda en version 2 y los clientes aprenden VLAN 10-80; no te atasques en forzar version 2 en cada cliente de Packet Tracer.

## Correccion Recomendada Antes De Seguir 10.2

### 1. Revisar Si Puedes Cambiar El WLC

Antes de renovar mas clientes, revisa en Packet Tracer si puedes reemplazar `WLC-PT` por un WLC 2504 o 3504.

Si usas 2504/3504, busca una seccion parecida a interfaces/dynamic interfaces y crea:

| Interface | VLAN | Gateway esperado |
| --- | ---: | --- |
| `primaria` | 10 | `172.23.40.1` |
| `secundaria` | 20 | `172.23.42.1` |
| `invitados` | 30 | `172.23.43.1` |
| `preparatoria` | 40 | `172.23.44.1` |
| `entrenadores` | 50 | `172.23.45.1` |
| `prensa` | 60 | `172.23.45.65` |
| `jueces` | 80 | `172.23.45.193` |

Luego asigna cada WLAN a su interfaz/VLAN correspondiente.

### 2. Corregir DHCP Sin Crear Otro DHCP En El WLC

En `DHCP-1ERA.1-39` > Services > DHCP:

- Eliminar o desactivar `serverPool`.
- Si Packet Tracer no deja eliminarlo, cambiarlo a algo inutil/no usado o reducirlo para que no entregue direcciones.
- En el pool de GestionTI/VLAN 70, poner `WLC Address` = `172.23.45.131`.
- Mantener activos los pools por VLAN:
  - `VLAN10_Primaria`
  - `VLAN_Secundaria`
  - `VLAN_Invitados`
  - `VLAN_Preparatoria`
  - `VLAN_Entrenadores`
  - `VLAN_Prensa`
  - `VLAN_GestionTI`
  - `VLAN_Jueces`

No borres los pools VLAN. Tampoco actives un segundo DHCP para clientes dentro del WLC salvo que no haya otra salida; para este diseno, el DHCP principal debe seguir siendo `172.23.45.130`.

### 3. Verificar trunk hacia WLC

En `SW-1ERA.1-42`:

```ios
show interfaces trunk
show running-config interface gigabitEthernet1/0/2
```

El puerto hacia el WLC debe funcionar como trunk y permitir las VLAN:

```ios
configure terminal
interface gigabitEthernet1/0/2
 description TRUNK_hacia_WLC-1ERA.1-35
 switchport mode trunk
 switchport trunk native vlan 70
 switchport trunk allowed vlan 10,20,30,40,50,60,70,80
end
write memory
```

Tu salida actual ya cumple lo importante: `Gi1/0/2` esta trunking y permite VLAN 10,20,30,40,50,60,70,80. La native VLAN 70 tiene sentido porque el WLC/APs viven en gestion.

### 4. Verificar APs

Los APs deben quedarse en VLAN 70 para gestion/CAPWAP. En los puertos donde conectan APs:

```ios
configure terminal
interface Fa0/X
 switchport mode access
 switchport access vlan 70
 spanning-tree portfast
end
write memory
```

### 5. Verificar WLC

En `WLC-1ERA.1-35`:

- Management: `172.23.45.131/26`, gateway `172.23.45.129`.
- Wireless LANs:
  - Primaria-Wifi -> VLAN 10
  - Secundaria-Wifi -> VLAN 20
  - Invitados-Wifi -> VLAN 30
  - Preparatoria-Wifi -> VLAN 40
  - Entrenadores-Wifi -> VLAN 50
  - Prensa-Wifi -> VLAN 60
  - Jueces-Wifi -> VLAN 80
- AP Groups: confirmar que las WLAN esten en `default-group`.
- Si el WLC solo muestra `Settings`, `Wireless LANs`, `AP Groups`, `DHCP`, `GigabitEthernet0` y `Management`, y no permite interfaces dinamicas, considera cambiar a 2504/3504.

### 6. Renovar clientes

Despues de corregir DHCP/trunk, en cada cliente wireless:

- Desktop > IP Configuration.
- Cambiar a Static y regresar a DHCP, o usar DHCP/Renew si aparece.
- Desconectar y reconectar al SSID si conserva la IP vieja.

## Resultado Esperado Por SSID

| SSID | VLAN | IP esperada |
| --- | ---: | --- |
| Primaria-Wifi | 10 | `172.23.40.3 - 172.23.41.255` |
| Secundaria-Wifi | 20 | `172.23.42.3 - 172.23.42.255` |
| Invitados-Wifi | 30 | `172.23.43.3 - 172.23.43.255` |
| Preparatoria-Wifi | 40 | `172.23.44.3 - 172.23.44.255` |
| Entrenadores-Wifi | 50 | `172.23.45.3 - 172.23.45.63` |
| Prensa-Wifi | 60 | `172.23.45.67 - 172.23.45.127` |
| Jueces-Wifi | 80 | `172.23.45.200 - 172.23.45.222` |

## WLC Y APs

Veredicto: PASS parcial en asociacion de APs, FAIL parcial en separacion por VLAN.

Evidencia positiva:

- WLC `WLC-1ERA.1-35` mantiene IP `172.23.45.131/26`.
- WLANs 10,20,30,40,50,60 y 80 existen y estan habilitadas.
- `Primaria-Wifi` ya tiene clave `concurso123`.
- Los 16 APs tienen `PRIMARY_AC 172.23.45.131`.
- El WLC muestra 16 entradas de AP.

Pendiente:

- `WLC_INTERFACES` sigue vacio; esto coincide con la limitacion visible del modelo `WLC-PT`.
- Confirmar o cambiar el WLC a un modelo que permita mapear cada WLAN a una interfaz/VLAN real.
- Los clientes wireless todavia no reciben IP de la VLAN correcta.

## Core De Red

Veredicto: PASS parcial alto.

El core se mantiene correcto:

- Router `RT-1ERA.1-45` con subinterfaces dot1Q para VLAN 10-80.
- Helpers DHCP hacia `172.23.45.130`.
- VLAN 70 sin helper.
- ACL `ACL_INVITADOS_IN` aplicada en `GigabitEthernet0/0/0.30`.
- Servidor local `ING-04SRV-01` con `172.23.45.194/27`.
- DHCP principal `DHCP-1ERA.1-39` con `172.23.45.130/26`.

## DHCP

Veredicto: FAIL parcial en el XML auditado por `serverPool` y por trafico wireless cayendo fuera de su VLAN.

Leases detectados:

| Pool | Leases |
| --- | ---: |
| `serverPool` | 41 |
| `VLAN10_Primaria` | 0 |
| `VLAN_Secundaria` | 0 |
| `VLAN_Invitados` | 0 |
| `VLAN_Preparatoria` | 18 |
| `VLAN_Entrenadores` | 2 |
| `VLAN_Prensa` | 0 |
| `VLAN_GestionTI` | 0 |
| `VLAN_Jueces` | 0 |

Lectura:

- Preparatoria cableada parece estar recibiendo DHCP correctamente por VLAN 40.
- Entrenadores cableados parecen recibir DHCP correctamente por VLAN 50.
- Wireless esta cayendo en `serverPool` en este XML.
- Si despues del export cambiaste `serverPool` y `PartPri1` sigue en `172.23.45.x`, genera un XML nuevo; eso confirmaria que el trafico del SSID esta llegando por VLAN 70/native o que el cliente conserva una concesion vieja.

## Administracion Telnet

Veredicto: Pendiente.

No fue el foco del nuevo avance. Aun conviene validar:

- `enable secret OMIenable2026`.
- `line vty` con password y `transport input telnet`.
- SVIs VLAN 70 en switches.

## Checklist Actual

| Criterio | Estado | Evidencia/pendiente |
| --- | --- | --- |
| Router-on-a-stick | PASS | VLAN 10-80 presentes |
| DHCP helper | PASS | Apunta a `172.23.45.130` |
| ACL Invitados | PASS parcial | Existe y esta aplicada; faltan pruebas |
| WLC gestion | PASS | `172.23.45.131/26` |
| Modelo WLC | FAIL parcial | El XML muestra `WLC-PT`; para este reto conviene 2504/3504 si esta disponible |
| WLANs 10-80 | PASS | Ya existe Jueces-Wifi |
| APs con controlador | PASS parcial | `PRIMARY_AC 172.23.45.131` |
| Clientes wireless conectados | PASS parcial | Tienen SSID e IP |
| Clientes wireless en VLAN correcta | FAIL | 24 pool incorrecto, 2 APIPA |
| `serverPool` generico | FAIL en XML | Esta entregando 41 leases; requiere nuevo XML si ya lo cambiaste |
| `WLC Address` en DHCP | Advertencia | Esta en `0.0.0.0`; poner `172.23.45.131` ayuda a descubrimiento AP, no a pools de clientes |
| Trunk WLC-switch | PASS parcial | Tu `show interfaces trunk` muestra `Gi1/0/2` trunking con VLAN 10-80 |
| Telnet gestion | Pendiente | Falta validar/configurar |

## Siguiente Paso

Vas en el Paso 10.2, pero antes de darlo por bueno corrige el WLC/VLAN wireless:

1. Si Packet Tracer ofrece WLC 2504 o 3504, cambia el `WLC-PT` por ese modelo.
2. Configura management del WLC: `172.23.45.131/26`, gateway `172.23.45.129`.
3. Crea/mapea interfaces o WLANs para VLAN 10,20,30,40,50,60 y 80.
4. En el servidor DHCP, deja los pools VLAN y pon `WLC Address 172.23.45.131` en el pool de GestionTI/VLAN 70.
5. No actives DHCP para clientes en el WLC si el servidor `172.23.45.130` ya esta funcionando.
6. Renueva un solo cliente: `PartPri1`.
7. Si `PartPri1` obtiene `172.23.40.x`, ya puedes repetir por SSID.

Si con WLC 2504/3504 y VLAN mapping correcto `PartPri1` sigue tomando `172.23.45.x`, entonces exporta otro XML; ahi ya se revisa si quedo una concesion vieja, un pool residual o un mapeo que Packet Tracer no guardo.
