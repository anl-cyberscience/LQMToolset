# Last Quarter Mile Toolset

The Last Quarter Mile Toolset (`LQMT`) is used to automate action to endpoint defense tools using data from Cyber Threat Intelligence (CTI). 

### Overview

`LQMT` works by taking CTI data and breaking it down into a common data format. Specialized tools designed to interface with endpoint defense tools  take this common data format and communicate the parsed CTI data to the endpoint tools. `LQMT` is able to string these tools together in a group called ToolChains, so you can automate actions to a variety of different tools all at once. 

Text-based diagram of how CTI Data flows to a chain of tools using LQMT: 

                        ---> Firewall
                       /
    CTI Data ---> LQMT ----> SIEM
                       \
                        ---> Syslog

#### Supported Tools
The following endpoints tools and actions are supported by `LQMT`: 

Tool             | Actions Supported 
-----------------|--------------
Checkpoint       | Automated Firewall Blocks   
Palo Alto        | Automated Firewall Blocks   
Arcsight Logger  | Data Routing       
Splunk           | Data Routing          
Syslog           | Data Routing 
Flextext         | Data Translation

### Open source
The code for `LQMT` is open source, and [available on Github](https://github.com/anl-cyberscience/LQMToolset). New tools and features are actively being developed for `LQMT`, but user contributions are welcome via pull requests.

### Contact
`LQMT` is developed and supported by the CFM team at Argonne National Lab. Any questions about LQMT can be directed to the CFM team at cfmteam@anl.gov. For general information about the CFM project, visit our website at http://www.anl.gov/cfm
