# Diseno Tecnico - Fase 3

## Arquitectura Logica

La topologia debe operar con un modelo router-on-a-stick:

- Router principal: `RT-1ERA.1-45`, modelo ISR4331.
- Interfaz troncal al switch de distribucion: `GigabitEthernet0/0/0`.
- Switch de distribucion principal: `SW-1ERA.1-42`, modelo 3650-24PS.
- Enlace router-switch: `SW-1ERA.1-42 Gi1/0/4` hacia `RT-1ERA.1-45 Gi0/0/0`.
- Servidor DHCP: `DHCP-1ERA.1-39`, IP `172.23.45.130/26`, gateway `172.23.45.129`, conectado a `SW-1ERA.1-42 Gi1/0/5` en VLAN 70.

## VLANs Y Direccionamiento

| VLAN | Nombre | Gateway router | Mascara | DHCP start | DHCP end |
| --- | --- | --- | --- | --- | --- |
| 10 | Primaria | `172.23.40.1` | `255.255.254.0` | `172.23.40.2` | `172.23.41.255` |
| 20 | Secundaria | `172.23.42.1` | `255.255.255.0` | `172.23.42.2` | `172.23.42.255` |
| 30 | Invitados | `172.23.43.1` | `255.255.255.0` | `172.23.43.2` | `172.23.43.255` |
| 40 | Preparatoria | `172.23.44.1` | `255.255.255.0` | `172.23.44.2` | `172.23.44.255` |
| 50 | Entrenadores | `172.23.45.1` | `255.255.255.192` | `172.23.45.2` | `172.23.45.63` |
| 60 | Prensa | `172.23.45.65` | `255.255.255.192` | `172.23.45.66` | `172.23.45.127` |
| 70 | GestionTI | `172.23.45.129` | `255.255.255.192` | `172.23.45.130` | `172.23.45.191` |
| 80 | Jueces | `172.23.45.193` | `255.255.255.224` | `172.23.45.194` | `172.23.45.223` |

## Politica De Seguridad

La VLAN 30 Invitados debe tratarse como red no confiable:

- Denegar trafico desde `172.23.43.0/24` hacia todo el bloque interno `172.23.40.0/21`.
- Permitir DHCP hacia el servidor si Packet Tracer requiere relay o respuesta del pool.
- Permitir salida a Internet solo si existe next-hop externo en la simulacion.
- Aplicar la ACL lo mas cerca del origen: entrada en `GigabitEthernet0/0/0.30`.

## CLI Base - Router 4331 `RT-1ERA.1-45`

El XML ya contiene gran parte de este bloque. Usalo para normalizar running-config y completar ACL.

```ios
enable
configure terminal
hostname RT-1ERA.1-45
ip cef
!
interface GigabitEthernet0/0/0
 description TRUNK_hacia_SW-1ERA.1-42
 no ip address
 no shutdown
 duplex auto
 speed auto
!
interface GigabitEthernet0/0/0.10
 description VLAN10_Primaria
 encapsulation dot1Q 10
 ip address 172.23.40.1 255.255.254.0
 ip helper-address 172.23.45.130
!
interface GigabitEthernet0/0/0.20
 description VLAN20_Secundaria
 encapsulation dot1Q 20
 ip address 172.23.42.1 255.255.255.0
 ip helper-address 172.23.45.130
!
interface GigabitEthernet0/0/0.30
 description VLAN30_Invitados
 encapsulation dot1Q 30
 ip address 172.23.43.1 255.255.255.0
 ip helper-address 172.23.45.130
 ip access-group ACL_INVITADOS_IN in
!
interface GigabitEthernet0/0/0.40
 description VLAN40_Preparatoria
 encapsulation dot1Q 40
 ip address 172.23.44.1 255.255.255.0
 ip helper-address 172.23.45.130
!
interface GigabitEthernet0/0/0.50
 description VLAN50_Entrenadores
 encapsulation dot1Q 50
 ip address 172.23.45.1 255.255.255.192
 ip helper-address 172.23.45.130
!
interface GigabitEthernet0/0/0.60
 description VLAN60_Prensa
 encapsulation dot1Q 60
 ip address 172.23.45.65 255.255.255.192
 ip helper-address 172.23.45.130
!
interface GigabitEthernet0/0/0.70
 description VLAN70_GestionTI
 encapsulation dot1Q 70
 ip address 172.23.45.129 255.255.255.192
!
interface GigabitEthernet0/0/0.80
 description VLAN80_Jueces
 encapsulation dot1Q 80
 ip address 172.23.45.193 255.255.255.224
 ip helper-address 172.23.45.130
!
ip access-list extended ACL_INVITADOS_IN
 remark Aisla invitados de red interna OMI/Tec
 deny ip 172.23.43.0 0.0.0.255 172.23.40.0 0.0.7.255
 permit ip 172.23.43.0 0.0.0.255 any
!
end
write memory
```

