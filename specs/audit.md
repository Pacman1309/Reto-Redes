# Auditoria Detallada Del XML - Fase 3

Archivo auditado: `data/output/Reto-Redes-actual.xml`  
Archivo anterior de referencia: `data/output/Reto-Redes.xml`  
Fecha de auditoria: 2026-06-13  
Revision complementaria: `data/output/...Fase 3 en proceso.xml`, 2026-06-14

Metodo: parseo XML estructurado con foco en `DEVICE`, `RUNNINGCONFIG`, `VLANS`, `VTP`, `VTY/Telnet`, `DHCP_SERVERS`, endpoints, WLC/CAPWAP, WLANs y `LINK`.

## Resumen Ejecutivo

El archivo actual ya incluye un avance importante frente al XML anterior: los AP autonomos fueron reemplazados por AP ligeros 3702i y se agrego/configuro un WLC con IP de gestion en la VLAN 70. Tambien se conecto el WLC al switch principal `SW-1ERA.1-42` mediante un puerto access en VLAN 70.

El core de capa 3 sigue practicamente igual: el router tiene subinterfaces dot1Q para VLAN 10-80 y el switch principal conserva las VLAN base. El XML tambien trae bloques internos de VTP, pero sin dominio ni comandos `vtp` visibles en las running-configs; por eso todavia no hay propagacion controlada de VLANs. El punto critico es que la configuracion logica todavia no esta distribuida al backbone, switches de acceso, LWAPs y endpoints. En otras palabras: ya se ve mas como una arquitectura centralizada con WLC, pero aun no esta operativa de punta a punta.

Estado general estimado:

| Area | Avance | Veredicto |
| --- | ---: | --- |
| Topologia fisica y objetos TIA/EIA | 78% | Parcialmente listo |
| VLSM y VLAN base | 80% | Parcialmente listo |
| VTP | 10% | Campos detectados, sin dominio/configuracion util |
| Router-on-a-stick | 70% | Funcional en core, requiere ajustes |
| DHCP como servicio | 60% | Pools creados, relay incorrecto |
| Switching de distribucion/acceso | 25% | Falta VTP, propagacion VLAN/trunks |
| Wireless con WLC/LWAP | 45% | WLC avanzado, APs no asociados |
| Seguridad por ACL | 0% | Pendiente |
| Administracion Telnet | 0% | VTY detectado, sin password ni transporte Telnet |
| Pruebas de conectividad | 0% | Pendiente |
| Export de configuraciones | 0% | Pendiente |

Conclusion: vas mejor que en el primer XML. El cambio a WLC/LWAP es correcto para una red de alta densidad, pero todavia falta completar VTP, CAPWAP, trunks/access VLANs, DHCP relay, Telnet de administracion, ACL de Invitados y pruebas ping. La maqueta fisica ya esta bastante armada; lo que falta es cerrar la operacion logica.

## Cambios Detectados Frente Al XML Anterior

| Elemento | XML anterior | XML actual | Lectura |
| --- | ---: | ---: | --- |
| Lineas XML | 186692 | 187911 | Hay cambios guardados en la topologia |
| Dispositivos/objetos | 156 | 156 | Inventario total estable |
| AP autonomos | 15 | 0 | Se sustituyeron por LWAP |
| Lightweight AP | 1 | 16 | Migracion wireless centralizada |
| WLC | 1 | 1 | Ahora aparece configurado con IP/WLANs |
| Enlaces cobre | 258 | 259 | Se agrego un enlace de cobre, consistente con el WLC |
| Enlaces fibra | 9 | 9 | Backbone fisico sin cambios |

## Inventario Detectado

El XML actual contiene 156 dispositivos/objetos.

| Tipo | Cantidad |
| --- | ---: |
| Wall Mount | 33 |
| PC | 30 |
| Switch | 21 |
| Patch Panel | 20 |
| LightWeightAccessPoint | 16 |
| Power Distribution Device | 9 |
| Laptop | 9 |
| Smartphone/PDA | 7 |
| Printer | 4 |
| Server | 3 |
| Router | 2 |
| MultiLayerSwitch | 1 |
| Wireless LAN Controller | 1 |

