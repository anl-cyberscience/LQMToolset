To_Mattermost
============
Tool that allows pushing of binary files to a Mattermost server

### Config

    [[Tools.Mattermost]]
        name = 'mattermost-tool'
        scheme = 'https'
        url = 'URL OF MATTERMOST INSTANCE'
        port = 'PORT OF MATTERMOST INSTANCE'
        login = 'username'
        password = 'password'
        channel_id = 'CHANNEL ID TO SEND FILE IN MATTERMOST'

Setting                 | Explanation
----------------------: | :----------
`name`                  | A unique name identifying this server
`scheme`                | Protocol used to access server (i.e. 'http' or 'https')
`url`                   | The URL of the mattermost server to access
`port`                  | Port to use for access, often '8065' or '443'
`login`                 | The username with permissions to upload a file to the channel on the mattermost server
`password`              | The corresponding password to the username listed above
`channel_id`            | The alphanumeric string representing the channel on the mattermost server to upload the files
