# Command Line
It's very simple to run LQMToolset; just pass `lqmt` a configuration file:

    lqmt my.conf

When in doubt, `-h`:

    lqmt -h
    usage: lqmt [-h] user_config_file

    positional arguments:
      user_config_file  The user configuration file

      optional arguments:
        -h, --help        show this help message and exit

# Scheduled Cron Job

For users who want to run LQMT on a schedule, it is recommended to set up a cron job. 

### Bash Script
First, you should create a bash script that you will use to run against the cron job. Below is an example script called lqmt.sh that runs a lqmt configuration file located in a sub directory in the users home directory:
```
#!/bin/bash
cd /home/user/lqmt/configs
lqmt lqmt-configuration.toml
```

This is a relatively simple example of a script to run LQMT. If you are using virtualenv or more complicated process, your script should reflect that. 

### Cron
Setting up a cron job to run this script can be done by running the following command: 
`crontab -e`

Once run, this will open up your crontab schedule file in an editor you specify. From here you can append the cron job you want to run the script above. Here is an example of what that job would look like to run the script every five minutes :

`*/5 * * * * /home/user/lqmt/cronscripts/lqmt.sh`

More information on formatting your cron jobs, use the man command (`man cron`), see the [Wikipedia](https://en.wikipedia.org/wiki/Cron) page, and check [other sources](https://www.google.com/?#q=cron+jobs) on the web on cron. 

If you run into any trouble or have questions, feel free to [reach out to us directly](http://lqmtoolset.readthedocs.io/en/latest/#contact). 