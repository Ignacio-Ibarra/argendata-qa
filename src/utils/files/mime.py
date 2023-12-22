import mimetypes

MICROSOFT_OFFICE_MIMETYPES = {
    "application/msword": ".doc",
    # "application/msword": ".dot",

    "application/vnd.openxmlformats-officedocument.wordprocessingml.document": ".docx",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.template": ".dotx",
    "application/vnd.ms-word.document.macroEnabled.12": ".docm",
    "application/vnd.ms-word.template.macroEnabled.12": ".dotm",

    "application/vnd.ms-excel": ".xls",
    # "application/vnd.ms-excel": ".xlt",
    # "application/vnd.ms-excel": ".xla",

    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet": ".xlsx",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.template": ".xltx",
    "application/vnd.ms-excel.sheet.macroEnabled.12": ".xlsm",
    "application/vnd.ms-excel.template.macroEnabled.12": ".xltm",
    "application/vnd.ms-excel.addin.macroEnabled.12": ".xlam",
    "application/vnd.ms-excel.sheet.binary.macroEnabled.12": ".xlsb",

    "application/vnd.ms-powerpoint": ".ppt",
    # "application/vnd.ms-powerpoint": ".pot",
    # "application/vnd.ms-powerpoint": ".pps",
    # "application/vnd.ms-powerpoint": ".ppa",

    "application/vnd.openxmlformats-officedocument.presentationml.presentation": ".pptx",
    "application/vnd.openxmlformats-officedocument.presentationml.template": ".potx",
    "application/vnd.openxmlformats-officedocument.presentationml.slideshow": ".ppsx",
    "application/vnd.ms-powerpoint.addin.macroEnabled.12": ".ppam",
    "application/vnd.ms-powerpoint.presentation.macroEnabled.12": ".pptm",
    "application/vnd.ms-powerpoint.template.macroEnabled.12": ".potm",
    "application/vnd.ms-powerpoint.slideshow.macroEnabled.12": ".ppsm",

    "application/vnd.ms-access": ".mdb"
}

extensions = {v:k for k, v in mimetypes.types_map.items()}
extensions.update(MICROSOFT_OFFICE_MIMETYPES)