## Core De Red

### Router principal `RT-1ERA.1-45`

Veredicto: PASS parcial.

Evidencia:

- Existe como ISR4331.
- Tiene `RUNNINGCONFIG` y `STARTUPCONFIG`.
- Tiene subinterfaces `GigabitEthernet0/0/0.10` a `.80`.
- Tiene `encapsulation dot1Q` para VLAN 10,20,30,40,50,60,70,80.
- Las IP gateway coinciden con el VLSM aprobado dentro de `172.23.40.0/21`.

Subinterfaces esperadas/detectadas:

| VLAN | Segmento | Gateway esperado |
| ---: | --- | --- |
| 10 | Primaria | `172.23.40.1/23` |
| 20 | Secundaria | `172.23.42.1/24` |
| 30 | Invitados | `172.23.43.1/24` |
| 40 | Preparatoria | `172.23.44.1/24` |
| 50 | Entrenadores | `172.23.45.1/26` |
| 60 | Prensa | `172.23.45.65/26` |
| 70 | GestionTI | `172.23.45.129/26` |
| 80 | Jueces | `172.23.45.193/27` |

Problemas:

- Todas las subinterfaces siguen usando `ip helper-address 172.23.45.129`.
- El servidor DHCP real detectado es `DHCP-1ERA.1-39` con IP `172.23.45.130`.
- La VLAN 70 no necesita helper hacia `172.23.45.129`, porque ese valor es el gateway de la propia VLAN.
- No hay ACL aplicada a `GigabitEthernet0/0/0.30` para aislar Invitados.
- No se detecta ruta por defecto, NAT ni enlace de salida a Internet.

Accion recomendada:

- Cambiar `ip helper-address` a `172.23.45.130` en VLAN 10,20,30,40,50,60 y 80.
- Quitar helper de VLAN 70.
- Agregar `ACL_INVITADOS_IN` inbound en VLAN 30.
- Si se requiere salida a Internet, definir next-hop/ruta default/NAT segun el enlace institucional simulado.

### Switch principal `SW-1ERA.1-42`

Veredicto: PASS parcial.

Evidencia:

- Existe como `3650-24PS`.
- Tiene VLAN 10,20,30,40,50,60,70,80.
- En `VLANS` aparecen las VLAN base y en `VTP` se detecta modo numerico `0`, version `1`, dominio vacio y revision `48`.
- `Gi1/0/4` esta configurado como trunk hacia `RT-1ERA.1-45`.
- `Gi1/0/5` esta en access VLAN 70 para `DHCP-1ERA.1-39`.
- `Gi1/0/2` ahora tiene `description WLC` y esta en access VLAN 70 para el controlador.

Problemas:

- Solo se detecta trunk efectivo hacia el router.
- No se detectan comandos `vtp domain`, `vtp mode`, `vtp version` ni `vtp password` en running-config.
- El dominio VTP esta vacio, por lo que no hay una estrategia VTP documentada para propagar VLANs.
- No hay trunks configurados desde `SW-1ERA.1-42` hacia el backbone o closets.
- No hay evidencia de propagacion de VLANs a `SW-1ERA.1-43`.
- No hay SVIs de administracion ni gateway de management en los switches.
- Las lineas VTY aparecen con `login`, pero sin password ni `transport input telnet`; asi Telnet no queda utilizable.
- No hay evidencia de STP tuning, root bridge, portfast masivo ni BPDU guard.

Accion recomendada:

- Configurar como trunk el puerto que conecta `SW-1ERA.1-42` hacia `SW-1ERA.1-43`.
- Permitir VLAN 10,20,30,40,50,60,70,80 en ese enlace.
- Configurar `SW-1ERA.1-42` como VTP server: dominio `OMI-REDES`, version 2 y password `OMI2026`.
- Mantener `Gi1/0/2` del WLC en VLAN 70 si Packet Tracer esta trabajando con WLC en modo centralizado basico.
- Configurar administracion del switch en VLAN 70 y habilitar Telnet de laboratorio si la rubrica pide gestion remota.

