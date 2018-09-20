"""
Created on Sept 7, 2018

@author: mghenderson
"""
import logging

from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from smtplib import SMTP, SMTPConnectError, SMTPException

from lqmt.lqm.data import AlertAction
from lqmt.lqm.tool import Tool


class ToEmail(Tool):
    def __init__(self, config):
        """
        ToEmail tool
        :param config: configuration file
        """
        super().__init__(config, [AlertAction.get('OtherAction')])
        self._logger = logging.getLogger('LQMT.ToEmail.{}'.format(self.getName()))

    def initialize(self):
        super().initialize()

    def process(self, attachment, meta=None):
        """
        Process function. Handles the processing of data for the tool

        :param attachment: File-like object to be sent via email
        :param meta:
        :return:
        """
        name = attachment.getName()
        _type = type(attachment)

        msg = MIMEMultipart()
        msg['From'] = self._config.sender
        msg['To'] = ", ".join(self._config.recipients)
        msg['Subject'] = self._config.subject.format(filename=name, type=_type)
        if self._config.body:
            msg.attach(MIMEText(self._config.body.format(filename=name, type=_type)))

        attachment_pdf = MIMEApplication(attachment.getBinFile(), "pdf")
        attachment_pdf.add_header('Content-Disposition', 'attachment', filename=name)
        msg.attach(attachment_pdf)

        try:
            with SMTP(self._config.outgoing_host) as smtp:
                smtp.send_message(msg)
        except SMTPConnectError as e:
            self._logger.error("Error connecting to SMTP server. Exception={}".format(e))
        except SMTPException as e:
            self._logger.error("SMTP Error={}".format(e))
        except Exception as e:
            self._logger.error("Error={}".format(e))

    def commit(self):
        pass

    def cleanup(self):
        pass