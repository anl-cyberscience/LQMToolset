class SystemConfig:
    def __init__(self):
        self.system_config = {
            'tools': {
                'Checkpoint': {
                    'module': 'to_checkpoint', 'config_class': 'CheckpointConfig', 'tool_class': 'ToCheckpoint',
                    'accepted_formats': ['Alert']
                },
                'PaloAlto': {
                    'module': 'to_paloalto', 'config_class': 'PaloAltoConfig', 'tool_class': 'ToPaloAlto',
                    'additional_paths': ['tpl'], 'accepted_formats': ['Alert']
                },
                'CSV': {
                    'module': 'to_csv', 'config_class': 'CSVConfig', 'tool_class': 'ToCSV',
                    'accepted_formats': ['Alert']
                },
                'CEF': {
                    'module': 'to_cef', 'config_class': 'CEFConfig', 'tool_class': 'ToCEF',
                    'accepted_formats': ['Alert']
                },
                'ArcSight': {
                    'module': 'to_arcsight', 'config_class': 'ArcSightConfig', 'tool_class': 'ToArcSight',
                    'accepted_formats': ['Alert']
                },
                'SysLog': {
                    'module': 'to_syslog', 'config_class': 'SysLogConfig', 'tool_class': 'ToSysLog',
                    'accepted_formats': ['Alert']
                },
                'FlexText': {
                    'module': 'to_flextext', 'config_class': 'FlexTextConfig', 'tool_class': 'ToFlexText',
                    'accepted_formats': ['Alert']
                },
                'Splunk': {
                    'module': 'to_splunk', 'config_class': 'SplunkConfig', 'tool_class': 'ToSplunk',
                    'accepted_formats': ['Alert']
                },
                'Bro': {
                    'module': 'to_bro', 'config_class': 'BroConfig', 'tool_class': 'ToBro',
                    'accepted_formats': ['Alert']
                },
                'MBL': {
                    'module': 'to_mbl', 'config_class': 'MBLConfig', 'tool_class': 'ToMBL',
                    'accepted_formats': ['Alert']
                },
                'From_MBL': {
                    'module': 'from_mbl', 'config_class': 'FromMBLConfig', 'tool_class': 'FromMBL',
                    'accepted_formats': ['Alert']
                },
                'Pull_Test': {
                    'module': 'pull_test', 'config_class': 'PullTestConfig', 'tool_class': 'PullTest',
                    'accepted_formats': ['Alert']
                },
                'Snort': {
                    'module': 'to_snort', 'config_class': 'SnortConfig', 'tool_class': 'ToSnort',
                    'accepted_formats': ['StixFile', 'RuleFile']
                },
                'From_Snort': {
                    'module': 'from_snort', 'config_class': 'FromSnortConfig', 'tool_class': 'FromSnort',
                    'accepted_formats': ['StixFile']
                },
                'Mattermost': {
                    'module': 'to_mattermost', 'config_class': 'MattermostConfig', 'tool_class': 'ToMattermost',
                    'accepted_formats': ['PdfFile', 'StixFile', 'RuleFile']
                },
                'From_Mattermost': {
                    'module': 'from_mattermost', 'config_class': 'FromMattermostConfig', 'tool_class': 'FromMattermost',
                    'accepted_formats': ['PdfFile']
                },
                'Email': {
                    'module': 'to_email', 'config_class': 'EmailConfig', 'tool_class': 'ToEmail',
                    'accepted_formats': ['PdfFile', 'StixFile', 'RuleFile']
                },
            },
            'UnprocessedCSV': {
                'name': 'for-unprocessed',
                'fields': ['dataItemID', 'fileID', 'detectedTime', 'reportedTime', 'processedTime', 'indicator',
                           'indicatorType', 'indicatorDirection', 'secondaryIndicator', 'secondaryIndicatorType',
                           'secondaryIndicatorDirection', 'directSource', 'secondarySource', 'action1', 'duration1',
                           'action2', 'duration2', 'reason1', 'reference1', 'reason2', 'reference2', 'majorTags',
                           'minorTags', 'restriction', 'sensitivity', 'reconAllowed', 'priors', 'confidence',
                           'severity', 'relevancy', 'relatedID', 'relationType', 'comment', 'fileHasMore']
            },
            'parsers': {
                'Cfm20Alert': {
                    'module': 'lqmt.lqm.parsers.FlexTransform',
                    'parser_class': 'FlexTransformParser',
                    'configs': {
                        'LQMTools': 'resources/sampleConfigurations/lqmtools.cfg',
                        'Cfm20Alert': 'resources/sampleConfigurations/cfm20alert.cfg'
                    },
                    'format': 'Cfm20Alert',
                    'default_enabled': True
                },
                'Cfm13Alert': {
                    'module': 'lqmt.lqm.parsers.FlexTransform',
                    'parser_class': 'FlexTransformParser',
                    'configs': {
                        'LQMTools': 'resources/sampleConfigurations/lqmtools.cfg',
                        'Cfm13Alert': 'resources/sampleConfigurations/cfm13.cfg'
                    },
                    'format': 'Cfm13Alert',
                    'default_enabled': True
                },
                'stixtlp': {
                    'module': 'lqmt.lqm.parsers.FlexTransform',
                    'parser_class': 'FlexTransformParser',
                    'configs': {
                        'LQMTools': 'resources/sampleConfigurations/lqmtools.cfg',
                        'stix-tlp': 'resources/sampleConfigurations/stix_tlp.cfg',
                        'STIX': 'resources/sampleConfigurations/stix_tlp.cfg'

                    },
                    'format': ['stix-tlp', 'STIX'],
                    'default_enabled': True
                },
                'MBL': {
                    'module': 'lqmt.lqm.parsers.FlexTransform',
                    'parser_class': 'FlexTransformParser',
                    'configs': {
                        'LQMTools': 'resources/sampleConfigurations/lqmtools.cfg',
                        'mbl': 'resources/sampleConfigurations/MBL.cfg',
                        'Cfm20Alert': 'resources/sampleConfigurations/cfm20alert.cfg',
                        'stix-tlp': 'resources/sampleConfigurations/stix_tlp.cfg'

                    },
                    'format': 'mbl',
                    'default_enabled': True
                },
                'IIDactiveBadHosts': {
                    'module': 'lqmt.lqm.parsers.FlexTransform',
                    'parser_class': 'FlexTransformParser',
                    'configs': {
                        'LQMTools': 'resources/sampleConfigurations/lqmtools.cfg',
                        'IIDactiveBadHosts': 'resources/sampleConfigurations/iid_host_active.cfg'
                    },
                    'format': 'IIDactiveBadHosts',
                    'default_enabled': False
                },
                'IIDcombinedURL': {
                    'module': 'lqmt.lqm.parsers.FlexTransform',
                    'parser_class': 'FlexTransformParser',
                    'configs': {
                        'LQMTools': 'resources/sampleConfigurations/lqmtools.cfg',
                        'IIDcombinedURL': 'resources/sampleConfigurations/iid_combined_recent.cfg'
                    },
                    'format': 'IIDcombinedURL',
                    'default_enabled': False
                },
                'IIDdynamicBadHosts': {
                    'module': 'lqmt.lqm.parsers.FlexTransform',
                    'parser_class': 'FlexTransformParser',
                    'configs': {
                        'LQMTools': 'resources/sampleConfigurations/lqmtools.cfg',
                        'IIDdynamicBadHosts': 'resources/sampleConfigurations/iid_host_dynamic.cfg'
                    },
                    'format': 'IIDdynamicBadHosts',
                    'default_enabled': False
                },
                'IIDrecentBadIP': {
                    'module': 'lqmt.lqm.parsers.FlexTransform',
                    'parser_class': 'FlexTransformParser',
                    'configs': {
                        'LQMTools': 'resources/sampleConfigurations/lqmtools.cfg',
                        'IIDrecentBadIP': 'resources/sampleConfigurations/iid_ipv4_recent.cfg'
                    },
                    'format': 'IIDrecentBadIP',
                    'default_enabled': False
                },
                'STIXParser': {
                    'module': 'lqmt.lqm.parsers.STIXParser',
                    'parser_class': 'STIXParser',
                    'configs': {
                        'STIXparserConfig': 'resources/parser_configs/stixparser.toml'
                    },
                    'format': ['stix-tlp', 'STIX'],  # OtherFormat
                    'default_enabled': False
                },
                'RuleParser': {
                    'module': 'lqmt.lqm.parsers.RuleParser',
                    'parser_class': 'RuleParser',
                    'configs': {
                        'RuleParserConfig': 'resources/parser_configs/ruleparser.toml'
                    },
                    'format': ['SnortRules', 'YaraRules'],  # OtherFormat, SnortJson, AnyFormat
                    'default_enabled': False
                },
                'PdfParser': {
                    'module': 'lqmt.lqm.parsers.PdfParser',
                    'parser_class': 'PdfParser',
                    'configs': {
                        'PdfParserConfig': 'resources/parser_configs/pdfparser.toml'
                    },
                    'format': ['PDF', 'OtherPDF'],  # Could allow Binary/Agnostic formats
                    'default_enabled': False
                }
            }
        }

    def getConfig(self):
        return self.system_config