## WLC Y Wireless

Veredicto: FAIL operativo, con avance fuerte de configuracion.

### WLC `WLC-1ERA.1-35`

Evidencia:

- Modelo detectado: `WLC-PT`.
- IP de gestion: `172.23.45.131`.
- Mascara: `255.255.255.192`.
- Gateway: `172.23.45.129`.
- Conectado al switch principal por un puerto access en VLAN 70.
- Tiene WLANs creadas y habilitadas para VLAN 10-60.

WLANs detectadas:

| WLAN | SSID | VLAN | Estado |
| --- | --- | ---: | --- |
| Primaria | `Primaria-Wifi` | 10 | Habilitada |
| Secundaria | `Secundaria-Wifi` | 20 | Habilitada |
| Invitados | `Invitados-Wifi` | 30 | Habilitada |
| Preparatoria | `Preparatoria-Wifi` | 40 | Habilitada |
| Entrenadores | `Entrenadores-Wifi` | 50 | Habilitada |
| Prensa | `Prensa-Wifi` | 60 | Habilitada |

Problemas:

- `WLC_INTERFACES` esta vacio.
- Cada WLAN tiene `INTERFACE_NAME` vacio.
- `CAPWAP_AC/APS` esta vacio: no hay APs asociados al WLC.
- `PRIMARY_AC` del WLC aparece como `0.0.0.0`.
- No existe WLAN para Jueces VLAN 80, aunque el alcance indica 10 PCs criticas inalambricas.
- La WLAN Primaria tiene clave almacenada como `consurso123`; probablemente deberia ser `concurso123`.
- La VLAN Preparatoria aparece como WLAN, aunque el diseno base indica laboratorios cableados. No es necesariamente error, pero debe justificarse o retirarse para no confundir la revision.

Accion recomendada:

- Crear interfaces dinamicas del WLC para VLAN 10,20,30,40,50,60 y 80, si Packet Tracer lo exige para mapear WLAN a VLAN.
- Asignar `INTERFACE_NAME` a cada WLAN.
- Agregar WLAN `Jueces-Wifi` en VLAN 80 si los jueces usaran Wi-Fi.
- Corregir la clave de Primaria.
- Confirmar que el puerto hacia el switch principal transporta las VLAN requeridas por el WLC segun el modo que permita Packet Tracer.

### AP ligeros

Veredicto: FAIL pendiente.

Se detectan 16 LWAP 3702i:

| AP | Observacion |
| --- | --- |
| `CIT-PBAP-02` | LWAP, sin asociacion CAPWAP |
| `CIT-PBAP-01` | LWAP, sin asociacion CAPWAP |
| `CIT-02AP-01` | LWAP, sin asociacion CAPWAP |
| `CIT-03AP-03` | LWAP, sin asociacion CAPWAP |
| `CIT-03AP-02` | LWAP, sin asociacion CAPWAP |
| `CIT-03AP-01` | LWAP, sin asociacion CAPWAP |
| `HUM-02AP-05` | LWAP, sin asociacion CAPWAP |
| `Light Weight Access Point6` | Nombre generico, debe renombrarse |
| `HUM-PBAP-02` | LWAP, sin asociacion CAPWAP |
| `HUM-02AP-01` | LWAP, sin asociacion CAPWAP |
| `HUM-02AP-02` | LWAP, sin asociacion CAPWAP |
| `HUM-02AP-03` | LWAP, sin asociacion CAPWAP |
| `HUM-02AP-04` | LWAP, sin asociacion CAPWAP |
| `HUM-PBAP-03` | LWAP, sin asociacion CAPWAP |
| `ING-04AP-01` | LWAP, sin asociacion CAPWAP |
| `ING-PBAP-01` | LWAP, sin asociacion CAPWAP |

Problemas comunes:

