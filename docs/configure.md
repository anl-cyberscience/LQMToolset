The LQMToolset configuration file contains the local configuration options, including data source definitions, tool instances, and tool chains.

# Data Source
This setting specifies root source directories and what to do with the files once they've been processed.

    [[Source.Directory]]
        dirs = ["/tmp", "/var/spool"]
        post_process = "delete"

Setting        | Explanation
:------------: | :----------
    `dirs`     | A list of directory paths, whose contents will be scanned for input files to process.
`post_process` | An action for LQMToolset to perform after processing a file. Allowed values include `delete`, `move`, and `track`. While `delete` is self-explanatory, `move` will mark the input files to be moved after processing to another directory. `track` will mark the input files to be tracked in another text file. `move` is the default value when nothing is set in the user configuration file. 

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
`api_key`            | The API key retrieved from the Palo Alto device for remote access. Note: You can either use an API key, or a username/password. An API key is recommended.
`api_username`       | A username with with API access/privileges to the Palo Alto device. Note: You can either use an API key, or a username/password. An API key is recommended.
`api_password`       | The corresponding password to the username listed above. Note: You can either use an API key, or a username/password. An API key is recommended.
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
LQMT uses Palo Alto's Dynamic Block Lists (also called External Block Lists or EBLs) to block IPs. There is a limit to the number of IP addresses that can be blocked by a Palo Alto device. See your devices documentation for these limits. Each Palo Alto device can have up to 10 block lists and each block list is limited to 300 less than the device's limit. The Palo Alto accesses the EBLs via http request to a web server. Configuring one is beyond the scope of this document. 

Requirements: 

- Web server to host the Dynamic Block List files
    - Only needs to be accessible from the machine LQMT is installed on
    - The LQMT machine also needs to have write access to the location it reads the EBLs from as it will write the files to that location
- The LQMT machine needs to trust the root CA for the Palo Alto web server
    - One will need to be created if one hasn't already been imported
        - The default certificate created by the device will not work. 
    - To create one,
        - Log in to the web UI as an administrator
        - Select the Device tab
        - Select Certificates under the Certificated management menu
        - Click on Generate at the bottom of the window
        - Fill in the fields as appropriate
            - Common name should be the machine name
            - Ensure Certificate Authority is check
            - Add any Certificate Attributes you may want
            - Click Generate
    - The click on the newly generated certificate and check the following:
            - Forward Trust Certificate
            - Forward Untrust Certificate
            - Certificate for Secure Web GUI
    - After creating the certificate, you will need to export it
        - Click the export button at the bottom of the window and accept the defaults
        - Store it in a location accessible to LQMT
        - Specify the location in the cafile configuration parameter for the specific Palo Alto device
- Create the block list objects
    - Log into the Web GUI as an administrator
    - Select the Objects tab
    - Select the Dynamic Block Lists item from the menu
        - Click the Add button at the bottom of the window
        - Enter a name
            - This name will be in the block_lists configuration parameter
        - Optionally enter a description
        - Enter the source location of the file backing this block list
            - The physical location of the file will be added to the badIPFiles configuration parameter
        - Set the repeat to Monthly at 00:00
            - This is sufficient because LQMT will perform a refresh as necessary and doesn't need to rely on a regularly scheduled refresh
- Create the policies that use the block lists to restrict network traffic
    - Due to the unique nature of each installation, this is beyond the scope of this document
    - Some useful links related to using EBLs
        - <https://live.paloaltonetworks.com/t5/Learning-Articles/Working-with-External-Block-List-EBL-Formats-and-Limitations/ta-p/58795>
        - <https://www.paloaltonetworks.com/documentation/61/pan-os/pan-os/policy/use-a-dynamic-block-list-in-policy.html>

#### Limitations
The Palo Alto module currently only blocks IP addresses and network ranges (CIDR). Any other block that are not supported will be output to the field specified in the unhandled_blocks configuration parameter. 

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
`name`                  | A unique name identifying this tool instance. 
`hostname`              | The Checkpoint device's hostname or IP address.
`port`                  | The port number through which to connect via SSH.
`username`              | The username with which to login to the Checkpoint device.
`originator`            | The originator that will be stored with the blocks put into the Checkpoint device.
`default_duration`      | The default time a block should be in place for if the duration is not specified in the alert.
`unprocessed_file`      | A file that will hold all unprocessed blocks. This file will be a CSV file and will have the creation timestamp (YYMMDD-HHMMSS) embedded in the filename before the extension, or at the end if no extension is specified. For example, if the filename is *dir/file.txt*, the file created, if nessecary, would be *dir/file.20150401-113524.txt*.
`actions_to_process`    | Specify the list of actions this cool can/will process. Valid values: `Block`, `Revoke`, `Notify`, `Watch`, `SentReport`, `OtherAction`, `All`.

#### Device Setup & Configuration
The LQMTool module for checkpoint devices uses the checkpoint firewall's Suspicious Activities Monitoring Protocol (samp) to block IP addresses via the command line interface and ssh from the LQMT machine. The following outlines the steps necessary to configure the device for use with LQMT. The following assumes the computer that is running the LQMT software is named lqmt.domain.com, the checkpoint computer is named cp.domain.com

