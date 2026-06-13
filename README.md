# Reto-Redes

## Generar el XML desde el Packet Tracer

1. Coloca el archivo `.pkt` dentro de `data/input/`.
2. Ejecuta el comando ajustando el nombre del archivo de entrada y la salida XML:

```bash
./src/pka2xml/pka2xml -d "data/input/Nombre del archivo.pkt" data/output/Como quieres que se llame el .xml
```

3. El archivo XML generado quedará en `data/output/` con el nombre que indiques en el comando.

Para una version mas amigable y visual, consulta [specs/paso-a-paso-fase3.html](specs/paso-a-paso-fase3.html).
La version completa y tecnica sigue en [specs/paso-a-paso-fase3.txt](specs/paso-a-paso-fase3.txt).