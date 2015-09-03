The LQMToolset configuration file contains the local configuration options, including data source definitions, tool instances, and tool chains.

# Data Source

# Tool Chains

# Tools

### Palo Alto

### Checkpoint

### ArcSight

### CEF

# Logging

    [Logging]
        LogFileBase = "/var/log/lqmt"
        Debug = true

`LogFileBase`: The path and filename prefix to the LQMToolset log file. Multiple log files will be created based on the filename prefix specified in this setting. For example, if `LogFileBase` is "/var/log/lqmt", the following log files may be created:
- /var/log/lqmt.err.log
- /var/log/lqmt.info.log
- /var/log/lqmt.debug.log

`Debug`: Enable debug-level logging, which will create and write to the **.debug.log** file. `Debug` is optional, and it accepts either (case-sensitive) `true` or `false`.

# Whitelists

LQMToolset allows indicators to be whitelisted. When you define a path to a text file containing the whitelisted indicators, LQMToolset will check the file for modifications and then update the internal database.

In the LQMToolset configuration file, be sure to configure your whitelist settings like so:

    [Whitelist]
        whitelist = "/path/to/whitelist/file.txt"
        dbfile = "/path/to/whitelist/database.db"

`whitelist`: The full path to the text file containing whitelisted indicators, adhering to the whitelist format below.

`dbfile`: The location of the SQLite database that holds the whitelist information.

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
