# Tareas - Fase 3

## Estado

Leyenda: `[x]` terminado, `[~]` parcial, `[ ]` pendiente.

## Auditoria Y Base De Datos

- [x] Auditar `data/output/Reto-Redes.xml` sin cargarlo completo en contexto.
- [x] Identificar router ISR4331 principal: `RT-1ERA.1-45`.
- [x] Identificar switch de distribucion principal: `SW-1ERA.1-42`.
- [x] Identificar servidor DHCP: `DHCP-1ERA.1-39`, IP `172.23.45.130`.
- [x] Confirmar VLANs 10,20,30,40,50,60,70,80 en `SW-1ERA.1-42`.
- [~] Confirmar propagacion de VLANs a todos los switches de acceso; varios equipos siguen en VLAN 1 por defecto.

## Router 4331

- [x] Confirmar subinterfaces `GigabitEthernet0/0/0.10` a `.80`.
- [x] Confirmar encapsulacion `dot1Q` por VLAN.
- [x] Confirmar gateways VLSM aprobados.
- [ ] Corregir o validar `ip helper-address`: preferir `172.23.45.130` como servidor DHCP.
- [ ] Agregar ACL de aislamiento para VLAN 30 Invitados.
- [ ] Guardar configuracion con `write memory`.
- [ ] Exportar running-config final a texto individual.

## Switch De Distribucion `SW-1ERA.1-42`

- [x] Confirmar VLAN database 10-80.
- [x] Confirmar trunk `Gi1/0/4` hacia `RT-1ERA.1-45`.
- [x] Confirmar puerto `Gi1/0/5` en VLAN 70 para `DHCP-1ERA.1-39`.
- [ ] Configurar trunks de fibra hacia closets en `Gi1/1/1 - Gi1/1/4` o puertos equivalentes usados en la topologia.
- [ ] Verificar que los trunks permitan VLAN 10,20,30,40,50,60,70,80.
- [ ] Guardar configuracion con `write memory`.
- [ ] Exportar running-config final a texto individual.

## Switches De Acceso

- [ ] Nombrar switches por edificio/area siguiendo TIA/EIA-606-B.
- [ ] Crear VLANs 10-80 en cada switch donde aplique.
- [ ] Configurar uplinks como trunk.
- [ ] Configurar puertos de AP como access en la VLAN del area atendida.
- [ ] Configurar puertos de PCs cableadas como access en la VLAN del laboratorio.
- [ ] Aplicar `spanning-tree portfast` en puertos de usuario.
- [ ] Documentar cada puerto con `description`.
- [ ] Guardar configuracion y exportar running-config por equipo.

## DHCP Y Servicios

- [x] Confirmar pool VLAN10 Primaria.
- [x] Confirmar pool VLAN20 Secundaria.
- [x] Confirmar pool VLAN30 Invitados.
- [x] Confirmar pool VLAN40 Preparatoria.
- [x] Confirmar pool VLAN50 Entrenadores.
- [x] Confirmar pool VLAN60 Prensa.
- [x] Confirmar pool VLAN70 GestionTI.
- [x] Confirmar pool VLAN80 Jueces.
- [ ] Eliminar o justificar pool generico `serverPool`, porque se traslapa conceptualmente con GestionTI.
- [ ] Verificar que los clientes reciban gateway correcto.
- [ ] Reservar IPs estaticas para servidor local, impresoras y administracion.

## Seguridad

- [ ] Implementar `ACL_INVITADOS_IN` en subinterfaz VLAN 30.
- [ ] Probar que Invitados no accede a `172.23.45.192/27` ni a otros segmentos internos.
- [ ] Probar que Invitados conserva salida permitida si hay nube/Internet.
- [ ] Validar que Jueces y competidores autorizados si alcanzan el Servidor Local.

## Pruebas

- [ ] Hacer ping desde Primaria al Servidor Local.
- [ ] Hacer ping desde Secundaria al Servidor Local.
- [ ] Hacer ping desde Preparatoria al Servidor Local.
- [ ] Hacer ping desde Jueces al Servidor Local.
- [ ] Hacer ping desde Entrenadores segun politica autorizada.
- [ ] Verificar que Invitados falla al intentar ping al Servidor Local.
- [ ] Capturar evidencia de `show ip interface brief`, `show running-config`, `show vlan brief`, `show interfaces trunk` y pings.

## Entregables

- [x] `specs/requirements.md`
- [x] `specs/design.md`
- [x] `specs/tasks.md`
- [x] `specs/acceptance.md`
- [ ] Archivos `.txt` de configuracion final por dispositivo.
- [ ] Evidencias de conectividad y aislamiento.
