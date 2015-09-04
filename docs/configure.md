The LQMToolset configuration file contains the local configuration options, including data source definitions, tool instances, and tool chains.

# Data Source
This setting specifies root source directories and what to do with the files once they've been processed.

    [[Source.Directory]]
        dirs = ["/tmp", "/var/spool"]
        post_process = "delete"

Setting        | Explanation
:------------: | :----------
    `dirs`     | A list of directory paths, whose contents will be scanned for input files to process.
`post_process` | An action for LQMToolset to perform after processing a file. Allowed values include `delete`, `move`, and `track`. While `delete` is self-explanatory, `move` will mark the input files to be moved after processing to another directory. `track` will mark the input files to be tracked in another text file.

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
The Palo Alto tool places or removes blocks on Palo Alto Networks firewall devices.

    [[Tools.PaloAlto]]
        name = "my-pa200"
        api_key = "API KEY OBTAINED FROM DEVICE"
        api_username = "username"
        api_password = "password"
        hostname = "palo-alto.yourdomain.com"
        badIPFiles = [ "BlockedIPs-01.txt", "BlockedIPs-02.txt" ]
        block_lists = [ "CFM_EBL-01", "CFM_EBL-02" ]
        db_location = "paloalto"
        cafile = "pa-ames/pa.crt"
        prune_method = "Expiration"
        default_duration = 259200
        unprocessed_file = "unprocessed/pa-ames.csv"

Setting              | Explanation
:------------------: | :----------
`name`               | A unique name identifying this device.
`api_key`            | The API key retrieved from the Palo Alto device for remote access.
`api_username`       | A username with with API access/privileges to the Palo Alto device.
`api_password`       | The corresponding password to the username listed above.
`hostname`           | The hostname or IP address of the Palo Alto device.
`badIPFiles`         | A list of dynamic block-lists files to use. Each file can hold 300 less than the maximum number of IP addresses that the Palo Alto device supports.
`block_lists`        | The named block lists configured on the Palo Alto device.
`db_location`        | The path to the directory that will hold the local database of blocked IP addresses.
`cafile`             | The path to your CA certificate file for the Palo Alto device.
`prune_method`       | The method used to prune IP addresses from the database if there are more IP addresses than the Palo Alto device supports. IP addresses are pruned after removing all expired IP blocks. `prune_method` accepts `Expiration`, for removing blocks with the earliest expiration time; `Added`, for removing blocks with the earlist added time; and `Detected`, for removing blocks with the earliest detection time.
`default_duration`   | The default time limit that a block should be held if the duration is not specified in the alert.
`unprocessed_file`   | The path to the CSV file that will hold all unprocessed blocks. The contents will consist of filenames, whose names have been altered by adding a timestamp (YYMMDD-HHMMSS) between the name and the extension. (If the file lacks an extension, the timestamp will be appended to the filename.)
`actions_to_process` | A list of actions for this tool to process: `Block`, `Revoke`, `Notify`, `Watch`, `SendReport`, `OtherAction`, `All`.

#### Device Setup & Configuration

### Checkpoint
Place or remove blocks on Checkpoint devices. The connection to Checkpoint devices is done through a shared SSL key which needs to be generated on the machine LQMTools is installed on and copied to the Checkpoint device.

    [[Tools.Checkpoint]]
        name = "checkpoint"
        hostname = "checkpoint.yourdomain.com"
        port = 22
        username = "foo"
        originator = "bar"
        default_duration = 259200
        unprocessed_file = "unprocessed.txt"
        actions_to_process = "All"
        

Setting                 | Explanation
:---------------------: | :----------
`name`                  | A unique name identifying this device. 
`hostname`              | The Checkpoint device's hostname or IP address.
`port`                  | The port number through which to connect via SSH.
`username`              | The username with which to login to the Checkpoint device.
`originator`            | The originator that will be stored with the blocks put into the Checkpoint device.
`default_duration`      | The default time a block should be in place for if the duration is not specified in the alert.
`unprocessed_file`      | A file that will hold all unprocessed blocks. This file will be a CSV file and will have the creation timestamp (YYMMDD-HHMMSS) embedded in the filename before the extension, or at the end if no extension is specified. For example, if the filename is *dir/file.txt*, the file created, if nessecary, would be *dir/file.20150401-113524.txt*.
`actions_to_process`    | Specify the list of actions this cool can/will process. Valid values: `Block`, `Revoke`, `Notify`, `Watch`, `SentReport`, `OtherAction`, `All`.

