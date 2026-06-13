import zipfile
import os

def extraer_datos_pkt(ruta_pkt, carpeta_destino):
    """
    Desempaqueta el archivo .pkt para extraer el XML interno 
    que contiene la topología y configuraciones.
    """
    if not os.path.exists(carpeta_destino):
        os.makedirs(carpeta_destino)
        
    try:
        # Los archivos .pkt a menudo se pueden abrir como archivos ZIP
        with zipfile.ZipFile(ruta_pkt, 'r') as zip_ref:
            # Extraemos el archivo que contiene la estructura de la red
            # Nota: El nombre exacto puede variar según la versión de Packet Tracer
            xml_config = "properties.xml" 
            
            if xml_config in zip_ref.namelist():
                zip_ref.extract(xml_config, carpeta_destino)
                # Le cambiamos el nombre para saber a qué práctica pertenecía
                nombre_base = os.path.basename(ruta_pkt).replace('.pkt', '_estructura.xml')
                os.rename(os.path.join(carpeta_destino, xml_config), os.path.join(carpeta_destino, nombre_base))
                print(f"¡Éxito! Guardado como {nombre_base}")
            else:
                print("No se encontró el archivo de propiedades estándar dentro del .pkt.")
    except zipfile.BadZipFile:
        print("El archivo .pkt no se pudo abrir. Asegúrate de que no esté corrupto.")

# Ejemplo de uso local
if __name__ == "__main__":
    extraer_datos_pkt("data/input/mi_red.pkt", "data/output/")