- `PRIMARY_AC` en los APs esta en `0.0.0.0`.
- No se detectan WLANs heredadas desde el WLC.
- No hay evidencia de IP valida de gestion en los APs.
- Los APs no aparecen dentro de la lista `APS` del WLC.

Accion recomendada:

- Renombrar `Light Weight Access Point6` con la nomenclatura del edificio/area.
- Configurar los puertos de switch donde conectan los LWAPs en VLAN 70 para gestion/CAPWAP, salvo que el escenario de Packet Tracer requiera trunk especifico.
- Habilitar DHCP o asignar IP estatica de gestion a cada AP en VLAN 70.
- Definir controlador primario `172.23.45.131` en cada LWAP o asegurar descubrimiento CAPWAP.
- Verificar que los APs aparezcan registrados en el WLC antes de probar clientes.

## VTP Y Switching De Acceso/Backbone

Veredicto: FAIL pendiente.

### VTP

Evidencia:

- El XML contiene bloques `VTP` en switches, pero el dominio aparece vacio.
- En `SW-1ERA.1-42` se observan VLAN 10-80 y revision VTP interna, pero no hay comandos `vtp` en running-config.
- En los switches de acceso solo se observan VLANs por defecto o configuracion base.

Problemas:

- No hay un dominio VTP comun.
- No hay servidor VTP definido de forma explicita.
- No hay clientes VTP documentados en los switches restantes.
- Sin trunks activos entre switches, VTP tampoco podria transportar anuncios de VLAN aunque estuviera configurado.

Accion recomendada:

- Usar `SW-1ERA.1-42` como VTP server.
- Configurar dominio `OMI-REDES`, version 2 y password `OMI2026`.
- Configurar todos los switches restantes como VTP client con el mismo dominio, version y password. En clientes, aplicar primero `vtp version 2` y al final `vtp mode client` para evitar `cannot modify version in VTP client mode`.
- Crear VLAN 10,20,30,40,50,60,70,80 solo en el servidor VTP.
- Verificar con `show vtp status`, `show vlan brief` y `show interfaces trunk`.

### Telnet Y VTY

Evidencia:

- Se detectan bloques `line vty` en router y switches.
- Las lineas VTY tienen `login`, pero no password visible ni `transport input telnet`.
- No se detectan SVIs de administracion VLAN 70 con IPs de gestion en switches de acceso.

Problemas:

- Con `login` sin password configurado, Telnet no queda listo para uso practico.
- Sin `interface vlan 70` con IP unica y `ip default-gateway 172.23.45.129`, los switches capa 2 no pueden recibir Telnet desde GestionTI.
- Si Invitados puede abrir Telnet hacia equipos internos, la ACL de aislamiento estaria incompleta.

Accion recomendada:

- Usar `enable secret OMIenable2026`.
- Configurar VTY con `password OMItelnet2026`, `login` y `transport input telnet`.
- Asignar `172.23.45.132-.152/26` a SVIs VLAN 70 de switches y reservar DHCP dinamico desde `172.23.45.154`.
- Probar Telnet desde VLAN 70 y comprobar que falla desde VLAN 30 Invitados.

### Switching De Acceso Y Backbone

Los siguientes switches existen fisicamente, pero siguen con configuracion IOS base: hostname generico `Switch`, sin VLANs OMI, sin trunks, sin puertos access por area y sin startup-config util.