#### Device Setup & Configuration
The LQMTool module for checkpoint devices uses the checkpoint firewall's Suspicious Activities Monitoring Protocol (samp) to block IP addresses via the command line interface and ssh from the LQMT machine. The following outlines the steps necessary to congiure the device for use with LQMT. The following assumes the computer that is running the LQMT software is named lqmt.domain.com, the checkpoint computer is named cp.domain.com

- Use the web UI to create a new user with an adminRole, set the shell to /bin/bash, and ensure that command line access is granted. For purposes of this document, the username cfm will be used. 
- Set up password-less ssh access for the cfm user just created. The exact steps will depend on the machine running LQMT, but the basics: 
    - Create an RSA key pair if not already done. This can be done by running the command: `ssh-keygen -t rsa` on lqmt.domain.com and accepting all the defaults. For these purposes, itis best to not have a passphrase for this key pair. 
    - Copy the public key to the admin user's account on the checkpoint device. Depending on the open-ssl version on the LQMT computer, you could use the command: `ssh -copy-id cfm@cp.domain.com`. If that command isn't available, you can run the following on lqmt.domain.com as the user that will be running LQMT:  `cat ~/.ssh/id_rsa.pub | ssh user@123.45.56.78 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys`
    - Verify password-less access by trying to ssh to the checkpoint machine: 
        - `ssh cfm@cp.domain.com`
    - In addition, the checkpoint device needs to be configured as a firewall in order for the LQMT to be effective. 

#### Limitations
The Checkpoint module currently only blocks IP addresses and network ranges(CIDR). Any other blocks that are not supported will be output to the file specified in the unhandled_blocks configuration parameter. 

### ArcSight
The ArcSight tool places or removes blocks on ArcSight devices.

    [[Tools.ArcSight]]
        name = "arcsight-1"
        host = "arcsight1.yourdomain.com"
        port = 598
        protocol = "tcp"
        actions_to_process = [ "All" ]

Setting              | Explanation
:------------------: | :----------
`name`               | A unique name identifying this device.
`host`               | The hostname or IP address of the ArcSight device.
`port`               | The port number on which the ArcSight device is listening.
`protocol`           | The IP protocol to use: `tcp` or `udp`.
`actions_to_process` | A list of actions for this tool to process: `Block`, `Revoke`, `Notify`, `Watch`, `SendReport`, `OtherAction`, `All`.

#### Device Setup & Configuration
To configure the ArcSight logger to receive data from LQMToolset, a new Receiver needs to be configured. To do so, login through the web interface of the ArcSight device,  and navigate to *Configuration* > *Receivers*. Click the *Add* button, enter a name for the Receiver, select *CEF TCP Receiver*, and click *next*. At this time, modify any necessary parameters. Do _not_ change the source type. Note the port number! (You'll need that port number for the LQMToolset configuration file). By default, new Receivers aren't enabled. Enable the new Receiver by clicking the box on the far right of the Receiver list for the new Receiver that was just added.

### CEF
The CEF tool converts data from the intermediate format to the CEF format.

    [[Tools.CEF]]
        name = "cef-mapping"

Setting | Explanation
:-----: | :----------
`name`  | A unique name identifying this device.

### Syslog
The Syslog tool is used to log information to remote Syslog servers. 
   
    [[Tools.SysLog]]
        name = "syslog-1"
        host = "syslog1.yourdomain.com"
        port = 514
        protocol = "tcp"
        messageHead = "WY rsyslogd: Message from LQMT - "
        messageFields = ["indicatorType", "indicator", "action1"]

Example output in syslog: 
    
    Aug 26 14:23:01 WY rsyslogd: Message from LQMT - indicatorType="IPv4Address" indicator="192.168.1.1" action1="Block"
    Aug 26 14:23:01 WY rsyslogd: Message from LQMT - indicatorType="IPv4Address" indicator="192.168.1.2" action1="Block"
    Aug 26 14:24:05 WY rsyslogd: Message from LQMT - indicatorType="IPv4Address" indicator="192.168.1.5" action1="Block"

Setting         | Explanation
:-------------: | :-----------
`name`          | A Unique name identifying this device.
`host`          | The hostname or IP address of the remote syslog server
`port`          | The port number the Syslog server is listening on. Note: Syslog defaults to 514, so if left blank LQMT will also default to 514 for   communication. 
`protocol`      | The IP protocol to use: "tcp" or "udp"
`messageHead`   | Used at the beginning of every message sent to Syslog. 
`messageFields` | Used to specify what fields you want extracted from the alerts and sent in the message to Syslog. 

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
