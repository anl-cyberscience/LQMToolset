The LQMToolset configuration file contains the local configuration options, including data source definitions, tool instances, and tool chains.

# Data Source
This setting specifies root source directories and what to do with the files once they've been processed.

    [[Source.Directory]]
        dirs = ["/tmp", "/var/spool"]
        post_process = "delete"
        post_process_location = "/home/lqmt/post_process/"

Setting        | Explanation
----------------------: | :----------
`dirs`                  | A list of directory paths, whose contents will be scanned for input files to process.
`post_process`          | An action for LQMToolset to perform after processing a file. Allowed values include `nothing`, `delete`, `move`, and `track`. `nothing` will simply leave the files untouched after processing, and `delete` will remove them. `move` will mark the input files to be moved after processing to another directory. `track` will mark the input files to be tracked in another text file. `move` is the default value when nothing is set in the user configuration file. 
`post_process_location` | Used in conjunction with the `track` post process option. Used to specify a custom location for where your track file will be placed. 


# Source Filters
This setting specifies meta-data file based filtering of files before being processed.  This allows a user to include or exclude files from being parsed and utilized in tools.  The parameters are not required and do not need to be present in the configuration file.

    [[Source.Filters]]
        site_includes = [ 'SITE1' ]
        site_excludes = [ 'SITE2' ]
        payload_types = [ 'Alert' ]
        payload_formats = [ 'STIX' ]
        sensitivities = [ 'noSensitivity' ]
        restrictions = [ 'WHITE' ]
        reconnaissance = [ 'Touch' ]
        max_file_age = "2 mon"

Setting        | Explanation
----------------------: | :----------
`site_includes`     | (Optional) A list of `SendingSite` entries that are allowed.  An empty list or no entry results in `True` to not filter for this setting.
`site_excludes`     | (Optional) A list of `SendingSite` entries that are to be filtered out.  An empty list or no entry results in `True` to not filter for this setting. 
`payload_types`     | (Optional) A list of `PayloadType` entries that are allowed (e.g. `Alert`, `Report`, etc).  An empty list or no entry results in `True` to not filter for this setting. 
`payload_formats`   | (Optional) A list of `PayloadFormat` entries that are allowed (e.g. `STIX`, `Cfm13Alert`, etc).  An empty list or no entry results in `True` to not filter for this setting.
`sensitivities`     | (Optional) A list of `DataSensitivity` entries that are allowed (e.g. `ouo`, `noSensitivity`, etc).  An empty list or no entry results in `True` to not filter for this setting.
`restrictions`      | (Optional) A list of `SharingRestrictions` entries that are allowed (e.g. `WHITE`, `AMBER`, etc).  An empty list or no entry results in `True` to not filter for this setting.
`reconnaissance`    | (Optional) A list of `ReconPolicy` entries that are allowed (e.g. `Touch`, `NoTouch`, etc).  An empty list or no entry results in `True` to not filter for this setting.
`max_file_age`      | (Optional) A string formatted `%d %s` for the maximum age file to be processed.  This supports an offset for seconds `'s', 'sec', 'secs', 'second', 'seconds'`, minutes `'m', 'min', 'minute', 'minutes'`, hours `'h', 'hr', 'hrs', 'hour', 'hours'`, days `'d', 'day', 'days'`, weeks `'w', 'week', 'weeks'`, months `'mon', 'month', 'months'`, years `'y', 'yr', 'yrs', 'year', 'years'`.

# Parsers
LQMT uses special parsers for each type of alert file to get all the data into one common format. By default, the majority of the parsers are enabled, but some parsers are disabled by default. Detailed below are the types of parsers LQMT uses, which are enabled by default, and how you can configure LQMT to disable or enable them. 

Parsers             | Enabled by Default
------------------: | :----------------
`Cfm13Alert`        | `True`
`Cfm20Alert`        | `True`
`STIX`              | `True`
`stix-tlp`          | `True`
`IIDactiveBadHosts` | `False`
`IIDcombinedUrl`    | `False`
`IIDdynamicBadHosts`| `False`
`IIDrecentBadIP`    | `False`
`STIXParser`        | `False`
`RuleParser`        | `False`

Setting | Explanation
--------: | :-----------
`enable`  | A list of parsers to enable.
`disable` | A list of parsers to disable.

## Configuration 
    [Parsers]
        # The enabled and disabled params use lists to track which parsers to override.
        enable = [ 'IIDcombinedUrl', 'IIDdynamicBadHosts', 'IIDrecentBadIP' ]
        disable = [ 'STIX', 'Cfm20Alert' ]

## Individual Parser Configurations
As necessary, each parser can take in a configuration file to control the Parser behavior.  Refer to they systemconfig.py to view the default configuration file associations.  Additionally, sample configurations are contained at lqmt/resources/parser_configs.

