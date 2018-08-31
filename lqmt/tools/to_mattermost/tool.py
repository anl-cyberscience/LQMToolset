"""
Created on July 26, 2018

@author: grjohnson
"""
import logging
import mattermostdriver
import json
import arrow
from lqmt.lqm.data import AlertAction
from lqmt.lqm.tool import Tool


class ToMattermost(Tool):
    def __init__(self, config):
        """
        ToMattermost tool.
        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('OtherAction')])
        self._logger = logging.getLogger("LQMT.ToMattermost.{0}".format(self.getName()))

        self.client = mattermostdriver.Driver({
            'scheme': self._config.scheme,
            'url': self._config.url,
            'port': self._config.port,
            'login_id': self._config.login,
            'password': self._config.password
        })

        self.tool_user_id = 'Unknown'

    def initialize(self):
        super().initialize()

    def __mm_login(self):
        """
        Log in to Mattermost through the driver.  Setup of driver in config initialization.
        Mattermost return is similar to requests return content.

        :return Boolean: True indicating successful log in or False for unsuccessful
        """
        try:
            ret = self.client.login()
            if ret.status_code != 200:
                self._logger.error("Error logging in to MatterMost. Code={0}".format(str(ret.status_code)))
                return False
            else:
                t = json.loads(ret.text)
                self.tool_user_id = t['id']
        except Exception as e:
            self._logger.error("Error logging in to MatterMost. Exception={0}".format(e))
            return False

        return True

    def __mm_logout(self):
        """
        Logout of Mattermost through the driver.

        :return Boolean: True indicating successful log out or False if error
        """
        try:
            ret = self.client.logout()
            if ret['status'].lower() != 'ok':
                self._logger.error("Error logging out of MatterMost. Status={0}".format(str(ret['status'])))
                return False
        except Exception as e:
            self._logger.error("Error logging out of MatterMost. Exception={0}".format(e))
            return False

        return True

    def __build_post_message(self, fname, meta=None):
        """
        Generic function to build a string to accompany a MM upload of a file.
        Uses context from the file meta-data to add usage guidance (if available).

        :param fname: String filename to be added to the MM post text.
        :param meta: Meta data for file to extract context for MM post text.
        :return message: Finally built string for MM post.
        """
        # default message if no meta data to build larger message
        message = fname + ' uploaded from LQMT'

        if meta:
            t = arrow.Arrow.fromtimestamp(meta['SentTimestamp'])
            m = t.format('MMM D, hh:mm:ss A ZZ')
            message = meta['SendingSite'] + ' posted ' + fname + ' on ' + m + '\n'
            message += 'Sensitivity: ' + meta['DataSensitivity'] + '\n' + \
                       'Restrictions: ' + meta['SharingRestrictions'] + '\n' + \
                       'Recon Policy: ' + meta['ReconPolicy']

        return message

    def __pdf_handler(self, pdf):
        """
        Function to upload a PDF file to the MM channel.  Called when data object is PdfFile type.

        :param pdf: PdfFile object following parsing.
        :return None:
        """
        message = self.__build_post_message(pdf.getName(), meta=pdf.getMeta())
        self.__mm_upload_file(message, pdf.getName(), pdf.getBinFile())

    def __stix_handler(self, stix):
        """
        Function to upload a STIX file to the MM channel.  Called when data object is StixFile type.

        :param stix: PdfFile object following parsing.
        :return None:
        """
        message = self.__build_post_message(stix.getName(), meta=stix.getMeta())
        self.__mm_upload_file(message, stix.getName(), stix.getBinFile())

    def __rule_handler(self, rule):
        """
        Function to upload a Rule file to the MM channel.  Called when data object is RuleFile type.

        :param rule: RuleFile object following parsing.
        :return None:
        """
        message = self.__build_post_message(rule.getName(), meta=rule.getMeta())
        self.__mm_upload_file(message, rule.getName(), rule.getBinFile())

    def __mm_post_error(self, err_resp):
        """
        Generic function to post a message containing Error context to a MM channel when upload/post fail.
        May work for some failures such as insufficient permissions, but won't work if no access to the channel.
        Therefore, attempts post only once and logs to LQMT logs if fails.

        :param err_resp: Return dictionary from MM API. Expected to match MM definition.
        :return None:
        """
        try:
            # build error response message from MM return
            if 'status_code' not in err_resp:
                msg = 'Unknown error occurred'
            else:
                msg = 'Status={0} Message={1}'.format(str(err_resp['status_code']), err_resp['message'])
            self._logger.error('Issue uploading to MM.  Text=' + msg)

            # post the failure context to MM
            post_resp = self.client.posts.create_post({
                'channel_id': self._config.channel_id,
                'message': msg
            })

            # status code only present if create post failed
            # log failure and move on since this was an attempt to post previous failure
            if 'status_code' in post_resp:
                self._logger.error(
                    'Error posting failure alert to MM.  Status={0} Message={1}'.format(str(post_resp['status_code']),
                                                                                        post_resp['message']))
        except Exception as e:
            self._logger.error('Error posting failure alert to MM.  Exception={0}'.format(e))

    def __mm_upload_file(self, msg, fname, binfile):
        """
        Generic function to upload a file to MM post to a configured channel ID. Performs the sequence of
        uploading the file to the channel, and creating a post to associate with the file.

        :param msg: Text to be included with the uploaded file for user consumption.
        :param fname: Filename to be used in upload tuple to MM.
        :param binfile: Binary array of file contents to upload to MM.
        :return None:
        """
        try:
            # upload the file to the MM channel for future post message
            upload_resp = self.client.files.upload_file(self._config.channel_id,
                                                        files={'files': (fname, binfile)})
            # if successful, file info in the return
            if 'file_infos' not in upload_resp:
                self.__mm_post_error(upload_resp)  # attempt to post failure context to MM
            else:
                self._logger.info('Successfully uploaded ' + fname + ' to MM.')
                self.__mm_post_file(msg, upload_resp)  # now create post to MM

        except Exception as e:
            self.__mm_post_error({'message': e, 'status_code': -1})  # attempt to post failure context to MM

    def __mm_post_file(self, msg, up_resp):
        """
        Generic function to finalize the posting of the File to MM channel.
        Calling this function follows successful upload of the file and the MM return context is provided.

        :param msg: String message to be included with the File in the MM post.
        :param up_resp: MM return dictionary following successful upload of the File to the channel.
        :return None:
        """
        try:
            # confirm that file information is in the post to create
            if 'file_infos' not in up_resp:
                self._logger.error('No uploaded file ID to associate to MM post.')
                return

            # create a post to MM channel and link the uploaded file
            post_resp = self.client.posts.create_post({
                'channel_id': self._config.channel_id,
                'message': msg,
                'file_ids': [
                    up_resp['file_infos'][0]['id']
                ]
            })

            # error with MM if status code present
            if 'status_code' in post_resp:
                self.__mm_post_error(post_resp)  # attempt to post failure context to MM
            else:
                self._logger.info('Successfully posted message to MM. ID={0}'.format(post_resp['id']))

        except Exception as e:
            self.__mm_post_error({'message': e, 'status_code': -1})  # attempt to post failure context to MM

    def process(self, file):
        """
        Process function.  Handles the processing of data for the tool.

        :param alerts: Binary PDF file object
        :return None:
        """
        # build mapping of Data Object Types with functions to handle
        file_handler = {'PdfFile': self.__pdf_handler,
                        'StixFile': self.__stix_handler,
                        'RuleFile': self.__rule_handler}

        # log in to MM
        if not self.__mm_login():
            return

        # compare Object received to list of compatible objects
        f_type = type(file).__name__
        if f_type not in self._config.compatible_types:
            self._logger.warning("Unsupported Object Type {0}: No files posted to MM".format(f_type))
            return

        # send to specific handler for each type
        file_handler[f_type](file)

    def commit(self):
        pass

    def cleanup(self):
        self.__mm_logout()

