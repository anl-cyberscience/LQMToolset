import argparse
import os
import json
import uuid
import random
import time

class MetaMaker(object):
    def __init__(self, args):
        self.args = args
        self.file = ""
        self.filebase = ""
        self.metafile = ""
        self.directory = "./"

        # metadata structure
        self.metadata = {
            "DataSensitivity": "",
            "DownloadElementExtendedAttribute": "",
            "FileName": "",
            "PayloadFormat": "",
            "PayloadType": "",
            "ReconPolicy": "",
            "SendingSite": "",
            "SentTimestamp": "",
            "SharingRestrictions": "",
            "UploadID": ""
        }

        # valid payload formats
        self.payload_formats = {
            'cfm13alert': 'Cfm13Alert',
            'cfm20alert': 'Cfm20Alert',
            'stix': 'STIX',
            'stix-tlp': 'stix-tlp',
            'iidactivebadhosts': 'IIDactiveBadHosts',
            'iidcombinedurl': 'IIDcombinedURL',
            'iiddynamicbadhosts': 'IIDdynamicBadHosts',
            'iidrecentbadip': 'IIDrecentBadIP',
            "ds_query": "DS_QUERY"
        }

        # valid payload types
        self.payload_types = {
            'alert': "Alert",
            "report": "Report",
            "rule": "Rule",
            "othertype": "OtherType"
        }

        # valid sensitivity
        self.sensitivity = {
            "ouo": "ouo",
            "nosensitivity": "noSensitivity" 
        }

        # valid recon
        self.recon = {
            "touch": "Touch",
            "notouch": "NoTouch"
        }

        self.SharingRestrictions = {
            "red": "RED",
            "amber": "AMBER",
            "green": "GREEN",
            "white": "WHITE"
        }

    def sort_args(self):
        """
        Method for sorting argument values into their respective metadata fields. All values except FileName and PayloadFormat will
        randomize their value if the user does not provide a value. 
        """
        try:   
            self.file = os.path.split(self.args.source_file)[1]
            self.metafile = "." + self.file
            self.metadata['FileName'] = self.file

        except Exception as e:
            print("No file present. Exception: {0}".format(e))

        if self.args.format:
            self.metadata['PayloadFormat'] = self.payload_formats[self.args.format.lower()]

        if self.args.site:
            self.metadata['SendingSite'] = self.args.site
        else:
            self.metadata['SendingSite'] = self.random_site()

        if self.args.type: 
            self.metadata['PayloadType'] = self.payload_types[self.args.type.lower()]
        else:
            self.metadata['PayloadType'] = self.random_dict_item(self.payload_types)

        if self.args.upload_id:
            self.metadata['UploadID'] = self.args.upload_id
        else:
            self.metadata['UploadID'] = str(uuid.uuid4()).upper()

        if self.args.sent_time:
            self.metadata['SentTimestamp'] = self.args.sent_time
        else:
            self.metadata['SentTimestamp'] = str(int(time.time()))

        if self.args.sensitivity:
            self.metadata['DataSensitivity'] = self.sensitivity[self.args.sensitivity.lower()]
        else:
            self.metadata['DataSensitivity'] = self.random_dict_item(self.sensitivity)

        if self.args.recon:
            self.metadata['ReconPolicy'] = self.recon[self.args.recon.lower()]
        else:
            self.metadata['ReconPolicy'] = self.random_dict_item(self.recon)

        if self.args.restrictions:
            self.metadata['SharingRestrictions'] = self.SharingRestrictions[self.args.restrictions.lower()]
        else:
            self.metadata['SharingRestrictions'] = self.random_dict_item(self.SharingRestrictions)
        
        if self.args.directory:
            self.directory = self.args.directory

    def write_file(self):
        """
        Method for writing the metadata to the file
        """
        with open(self.directory+self.metafile, 'w') as f:
            json.dump(self.metadata, f, indent=2)

    def clean_meta(self):
        delkeys = []
        for key, value in self.metadata.items():
            if not value:
                delkeys.append(key)

        for key in delkeys:
            del self.metadata[key]

    def make_meta(self):
        """
        Main function for running everything
        """
        self.sort_args()
        self.clean_meta()
        self.write_file()

    @staticmethod
    def random_dict_item(dictionary):
        """
        Method for randomly choosing a value from a dictionary
        """
        return random.choice(list(dictionary.items()))[1]

    @staticmethod
    def random_site(length=3):
        alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        site = ""
        while length > 0:
            site += random.choice(alpha)
            length -= 1
        return site


def main():
    # argument parser
    parser = argparse.ArgumentParser(prog='metamaker',
                                     description='Create LQMT compatible metadata file from a source alert file.')
    parser.add_argument('source_file', help='Path to source file needing a metadata file.')
    parser.add_argument('format', help='The PayloadFormat of the alert.')
    parser.add_argument('--sensitivity', help='Sensitivity level of the alert.')
    parser.add_argument('--type', help='The PayloadType of the alert.')
    parser.add_argument('--recon', help='Recon level of the alert')
    parser.add_argument('--site', help='The SendingSite of the alert.')
    parser.add_argument('--sent_time', help='The Unix Time timestamp of when the alert was sent.') 
    parser.add_argument('--restrictions', help='The SharingRestrictions of the alert.')
    parser.add_argument('--upload_id', help='The UploadID of the alert.')
    parser.add_argument('--directory', help='Path to the directory where you want the file written out. ')
    args = parser.parse_args()

    # metamaker object
    metamaker = MetaMaker(args)
    metamaker.make_meta()


if __name__ == '__main__':
    main()