### STIX Parser
The STIX parser allows for certain controlling behaviors.  An example is as follows.

    [[Filters]]
        sources = [ 'US-CERT' ]
        elements = [ 'indicators', 'incidents' ]
        rules = [ 'snort' ]

Setting | Explanation
------: | :----------
`sources`  | (Optional) A list containing case-insensitive names to match in the Information_Source element of the STIX_Header.
`elements` | (Optional) A list of the case-insensitive XML element titles to specifically extract from the STIX file `$.<string>`.  At this time it must be one of the top level values `STIX_Header`, `Observables`, `Indicators`, `TTPs`, `Exploit_Targets`, `Incidents`, `Courses_Of_Action`, `Campaigns`, `Threat_Actors`, `Related_Packages`.
`rules`    | (Optional) A list of case-insensitive Rule types to extract, currently only supports entries for `snort`, `yara` to automatically identify.

### Rule Parser
The Rule parser allows for parsing Snort and Yara rules from an input file.  An example is as follows.

    [[Filters]]
        sources = [ 'US-CERT' ]
        rules = [ 'snort', 'yara' ]
        start_offset = 0

Setting | Explanation
------: | :----------
`sources`         | (Optional) A list containing case-insensitive names to match in the SendingSite, Originator, Custodian elements of the CFM Meta Data File.
`rules`           | (Optional) A list of the case-insensitive rule titles to specifically extract. At this time it must be one of the values `snort`, `yara`.
`start_offset`    | (Optional) An integer represents the line offset inside a rules file. This is intended to be used in scenarios a file may have a header to skip before rules.

# Tool Chains
Tool Chains are built from tool instances, which are created from the available tools in LQMToolset. Chaining these tool instances together creates Tool Chains. To configure a new device, an entry must be added in the configuration file.

    [[ToolChains]]
        name = "arcsight-1"
        chain = [ "cef-mapping", "arcsight-1" ]

Setting | Explanation
------: | :----------
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
-------------------: | :----------
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
----------------------: | :----------
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
-------------------: | :----------
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
------: | :----------
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
--------------: | :-----------
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
        fields              = ['action1', 'indicator', 'reportedTime']
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
--------------------: | :-----------
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
`incrementFile`       | Used to increment the output file. When set to `True`, the output file name will be incremented with a timestamp. When set to `False` the output will be appended to any prexisting file of the same name. Defaults to `False`

### Splunk
Ingest CTI data into your Splunk instance in a keyword value format. 

    [[Tools.Splunk]]
        name        = "splunk-tool"
        host        = "https://test-splunk.dev.yourdomain.gov"
        port        = 8089
        username    = "serviceuser"
        password    = "greatpassword123"
        cert_check  = true
        source      = "lqmt-splunk-tool"
        sourcetype  = "lqmt-test"
        index       = "main"
        fields      = ['action1', 'indicator', 'reportedTime']

Setting                 | Explanation
----------------------: | :-----------
`name`                  | A unique name identifying this tool instance. 
`host`                  | Host address of your Splunk instance.
`port`                  | Port used to communicate with your Splunk instances REST API interface. Defaults to `8089`.
`username`              | Username that you want to authenticate with.
`password`              | Password that you want to authenticate with.
`cert_check`            | Used to disable the the certificate check. This is helpful for testing on a machine that you haven't imported your Splunk SSL cert on yet. Defaults to `false`.
`source`                | Name of the source you want the data to be identified by. Defaults to `lqmt`. 
`sourcetype`            | The sourcetype that you want to ingest the data into. 
`index`                 | The index that you want to ingest data into.
`fields`                | Fields, identified from the intermediate format, to be extracted. If `fields` are not provided, then it defaults to a value of ['all'], which will automatically extract all supported field types. 


#### Device Setup and Configuration 
LQMT authenticates using Splunk's token-based authentication endpoint. This requires you to provide a username and 
password. It is recommended that you create a new role specifically for REST API usage as well as a new user that 
belongs to this role. Having a specific user and role just for REST API access will make auditing your REST API usage
much easier.

##### Role Creation
The following steps will walk you through creating a role with enough permissions to permit usage of the REST API.

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
role if you are only using this account for user Splunk REST API. 
7. Set a password for your user.
8. One completed, hit `Save`

You should now have a user created specifically for using Splunk's REST API. This user can now be used in your LQMT 
instance for pushing data to your Splunk instance. 