Nota tecnica: el XML actual usa `ip helper-address 172.23.45.129` en las subinterfaces. Para DHCP relay hacia un servidor dedicado, la direccion esperada es `172.23.45.130`, que corresponde a `DHCP-1ERA.1-39`. Packet Tracer puede funcionar si el servicio esta localmente asociado de forma especial, pero la configuracion IOS mas clara y evaluable apunta al servidor.

## CLI Base - Switch De Distribucion `SW-1ERA.1-42`

```ios
enable
configure terminal
hostname SW-1ERA.1-42
vtp domain OMI-REDES
vtp mode server
vtp version 2
vtp password OMI2026
!
vlan 10
 name Primaria
vlan 20
 name Secundaria
vlan 30
 name Invitados
vlan 40
 name Preparatoria
vlan 50
 name Entrenadores
vlan 60
 name Prensa
vlan 70
 name GestionTI
vlan 80
 name Jueces
!
interface GigabitEthernet1/0/4
 description TRUNK_hacia_RT-1ERA.1-45
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,50,60,70,80
 no shutdown
!
interface GigabitEthernet1/0/5
 description DHCP-1ERA.1-39
 switchport mode access
 switchport access vlan 70
 spanning-tree portfast
 no shutdown
!
interface range GigabitEthernet1/1/1 - 4
 description TRUNK_FIBRA_hacia_closets
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,50,60,70,80
 no shutdown
!
end
write memory
```

## Plantilla Para Switches De Acceso 2960

Aplicar en cada switch de acceso segun edificio y area. Ajustar hostname, uplink y puertos de usuario.

```ios
enable
configure terminal
hostname SW-AREA-ID
vtp domain OMI-REDES
vtp password OMI2026
vtp mode client
!
interface GigabitEthernet0/1
 description TRUNK_hacia_distribucion_o_patch_panel_fibra
 switchport mode trunk
 switchport trunk allowed vlan 10,20,30,40,50,60,70,80
 no shutdown
!
interface range FastEthernet0/1 - 24
 description PUERTOS_USUARIO_AJUSTAR_VLAN
 switchport mode access
 switchport access vlan VLAN_DEL_AREA
 spanning-tree portfast
 no shutdown
!
end
write memory
```

Nota VTP: en este Packet Tracer, los clientes pueden mostrar `VTP version running: 1` al pasar a `vtp mode client`, aunque antes de cambiar el modo se hubiera visto version 2. No se debe pelear esa version en el cliente. La version 2 se valida en `SW-1ERA.1-42` como servidor VTP; en clientes se valida dominio `OMI-REDES`, password, modo client y aprendizaje de VLAN 10-80 por trunk. Si un modelo de Packet Tracer no propaga VTP, crear VLAN 10-80 manualmente como respaldo en ese switch.

## Gestion Remota Por Telnet

Telnet se documenta solo para evidencia de laboratorio. Debe probarse desde VLAN 70 GestionTI y debe fallar desde VLAN 30 Invitados por la ACL de aislamiento.

Rango recomendado de gestion:

- Gateway VLAN 70: `172.23.45.129`.
- DHCP: `172.23.45.130`.
- WLC: `172.23.45.131`.
- Switches: `172.23.45.132` a `172.23.45.152`.
- DHCP dinamico GestionTI: iniciar en `172.23.45.154`.

Plantilla IOS para switches:

```ios
enable
configure terminal
service password-encryption
enable secret OMIenable2026
interface vlan 70
 description MGMT_GestionTI
 ip address IP_MGMT_UNICA 255.255.255.192
 no shutdown
exit
ip default-gateway 172.23.45.129
line vty 0 15
 password OMItelnet2026
 login
 transport input telnet
 exec-timeout 10 0
end
write memory
```

Plantilla IOS para router:

```ios
enable
configure terminal
service password-encryption
enable secret OMIenable2026
line vty 0 4
 password OMItelnet2026
 login
 transport input telnet
 exec-timeout 10 0
end
write memory
```

## Configuracion Fisica Esperada

- Enlaces entre closets: fibra optica mediante patch panels y puertos troncales.
- Puertos de usuario en el mismo salon/laboratorio: cable directo permitido sin TO ni patch panel obligatorio.
- Elementos fisicos documentados en Packet Tracer con nombres compatibles con TIA/EIA-606-B.
- Descripciones de interfaces deben indicar destino: `TRUNK_hacia_...`, `AP_...`, `PC_...`, `DHCP_...`.