| Switch | Modelo | Estado |
| --- | --- | --- |
| `SW-3ERA.1-42` | 2960-24TT | Sin VLAN/trunk/access |
| `SW-1ERA.1-40` | 2960-24TT | Sin VLAN/trunk/access |
| `SW-1ERA.1-43` | Switch-PT | Sin VLAN/trunk/access |
| `SW-2ERA.1-42` | 2960-24TT | Sin VLAN/trunk/access |
| `SW-2ERA.1-44` | Switch-PT | Sin VLAN/trunk/access |
| `SW-3ERA.1-44` | Switch-PT | Sin VLAN/trunk/access |
| `SW-4ERC.1-42` | 2960-24TT | Sin VLAN/trunk/access |
| `SW-4ERC.1-44` | Switch-PT | Sin VLAN/trunk/access |
| `SW-1ERC.1-44` | Switch-PT | Sin VLAN/trunk/access |
| `SW-1ERC.1-40` | 2960-24TT | Sin VLAN/trunk/access |
| `SW-1ERC.1-42` | 2960-24TT | Sin VLAN/trunk/access |
| `SW-2ERB.1-44` | Switch-PT | Sin VLAN/trunk/access |
| `SW-2ERB.1-42` | 2960-24TT | Sin VLAN/trunk/access |
| `SW-2ERB.1-40` | 2960-24TT | Sin VLAN/trunk/access |
| `SW-1ERB.1-44` | Switch-PT | Sin VLAN/trunk/access |
| `SW-1ERB.1-42` | 2960-24TT | Sin VLAN/trunk/access |
| `SW-2ERBL.1-44` | Switch-PT | Sin VLAN/trunk/access |
| `SW-2ERBL.1-42` | 2960-24TT | Sin VLAN/trunk/access |
| `SW-2ERBA.1-44` | Switch-PT | Sin VLAN/trunk/access |
| `SW-2ERBA.1-42` | 2960-24TT | Sin VLAN/trunk/access |
| `SW-1ERA.1-37` | 2960-24TT | Sin VLAN/trunk/access |

Accion recomendada:

- Nombrar cada switch con su hostname real.
- Configurar VTP client en cada switch de acceso/distribucion para que VLAN 10-80 se aprendan desde `SW-1ERA.1-42`.
- Configurar trunks en enlaces hacia `SW-1ERA.1-43`, `SW-1ERC.1-44`, `SW-1ERB.1-44` y switches `.44` de closets.
- Configurar access ports por area: Primaria VLAN 10, Secundaria VLAN 20, Invitados VLAN 30, Preparatoria VLAN 40, Entrenadores VLAN 50, Prensa VLAN 60, GestionTI VLAN 70, Jueces VLAN 80.
- Guardar `startup-config` en todos los equipos, no solo en el core.

## Enlaces Fisicos

Veredicto: PASS fisico, FAIL logico.

El XML actual contiene 268 enlaces:

- 259 enlaces de cobre.
- 9 enlaces de fibra.

Enlaces de fibra detectados:

| Origen | Destino |
| --- | --- |
| `SW-3ERA.1-44` | `SW-1ERA.1-43` |
| `SW-2ERA.1-44` | `SW-1ERA.1-43` |
| `SW-4ERC.1-44` | `SW-1ERC.1-44` |
| `SW-1ERC.1-44` | `SW-1ERA.1-43` |
| `SW-1ERB.1-44` | `SW-1ERA.1-43` |
| `SW-1ERB.1-44` | `SW-1ERC.1-44` |
| `SW-2ERBA.1-44` | `SW-1ERB.1-44` |
| `SW-2ERBL.1-44` | `SW-1ERB.1-44` |
| `SW-2ERB.1-44` | `SW-1ERB.1-44` |

Problema principal:

- Los enlaces de fibra existen, pero los switches que los usan no tienen configuracion trunk en IOS.
- Esto impide que VLAN 10-80 viajen entre edificios aunque el cableado fisico exista.

## DHCP

Veredicto: PASS parcial.

Servidor principal:

- `DHCP-1ERA.1-39`.
- IP: `172.23.45.130`.
- Mascara: `255.255.255.192`.
- Gateway: `172.23.45.129`.
- Conectado al switch principal en access VLAN 70.

Pools correctos detectados:

| Pool | Red | Gateway | Rango |
| --- | --- | --- | --- |
| `VLAN10_Primaria` | `172.23.40.0/23` | `172.23.40.1` | `172.23.40.2 - 172.23.41.255` |
| `VLAN_Secundaria` | `172.23.42.0/24` | `172.23.42.1` | `172.23.42.2 - 172.23.42.255` |
| `VLAN_Invitados` | `172.23.43.0/24` | `172.23.43.1` | `172.23.43.2 - 172.23.43.255` |
| `VLAN_Preparatoria` | `172.23.44.0/24` | `172.23.44.1` | `172.23.44.2 - 172.23.44.255` |
| `VLAN_Entrenadores` | `172.23.45.0/26` | `172.23.45.1` | `172.23.45.2 - 172.23.45.63` |
| `VLAN_Prensa` | `172.23.45.64/26` | `172.23.45.65` | `172.23.45.66 - 172.23.45.127` |
| `VLAN_GestionTI` | `172.23.45.128/26` | `172.23.45.129` | `172.23.45.130 - 172.23.45.191` |
| `VLAN_Jueces` | `172.23.45.192/27` | `172.23.45.193` | `172.23.45.194 - 172.23.45.223` |

Problemas:

- Existe un `serverPool` generico en el DHCP principal con red `172.23.45.128/26`, gateway `0.0.0.0`, inicio `172.23.45.128` y fin `172.23.47.127`. Es inconsistente y puede confundir la evaluacion.
- Los helpers del router apuntan al gateway `172.23.45.129`, no al servidor DHCP `172.23.45.130`.
- Muchos clientes siguen en APIPA `169.254.x.x`, senal de que no reciben DHCP o no estan en la VLAN correcta.
- `ING-04SRV-01` y `DNS-1ERA.1-36` tienen pools `0.0.0.0`, lo cual no aporta a la entrega y puede confundir.

Accion recomendada:

- Deshabilitar/eliminar `serverPool` generico en `DHCP-1ERA.1-39`.
- Corregir helpers del router hacia `172.23.45.130`.
- Excluir IPs estaticas dentro de VLAN 70 y VLAN 80 si el servidor DHCP lo permite en Packet Tracer.
- Asignar IP estatica al Servidor Local de evaluacion en VLAN 80.
- Renovar DHCP en clientes despues de corregir trunks/access ports.

## Endpoints

Veredicto: FAIL pendiente.

Solo un endpoint tiene IP valida `172.23.x.x`:

- `DHCP-1ERA.1-39`: `172.23.45.130/26`.

Hay 26 endpoints en APIPA `169.254.x.x`, senal de que no recibieron DHCP o no estan en VLAN correcta:

- Primaria: `PartPri1`, `PartPri2`, `PartPri3`.
- Secundaria/Humanidades: `Laptop3`, `Laptop4`, `1208`, `Laptop6`, `Laptop7`, `PC10`, `PC11`, `PC12`, `1101`.
- Preparatoria/Ingenieria: `PC24`, `PC25`, `PC26`.
- Prensa: `Smartphone0`, `Smartphone2`.
- Jueces: `Juez01`, `Juez02`.
- Invitados: `Invitado1`, `Invitado2`, `Invitado3`, `Invitado4`, `Invitado5`.
- Entrenadores: `Entr2-i`, `Entr1-i`.

Hay 26 endpoints sin IP registrada, incluyendo PCs de laboratorios, impresoras, servidor local y DNS:

- `PC0` a `PC9`.
- `PC13` a `PC20`.
- `ING-04SRV-01`.
- `Entr2-A`, `Entr1-A`.
- `ING-04PRN-01` a `ING-04PRN-04`.
- `DNS-1ERA.1-36`.

Accion recomendada:

- Configurar puertos access correctos en switches.
- Renovar DHCP en los clientes.
- Asignar IPs estaticas al servidor local, DNS si se usa, e impresoras.
- Probar pings desde cada segmento hacia el Servidor Local.

## Seguridad

Veredicto: FAIL.

No se encontro:

- `ip access-list`.
- `access-list`.
- `ip access-group`.
- ACL de aislamiento para Invitados.
- Reglas para proteger Jueces/Servidor Local.

Accion minima recomendada en `RT-1ERA.1-45`:

```ios
conf t
ip access-list extended ACL_INVITADOS_IN
 remark Bloqueo de invitados hacia red interna OMI/Tec
 deny ip 172.23.43.0 0.0.0.255 172.23.40.0 0.0.7.255
 permit ip 172.23.43.0 0.0.0.255 any
exit
interface GigabitEthernet0/0/0.30
 ip access-group ACL_INVITADOS_IN in
end
write memory
```