- Use the web UI to create a new user with an adminRole, set the shell to /bin/bash, and ensure that command line access is granted. For purposes of this document, the username cfm will be used. 
- Set up password-less ssh access for the cfm user just created. The exact steps will depend on the machine running LQMT, but the basics: 
    - Create an RSA key pair if not already done. This can be done by running the command: `ssh-keygen -t rsa` on lqmt.domain.com and accepting all the defaults. For these purposes, it is best to not have a passphrase for this key pair. 
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
`name`               | A unique name identifying this tool instance.
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
`name`  | A unique name identifying this tool instance.

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
`name`          | A unique name identifying this tool instance.
`host`          | The hostname or IP address of the remote syslog server.
`port`          | The port number the Syslog server is listening on. Note: Syslog defaults to 514, so if left blank LQMT will also default to 514 for communication. 
`protocol`      | The IP protocol to use: `tcp` or `udp`.
`messageHead`   | Used at the beginning of every message sent to Syslog. 
`messageFields` | Used to specify what fields you want extracted from the alerts and sent in the message to Syslog. 

### FlexText
FlexText is a tool used to output parsed alert data in a user-defined, character delimited, format. 

    [[Tools.FlexText]]
        name                = "flextext-tool"
        fileParser          = "CSV"
        fields              = 'action1,indicator,reportedTime'
        delimiter           = ","
        quoteChar           = '"'
        escapeChar          = '\\'
        headerLine          = true
        doubleQuote         = false
        quoteStyle          = "Minimal"
        primarySchemaConfig = "resources/schemaDefinitions/lqmtools.json"
        fileDestination     = "/home/output/test.csv"
        incrementFile       = true

Setting               | Explanation
:-------------------: | :-----------
`name`                | A unique name identifying this tool instance.
`fileParser`          | Select parser type. Currently only supports and defaults to `CSV`.
`fields`              | Fields, identified from the intermediate format, to be extracted. The order of the fields here determines the order of the output.
`delimiter`           | A single character delimiter used to separate fields. Default value is `,`.
`quoteChar`           | Character used to quote respective values.
`escapeChar`          | Character used to escape other characters.
`headerLine`          | Boolean value used to set if a header line detailing the extracted values should be included in the output. Defaults to `False`.
`doubleQuote`         | Determines how the quoteChar itself is quoted. If `True` then the character is doubled. If `False`, the character is prefixed to the quoteChar.
`quoteStyle`          | Sets the style of the quoting. Can be one of four values. `Minimal`: only quotes fields that contain special characters. `NonNumeric`: only quotes non-numeric fields. `All`: quotes all fields. `None`: No fields are quoted
`primarySchemaConfig` | Defines the path to the primary schema configuration. Most users won't need to change the default setting; if you do, then some understanding of FlexTransform is suggested.
`fileDestination`     | Sets the destination of the output file. 
`incrementFile`       | Used to increment the output file. When set to `True`, the output file name will be incremented with a timestamp. When set to `False` the output file will be overrune everytime the the tool is run. Defaults to `False`

### Splunk
Ingest CTI data into your Splunk instance in a keyword value format. 

Setting                 | Explanation
:---------------------: | :-----------
`name`                  | A unique name identifying this tool instance. 
`host`                  | Host address of your Splunk instance.
`port`                  | Port used to communicate with your Splunk instances REST Api interface. Defaults to `8089`.
`username`              | Username that you want to authenticate with.
`password`              | Password that you want to authenticate with.
`cert_check`            | Used to disable the the certificate check. This is helpful for testing on a machine that you haven't imported your Splunk SSL cert on yet. Defaults to `false`.
`source`                | Name of the source you want the data to be identified by. Defaults to `lqmt`. 
`sourcetype`            | The sourcetype that you want to insert the data into. 

#### Device Setup and Configuration 
LQMT authenticates using Splunk's token-based authentication endpoint. This requires you to provide a username and 
password. It is recommended that you create a new role specifically for rest api usage as well as a new user that 
belongs to this role. Having a specific user and role just for REST api access will make auditing your rest api usage
much easier.

##### Role Creation
The following steps will walk you through creating a role with enough permissions to permit usage of the REST api.

1. Log into the web interface of your Splunk instance and go to `Settings` and then `Access Controls`.
2. From the `Access Control` screen, click the `Add New` action in the `Roles` row.
3. Assign this role any name you see fit. We will use `splunk_rest_api` in this example.
4. Everything will be left default with the exception of the `Capabilities` section. Go to the `Capabilities` section
and add the `edit_tcp` capability from the `Available capabilities` section to the `Selected capabilities` section. 
5. By default, Splunk should allow this role to access the `main` index under the `Indexes searched by default` section 
and the `All non-internal indexes` index under the `Indexes` section. Verify with your Splunk admin that you won't need 
access to any other indexes.
6. Once completed, hit `Save`

