# Verificador

La idea de éste módulo es tener bien segregadas las verificaciones que tienen que hacerse.

Algunas verificaciones **necesitan** otras. Por ejemplo, es difícil mirar nombres de variables, etc si el encoding no es
correcto. Pero para mirar el sistema de archivos; contar los datasets, scripts, variables declarados versus efectivos;
mirar las extensiones (.csv, .docx, etc); entre otros, se pueden hacer sin conocer la codificación.

Por ende, el objetivo tiene que ser identificar qué verificaciones bloquean a otras y cuáles no.

> [!CAUTION]
> Hay código hardcodeado a fines de tener _algo_ que ejecutar.

> [!WARNING]
> Actualmente hay distintos verificadores a fin de testear la funcionalidad básica.
> La estructura puede cambiar drásticamente, de tener varios verificadores a tener un
> solo verificador con varias funciones.

> [!TIP]
> Actualmente algunos verificadores como `VerificadorCSV` ejecuta automáticamente todas las verificaciones registradas 
> con `verificar_todo()`. Éste patrón se podría replicar en otros verificadores que exploten mejor ésta funcionalidad.

# Notas sobre la pipeline de verificaciones

- Cualquier chequeo sobre los archivos se tiene que hacer sobre la intersección de los declarados y los efectivos (no tiene sentido chequear efectivos no declarados).

- Antes de cargar el dataframe, necesito saber el delimiter, pues puede cargarme todo en la misma columna si no lo especifico.

- Necesito el encoding para saber si está bien lo que estoy leyendo, por lo tanto:
    - Si detecto un encoding LEGIBLE pero que no esté dentro de los encodings aceptados, devuelvo una advertencia.
    - Siempre tengo que doble-chequear el encoding.


- Para poder chequear cardinalidad (que no haya dos datapoints exactamente iguales), dependo de conocer el formato wide/long. Pero como conocer el formato (ahora) no es determinista, no tengo certeza en ninguna de ambas. Lo mejor por ahora es:
    - Chequear primero formato y, en función de la probabilidad de que esté incorrecto, enviar una advertencia.
    - Siempre hacer el chequeo de la cardinalidad, con la salvedad de la advertencia anterior (que tiene que ser cubritiva respecto de los casos posibles)



Chequeos FS:

- 'google docs', no .docx
- scripts/datasets declarados vs efectivos

Chequeos archivos (en orden):
- Codificacion correcta
- Headers que no matcheen regex
- Caracteres raros

Chequeos consistencia:
- Metadatos (en orden):
    - Variables declaradas/efectivas
    - Wide/Long
    - Cardinalidad 