Nota: si en la simulacion no hay Internet real, el `permit any` sirve solo para no bloquear trafico externo simulado. Si no existe salida, puede ajustarse a lo que pida la rubrica.

## Checklist De Aceptacion

| Criterio | Estado | Evidencia/pendiente |
| --- | --- | --- |
| Subinterfaces dot1Q en Router 4331 | PASS parcial | VLAN 10-80 presentes |
| Gateways VLSM correctos | PASS parcial | Coinciden con el bloque `172.23.40.0/21` |
| VTP server/client | FAIL | Dominio vacio y sin comandos VTP en running-config |
| Propagacion VLAN por VTP | FAIL | VLANs no distribuidas a switches de acceso |
| DHCP pools por VLAN | PASS parcial | Pools creados, helper incorrecto |
| Trunk router-switch principal | PASS | `Gi1/0/4` en `SW-1ERA.1-42` |
| Trunks backbone/fibra | FAIL | Switches de closets sin trunk |
| WLC con WLANs | PASS parcial | WLANs 10-60 creadas |
| APs unidos al WLC | FAIL | `APS` vacio y `PRIMARY_AC 0.0.0.0` |
| WLAN Jueces VLAN 80 | FAIL | No detectada |
| Invitados aislados por ACL | FAIL | No hay ACL |
| Telnet desde GestionTI | FAIL | VTY sin password/transporte Telnet y sin SVIs de gestion |
| Clientes con IP valida | FAIL | APIPA/sin IP |
| Pings al Servidor Local | Pendiente | No demostrable desde XML |
| Export de configuraciones | Pendiente | Falta generar configs por equipo |

## Lo Que Hace Falta En Orden De Prioridad

1. Corregir DHCP relay del router hacia `172.23.45.130` y quitar helper en VLAN 70.
2. Configurar VTP: `SW-1ERA.1-42` como server y switches restantes como client en dominio `OMI-REDES`.
3. Configurar trunks del backbone, especialmente desde `SW-1ERA.1-42` hacia `SW-1ERA.1-43` y sobre los enlaces de fibra.
4. Verificar que VLAN 10-80 se propaguen por VTP a todos los switches relevantes.
5. Configurar access ports por area y puertos de APs/LWAPs en la VLAN de gestion correcta.
6. Completar WLC: interfaces dinamicas, `INTERFACE_NAME`, WLAN de Jueces y clave correcta.
7. Asociar los 16 LWAP al WLC con controlador primario `172.23.45.131`.
8. Eliminar o corregir `serverPool` generico del DHCP.
9. Asignar IP estatica al Servidor Local `ING-04SRV-01`, impresoras y DNS si aplica.
10. Aplicar ACL de Invitados en la subinterfaz VLAN 30.
11. Renovar DHCP en endpoints hasta eliminar APIPA.
12. Habilitar Telnet de administracion desde VLAN 70 y verificar bloqueo desde Invitados.
13. Ejecutar pruebas ping por segmento y documentar resultados PASS/FAIL.
14. Exportar configuraciones finales de router, switches, WLC y dispositivos clave.

## Veredicto Actual

El avance mas importante del archivo actual es la migracion a WLC/LWAP. Eso mejora el diseno para alta densidad y se alinea mejor con Primaria, Secundaria, Prensa, Entrenadores, Invitados y Jueces. Pero todavia no se puede considerar funcional porque VTP no tiene dominio/configuracion util, los APs no estan unidos al controlador, las VLAN no viajan por el backbone, DHCP relay apunta al gateway equivocado, Telnet no esta listo en VTY y no existe ACL de Invitados.

Prioridad inmediata: primero hacer que el core entregue DHCP correctamente; despues configurar VTP y levantar trunks/access VLANs; despues registrar APs al WLC; finalmente aplicar Telnet/seguridad y correr pings. Ese orden reduce ruido al depurar en Packet Tracer.