#### Implementation Details
LQMT supports Splunk using Splunk's [REST API](http://dev.splunk.com/restapi). LQMT authenticates against Splunks 
/services/auth/login endpoint. Once authenticated, LQMT receives a token from Splunk and uses this for future
interactions. When the token exprires, LQMT just reauthenticates and receives a new token. 
The token's lifetime is determined by how you configure your Splunk instance - more information can be 
[found here](http://docs.splunk.com/Documentation/Splunk/6.5.1/Admin/Configureusertimeouts)

### Bro 
Convert CTI data into Bro's [Intelligence Framework](https://www.bro.org/sphinx/frameworks/intel.html) format. Data in this format can be easily read by your Bro instance.

    [[Tools.Bro]]
        name            = "bro-tool"
        file            = "/home/bro/lqmt-feed.txt"
        header_fields   = ['indicator', 'reportedTime', 'directSource']
        increment_file  = true


Setting                 | Explanation
----------------------: | :-----------
`name`                  | A unique name identifying this tool instance. 
`header_fields`         | Specify the fields you want converted and included in the output. Valid fields are extrated from the [Intermediate Data Format](#intermediate-data-format). By default, LQMT will extract all valid fields from the intermediate data foramt. 
`file`                  | Path and name of where you want the file output(Ex: /home/bro/lqmt-bro-feed.txt). By default, LQMT will output the file in the directory where LQMT as a file named `lqmt-bro-feed.txt`.
`increment_file`        | Used to increment the output file. When set to `True`, the output file name will be incremented with a timestamp. When set to `False` the output will be appended to any prexisting file of the same name. Defaults to `False`
`null_value`            | Value to be used to represent that a field is empty. Bro's default value is a hyphen ('-'), so by default LQMT uses a hyphen.

### Snort
Extract [Snort](https://www.snort.org/documents) rules from a STIX CTI datafile and append to a Snort rules definition file.
The ingested CTI datafile must contain Test Mechanism entries that contain Snort rules - [STIX Documentation](http://stixproject.github.io/data-model/1.1.1/snortTM/SnortTestMechanismType/).
An example of the STIX data model is in this [Implementation](https://stixproject.github.io/documentation/idioms/snort-test-mechanism/) section.
```xml
    <indicator:Test_Mechanisms>
        <indicator:Test_Mechanism id="example:testmechanism-a1475567-50f7-4dae-b0d0-47c7ea8e79e1" xmlns:snortTM='http://stix.mitre.org/extensions/TestMechanism#Snort-1' xsi:type='snortTM:SnortTestMechanismType'>
            <indicator:Efficacy timestamp="2014-06-20T15:16:56.987966+00:00">
                <stixCommon:Value xsi:type="stixVocabs:HighMediumLowVocab-1.0">Low</stixCommon:Value>
            </indicator:Efficacy>
            <indicator:Producer>
                <stixCommon:Identity id="example:Identity-a0740d84-9fcd-44af-9033-94e76a53201e">
                    <stixCommon:Name>FOX IT</stixCommon:Name>
                </stixCommon:Identity>
                <stixCommon:References>
                    <stixCommon:Reference>http://blog.fox-it.com/2014/04/08/openssl-heartbleed-bug-live-blog/</stixCommon:Reference>
                </stixCommon:References>
            </indicator:Producer>
            <snortTM:Rule><![CDATA[alert tcp any any -> any any (msg:"FOX-SRT - Flowbit - TLS-SSL Client Hello"; flow:established; dsize:< 500; content:"|16 03|"; depth:2; byte_test:1, <=, 2, 3; byte_test:1, !=, 2, 1; content:"|01|"; offset:5; depth:1; content:"|03|"; offset:9; byte_test:1, <=, 3, 10; byte_test:1, !=, 2, 9; content:"|00 0f 00|"; flowbits:set,foxsslsession; flowbits:noalert; threshold:type limit, track by_src, count 1, seconds 60; reference:cve,2014-0160; classtype:bad-unknown; sid: 21001130; rev:9;)]]></snortTM:Rule>
            <snortTM:Rule><![CDATA[alert tcp any any -> any any (msg:"FOX-SRT - Suspicious - TLS-SSL Large Heartbeat Response"; flow:established; flowbits:isset,foxsslsession; content:"|18 03|"; depth: 2; byte_test:1, <=, 3, 2; byte_test:1, !=, 2, 1; byte_test:2, >, 200, 3; threshold:type limit, track by_src, count 1, seconds 600; reference:cve,2014-0160; classtype:bad-unknown; sid: 21001131; rev:5;)]]></snortTM:Rule>
        </indicator:Test_Mechanism>
    </indicator:Test_Mechanisms>
```

    [[Tools.Snort]]
        name = "snort-tool"
        config_paths = ['/etc/nsm/<interface0>', '/etc/nsm/<interface1>']
        config_filename = 'snort.conf'
        rule_paths = ['/etc/nsm/rules']
        rule_filename = 'example.rules'
        max_rules_count = 50
        mode = "append"
        

Setting                 | Explanation
----------------------: | :----------
`name`                  | (Required) A unique name identifying this tool instance. 
`config_paths`          | (Required) List of paths to Snort config file - example is based on Security Onion with one configuration per interface.
`config_filename`       | (Optional) String filename for the config file (at each path), defaults to 'snort.conf' if not configured.
`rule_paths`            | (Required) List of paths for where to insert Rules files.
`rule_filename`         | (Optional) String filename for the rule file (at each path), defaults to TBD if not configured.
`max_rules_count`       | (Optional) Integer representing the maximum number of rules to have in a rules file.  Set to or allow to default to -1 to turn off management.
`mode`                  | (Optional) String defining rule writing mode `full` vs. `append`.  Full overwrites the full file, append smartly enters only unique new rules.

### From Snort
This tool is capable of searching Snort alert and capture logs to zip a data for transmission.  It currently only supports Full logging mode for Snort.
It is advised that review be performed on alert matching and pcap matching code to ensure it meets the users needs.  

    [[Tools.From_Snort]]
        name = "snort-pull-tool"
        alert_paths = ['/var/log/snort/log']
        packet_paths = ['/var/log/snort/log']
        mode = 'match'
        rules = ['/snort/rules/<name>.rules']
        max_file_age = '2 weeks'
        result_path = '/lqmt/results'


Setting                 | Explanation
----------------------: | :----------
`name`                  | (Required) A unique name identifying this tool instance. 
`alert_paths`           | (Required) List of paths to Snort alert log files.
`packet_paths`          | (Required) List of paths to Snort pcap capture log files.
`mode`                  | (Optional) String defining the alert and capture mode - `full` vs. `match`. In match mode, the tool attempts to grab only alert entries and PCAP matches to the alert IP addresses.
`rules`                 | (Required) List of full paths and file names to the Snort rules files to extract Snort IDs for matching in alerts.
`max_file_age`          | (Required) String defining the maximum file modification age to look for matches. Time can be defined similar to Splunk entries `sec`, `min`, `hr`, `day`, `week`, `mon`, `yr`.
`result_path`           | (Required) Folder path to write the final package, allows for providing to a transmission tool (CFM client, NiFi, etc.)

#### Setup and Configuration
The Tool will automatically attempt to add "include <rule_path>/<rule_filename>" to each defined Snort configuration file.
If the Snort configuration file does not exist, the tool will exit with no action.  If the include entry for the rule file exists, the tool will not add a new inclusion.
It is important to note, the Tool adds the full path for each Rules file to the Snort configuration and does not utilize variables such as $RULE_PATH.

#### Implementation Details
The Tool automatically managements the Rules file to ensure each line is a unique entry.  
The method for performing this action utilizes Python Sets which are unordered.  Therefore, the rule entries may change order after updates.
When configured to control the total number of rules in the file, the Tool decides the number of new rules to add and removes existing rules to accomodate.
It is important to note that this removal is performed in an unordered manner, therefore, it does not occur in a FIFO manner.

#### Limitations
STIX allows for Event Filters, Rate Filters, and Event Suppressions to be expressed within the [SnortTestMechanismType](http://stixproject.github.io/data-model/1.1.1/snortTM/SnortTestMechanismType/).
These are currently not utilized in the Tool.  If modifying the Tool to use, the Parser does pass them in the Full Rules object that contains the full context as a dictionary.

# Logging

    [Logging]
        logfilebase = "/var/log/lqmt"
        debug = true
        dailyrotation = true

Setting             | Explanation
------------------: | :----------
`logfilebase`       |The path and filename prefix to the LQMToolset log file. Multiple log files will be created based on the filename prefix specified in this setting. For example, if `LogFileBase` is "/var/log/lqmt", "/var/log/lqmt.err.log" and "/var/log/lqmt.info.log" will be created.
`debug`             | Enable debug-level logging, which will create an additional log file, *.debug.log*. `Debug` is optional, and it accepts either `true` or `false`.
`dailyrotation`    | Enable daily log rotation. When enabled, log file names will be appended with the current date (ex: lqmt_09-01-2017.debug). This makes it easier to parse logs and allows users to create rotation processes.

# Whitelists
LQMToolset allows indicators to be whitelisted. When you define a path to a text file containing the whitelisted indicators, LQMToolset will check the file for modifications and then update the internal database.

    [Whitelist]
        whitelist = "/path/to/whitelist/file.txt"
        dbfile = "/path/to/whitelist/database.db"

Setting     | Explanation
----------: | :----------
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
The intermediate data format is a subset/simplification of the complete threat data that can be directly used by a variety of systems. 

Field Name                      | Description
------------------------------: | :-----------
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

# Actions 
The most common action seen for the fields `action1`, and `action2` is `block`, but occasionaly a `revoke` action will be put out for alerts that a no longer needed or were sent out by mistake. `revoke` actions are taken care of automatically with the supported firewall tools, but you should take special note of them when using a custom outputs like FlexText. Not all data processed should be assumed to be malicious or worthy of a block action, and the `action` fields are meant to be better help determine what actions should be taken on data. 
