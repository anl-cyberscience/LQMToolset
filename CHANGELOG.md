# CHANGELOG
## [TBD] - TBD
- Added the ability to filter files prior to passing to the parser based on the meta-data file's contents.  The parameters that are checked are SendingSite, PayloadType, PayloadFormat, DataSensitivity, SharingRestrictions, ReconPolicy, and SentTimestamp.
- These configuration filter parameters are not required in the file and if not present are ignored when checking the file against filters.
- Added a STIX specific parser and data object that does not result in an Intermediate Format. Gives the ability to extract data from a STIX File utilizing keywords for better automation. Added automatic recognition of STIX and Yara rules to extract for tools.
- Added a Rule Parser to grab rules from within SnortRules, YaraRules file formats.  
- Added a tool for injecting Snort rules from a STIX or SnortRules file (requires a parsed STIX data object). Handles configuring Snort for a new rules file and manages unique, maximum entries in the rules file.
- Added a tool for collecting Snort alert logs and packet captures and writing to a results directory.  The tool attempts to read Rules files and match triggered Snort IDs within the alert file as well as matching IP addresses within PCAP files.

## [3.4.1] - 2017-09-26
- Added a configuration for log rotation. When enabled, log files will be appended with the current date when written. This feature was requested to make it easier to enable processes that will rotate out log files after a certain time, make the files easier to parse, and to break up the logs so that they do not grow to be so large. Looking into making the format of the rotation more configurable and possibly a feature for LQMT to do the actual file rotation. 
- Added this changelog. All changes were previously detailed in git commit messages. This practice will continue, but this file will make it easier to scan for changes and will be more detailed about the actual changes. 