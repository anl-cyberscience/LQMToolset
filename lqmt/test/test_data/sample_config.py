USERCONFIG = """
[[Source.Directory]]
    dirs = [ "{0}" ]
    post_process = "nothing"

[[Source.Filters]]
    site_includes = [ ]
    site_excludes = [ ]
    payload_types = [ ]
    payload_formats = [ ]
    sensitivities = [ ]
    restrictions = [ ]
    reconnaissance = [ ]
    max_file_age = "2 mon"

[Logging]
  logfilebase = "{1}"
  debug = true

[Whitelist]
    whitelist = "{2}"
    dbfile = "{3}"

#Flextext configuration
[[Tools.FlexText]]
    name                = "flextext-tool"
    fileParser          = "CSV"
    fields              = ['indicator', 'reportedTime', 'detectedTime', 'duration1', 'priors', 'directSource', 'reason1', 'majorTags', 'sensitivity', 'reconAllowed', 'restriction']
    delimiter           = " "
    quoteChar           = "'"
    escapeChar          = '\\'
    headerLine          = true
    doubleQuote         = false
    quoteStyle          = "none"
    primarySchemaConfig = "resources/schemaDefinitions/lqmtools.json"
    fileDestination     = ""
    incrementFile       = true

#Toolchain configuration
[[ToolChains]]
    active = true
    name   = "anl-flextext-test"
    chain  = [ "flextext-tool" ]
"""
