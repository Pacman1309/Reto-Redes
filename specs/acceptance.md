# Criterios De Aceptacion - Fase 3

## Rubrica PASS/FAIL

| ID | Criterio | Evidencia esperada | Estado actual |
| --- | --- | --- | --- |
| AC-01 | Router 4331 con subinterfaces dot1Q por VLAN | `show running-config` en `RT-1ERA.1-45` | PASS parcial: existe en XML |
| AC-02 | Gateways VLSM correctos para VLAN 10-80 | `show ip interface brief` y tabla VLSM | PASS parcial: coincide con XML |
| AC-03 | DHCP funcional por VLAN | Cliente obtiene IP/gateway de su segmento | PASS parcial: pools existen; falta prueba |
| AC-04 | Servidor DHCP en GestionTI | IP `172.23.45.130/26`, gateway `172.23.45.129` | PASS |
| AC-05 | Trunk router-distribucion | `show interfaces trunk` en `SW-1ERA.1-42` | PASS parcial |
| AC-06 | VLANs propagadas a switches de acceso | `show vlan brief` por switch | FAIL pendiente |
| AC-07 | Invitados aislado de red interna | Ping desde VLAN 30 a Jueces/Servidor Local falla | FAIL pendiente |
| AC-08 | Competidores autorizados alcanzan Servidor Local | Ping desde Primaria/Secundaria/Preparatoria/Jueces exitoso | FAIL pendiente |
| AC-09 | Cableado entre closets con fibra y patch panels | Vista fisica Packet Tracer con enlaces y labels | PASS parcial, requiere revision visual final |
| AC-10 | Documentacion TIA/EIA-606-B | Hostnames, descripciones y etiquetas fisicas | FAIL pendiente |
| AC-11 | Export de configs individuales | Archivos `.txt` por router/switch | FAIL pendiente |
| AC-12 | Telnet administrativo desde GestionTI | `telnet 172.23.45.132` desde VLAN 70 funciona; desde Invitados falla | FAIL pendiente |

## Comandos De Verificacion

Ejecutar en `RT-1ERA.1-45`:

```ios
show ip interface brief
show running-config
show running-config | section line vty
show access-lists
show ip route
```

Ejecutar en `SW-1ERA.1-42`:

```ios
show ip interface brief
show vlan brief
show interfaces trunk
show running-config | section line vty
show running-config
```

Ejecutar en cada switch de acceso:

```ios
show ip interface brief
show vlan brief
show interfaces trunk
show running-config | section line vty
show running-config
```

Ejecutar desde hosts finales:

```text
ipconfig
ping 172.23.45.193
ping IP_SERVIDOR_LOCAL
telnet 172.23.45.132
```

## Matriz De Pruebas Minima

| Origen | VLAN origen | Destino | Resultado esperado |
| --- | --- | --- | --- |
| Laptop Primaria | 10 | Servidor Local | PASS |
| Laptop Secundaria | 20 | Servidor Local | PASS |
| PC Preparatoria | 40 | Servidor Local | PASS |
| PC Jueces | 80 | Servidor Local | PASS |
| Host Entrenadores | 50 | Servidor Local | Segun politica del evento |
| Host Prensa | 60 | Internet | PASS si existe salida |
| Host Invitados | 30 | Servidor Local | FAIL esperado |
| Host Invitados | 30 | `172.23.45.193` | FAIL esperado |
| Host Invitados | 30 | Internet | PASS si existe salida |
| Host GestionTI | 70 | Telnet a `172.23.45.132` | PASS |
| Host Invitados | 30 | Telnet a `172.23.45.132` | FAIL esperado |

## Condicion De Cierre

La Fase 3 se considera aceptada cuando:

- Todas las VLAN tienen gateway operativo.
- DHCP entrega direcciones dentro del rango aprobado.
- Los segmentos autorizados alcanzan el Servidor Local.
- Invitados queda aislado de la red interna.
- Los trunks inter-closet transportan las VLAN requeridas.
- Telnet administrativo funciona desde GestionTI y queda bloqueado desde Invitados.
- Los archivos de configuracion final se exportan por dispositivo.
- La evidencia de comandos y pings queda lista para el reporte de Fase 4.
