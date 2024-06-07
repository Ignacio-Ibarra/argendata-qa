# Consolidacion de metadata
# Levanta las sheets de metadata y arma un csv con el conteo de subtopicos e items por url e institucion
library(googledrive)
library(tidyverse)
library(googlesheets4)

# setear mail de usuario con Sys.setenv("USER_GMAIL" = "")

# Autentica el acceso a Google Drive usando la dirección de correo electrónico de Gmail del usuario configurada en las variables de entorno
drive_auth(email = Sys.getenv("USER_GMAIL"))

# Lista los archivos dentro de la carpeta de Google Drive especificada por su ID y los guarda en un dataframe
df <- drive_ls(path = as_id("https://drive.google.com/drive/folders/16Out5kOds2kfsbudRvSoHGHsDfCml1p0"))

# Filtra el dataframe para obtener el ID de la carpeta que contiene los subtemas
id_subtopicos <- df[df$name == "SUBTOPICOS",]$id

# Lista los archivos o carpetas dentro de la carpeta de subtemas utilizando su ID
paths_subtopicos <- drive_ls(id_subtopicos)

# Para cada ID en paths_subtopicos, lista los archivos dentro y los recopila en una lista
files_subtopicos <- map(paths_subtopicos$id, \(x) {
  drive_ls(x)
})

# Combina los dataframes de archivos de subtemas en uno solo
files_subtopicos <- bind_rows(files_subtopicos)

# Filtra los archivos de metadatos que contienen "argendata -" en su nombre, excluyendo aquellos que contienen "ejemplo"
metadata_files <- files_subtopicos %>% 
  filter(str_detect(tolower(name), "argendata -")) %>% 
  filter(! str_detect(tolower(name), "ejemplo"))

# Autentica el acceso a Google Sheets usando la misma dirección de correo electrónico
gs4_auth(email = Sys.getenv("USER_GMAIL"))

leer_metadata <- function(id, name){
  read_sheet(id, skip = 6, col_types = "c") %>% mutate(subtop_id = str_replace(tolower(name), "argendata -", ""))
}

# Para cada archivo de metadatos, lee su contenido saltando las primeras 6 filas y asumiendo que las columnas son tipo texto
metadata <- map2(metadata_files$id, metadata_files$name, \(x,y) {leer_metadata(id = x, name = y)})

# Combina los datos leídos de todos los archivos de metadatos en un único dataframe
metadata_concat <- bind_rows(metadata) %>% select(-area,-topico_desc,-subtopico_desc)

# Filtra el dataframe resultante para eliminar las filas donde todos los valores son NA (datos faltantes)
metadata_concat <- metadata_concat %>% 
  filter(!if_all(everything(), is.na))

# Escribe el dataframe final a un archivo CSV llamado "metadata.csv"
metadata_concat %>% 
  write_csv("./tools/metadata.csv")

