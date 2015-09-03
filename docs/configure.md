The LQMToolset configuration file contains the local configuration options, including data source definitions, tool instances, and tool chains.

# Data Source
This setting specifies root source directories and what to do with the files once they've been processed.

    [[Source.Directory]]
        dirs = ["/tmp", "/var/spool"]
        post_process = "delete"

Setting        | Explanation
:------------: | :----------
    `dirs`     | A list of directory paths, whose contents will be scanned for input files to process.
`post_process` | An action for LQMToolset to perform after processing a file. Allowed values include "delete", "move", and "track". While "delete" is self-explanatory, "move" will mark the input files to be moved after processing to another directory. "track" will mark the input files to be tracked in another text file.

# Tool Chains
Tool Chains are built from tool instances, which are created from the available tools in LQMToolset. Chaining these tool instances together creates Tool Chains. To configure a new device, an entry must be added in the configuration file.

    [[ToolChains]]
        name = "arcsight-1"
        chain = [ "cef-mapping", "arcsight-1" ]

Setting | Explanation
:-----: | :----------
`name`  | A unique name identifying the Tool Chain.
`chain` | A list of tools to chain together to perform processing on each record.
`active`| Enables this Tool Chain if set to `true`. Otherwise, it will disable this Tool Chain if set to `false`. `active` is optional, and will default to `true` if not specified.

**NOTE**: There can be many tools of a specific type--one for each physical device--but they must have distinct names.

# Tools

### Palo Alto

### Checkpoint

### ArcSight

### CEF
The CEF tool converts data from the intermediate format to the CEF format.

    [[Tools.CEF]]
        name = "cef-mapping"

Setting | Explanation
:-----: | :----------
`name`  | A unique name identifying this device.

# Logging

    [Logging]
        LogFileBase = "/var/log/lqmt"
        Debug = true

Setting       | Explanation
:-----------: | :----------
`LogFileBase` |The path and filename prefix to the LQMToolset log file. Multiple log files will be created based on the filename prefix specified in this setting. For example, if `LogFileBase` is "/var/log/lqmt", "/var/log/lqmt.err.log" and "/var/log/lqmt.info.log" will be created.
`Debug`       | Enable debug-level logging, which will create an additional log file, *.debug.log*. `Debug` is optional, and it accepts either `true` or `false`.

# Whitelists
LQMToolset allows indicators to be whitelisted. When you define a path to a text file containing the whitelisted indicators, LQMToolset will check the file for modifications and then update the internal database.

    [Whitelist]
        whitelist = "/path/to/whitelist/file.txt"
        dbfile = "/path/to/whitelist/database.db"

Setting     | Explanation
:---------: | :----------
`whitelist` | The full path to the text file containing whitelisted indicators, adhering to the whitelist format below.
`dbfile`    | The location of the SQLite database that holds the whitelist information.

## Whitelist Format

The following sections specify the format of the whitelist file mentioned above.

###### IPv4 Addresses

    [IPv4Address]
    192.168.1.1

###### IPv4 Subnet Ranges

    [IPv4Subnet]
    192.168.1.0/24
    192.168.2.0/24
    192.168.3.0/24

###### IPv6 Addresses

    [IPv6Address]
    ffff:ffff:ffff:ffff:ffff:ffff:ffff:ffff

###### IPv6 Subnet Ranges

    [IPv6Subnet]
    ffff:ffff:ffff:ffff/90

###### Domain Name

    [Domain]
    example.com
    example2.com

###### Host

    [Host]
    badguy.example.com

###### URL

    [URL]
    http://www.somesite.com/blah
