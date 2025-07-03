#SCRIPT PARA EL HASHEO Y COMPROBACION DE HASHES

import hashlib

# Función para generar un hash de cualquier algoritmo partir de un texto
def generar_hash(texto: str) -> dict:
   return {
        "sha256": hashlib.sha256(texto.encode()).hexdigest(),
        "sha512": hashlib.sha512(texto.encode()).hexdigest(),
        "md5": hashlib.md5(texto.encode()).hexdigest(),
        "sha1": hashlib.sha1(texto.encode()).hexdigest()
    }
    
# Funcion para comprobar si el hash es igual al texto
def comprobar_hash(texto: str, hash_a_comprobar: str) -> bool:
    hash_generado = generar_hash(texto)
    
    if generar_hash(texto) == hash_generado:
        return f'El texto hasheado es igual a el hash generado'
    else: 
        return f'El texto hasheado no es igual a el hash generado'
    