You should now have a custom role created for using the Splunk REST API. 

##### User Creation
The following steps will walk you through creating a new Splunk user and assigning them to a role. 

1. Log into the web interface of your Splunk instance and go to `Settings` and then `Access Controls`.
2. From the `Access Control` screen, click the `Add New` action in the `Users` row.
3. Name your user. In our case, we will name our user `splunk_rest_api_user`
4. Fill in the `Full name`, `Email address`, and `Time zone` fields as you see fit. They are not needed, but can still 
used if you desire. 
5. Under the `Assign to roles` section, select the role that you previously created for REST API usage. Our role was 
named `splunk_rest_api`, so we will select that.
6. By default, splunk will have the `user` role pre-selected in the `Selected roles` section. We recommend removing this
role if you are only using this account for user Splunk REST api. 
7. Set a password for your user.
8. One completed, hit `Save`

You should now have a user created specifically for using Splunk's REST API. This user can now be used in your LQMT 
instance for pushing data to your Splunk instance. 

#### Implementation Details
LQMT supports Splunk using Splunk's [REST Api](http://dev.splunk.com/restapi). LQMT authenticates against Splunks 
/services/auth/login endpoint. Once authenticated, LQMT receives a token from Splunk and uses this for all future 
interactions. 

# Logging

    [Logging]
        logfilebase = "/var/log/lqmt"
        debug = true

Setting       | Explanation
:-----------: | :----------
`logfilebase` |The path and filename prefix to the LQMToolset log file. Multiple log files will be created based on the filename prefix specified in this setting. For example, if `LogFileBase` is "/var/log/lqmt", "/var/log/lqmt.err.log" and "/var/log/lqmt.info.log" will be created.
`debug`       | Enable debug-level logging, which will create an additional log file, *.debug.log*. `Debug` is optional, and it accepts either `true` or `false`.

# Whitelists
LQMToolset allows indicators to be whitelisted. When you define a path to a text file containing the whitelisted indicators, LQMToolset will check the file for modifications and then update the internal database.

    [Whitelist]
        whitelist = "/path/to/whitelist/file.txt"
        dbfile = "/path/to/whitelist/database.db"

Setting     | Explanation
:---------: | :----------
`whitelist` | The full path to the text file containing whitelisted indicators, adhering to the whitelist format below.
`dbfile`    | The location of the SQLite database that holds the whitelist information.

#### Whitelist Format

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

# Intermediate Data Format
The intermediate data format is a subset/simplification of the complete thread data that can be directly used by a cariety of systems. 

Field Name                      | Description
:-----------------------------: | :-----------
`dataItemID`                    | UUID for data item
`fieldID`                       | UUID for file
`detectedTime`                  | UTC epoch of time in the alert itself (if present, filled with reportedTime)
`reportedTime`                  | UTC epoch of time reported to CFM (or other system)
`processedTime`                 | UTC epoch of time processed locally on client (i.e. when this parsed record was created)
`indicator`                     | The value to be acted up (e.g. ip, domain name, URL)
`indicatorType`                 | A type name that informs how to interpret the indicator (e.g. ipv4, emailAddress) (enum)
`indicatorDirection`            | enum {source, destination}
`secondaryIndicator`            | A secondary indicator that restricts (logical AND) the indicator (e.g. a port number) (when appropriate)
`secondaryIndicatorType`        | A type name that informs how to interpret the secondaryIndicator (e.g. tcpport, udport) (enum)
`secondaryIndicatorDirection`   | enum {source, destination}
`directSource`                  | The CFM site abbr (or other applicable indentifier) that uploaded the data
`secondarySource`               | String representing where the CFM site got it from (when appropriate)
`action1`                       | An action to be performed when the indicator is seen (semi-enum)
`duration1`                     | How long the action is to be performed
`action2`                       | An action to be performed when the indicator is seen (semi-enum)
`duration2`                     | How long the action is to be performed
`reason1`                       | First reason for this alert
`reference1`                    | Reference for info for reason
`reason2`                       | Additional reason for this alert
`reference2`                    | Reference for info for reason
`majorTags`                     | A string containing a comma separated list of tags. These are high-level concepts that rend to remain "tag worthy" over time (e.g. Ransomware)
`minorTags`                     | A string containing a comma separated list of tags. These are highly detailed and/or only important for a short time (e.g. Cryptolocker)
`restriction`                   | TLP level
`sensitivity`                   | OUO marking
`reconAllowed`                  | Boolean: true (default) = recon
`priors`                        | Number of previous (known) reports
`confidence`                    | Confidence in accuracy: 0 = none 100 = full
`severity`                      | How significant is the impact (assuming relevant): 0 = no impact, 100 = catastrophic
`relevancy`                     | How relevant is this alert: 0 = not applicable, 100 = perfectly targeted
`relatedID`                     | UUID of a related indicator
`relationType`                  | enum (supersedes, extends, superseded by, extended by)
`comment`                       | A string that represents a comment that was included with the alert.
`fileHasMore`                   | Boolean: false (default) = data has been translated, true = More details on the data item are present in file. 