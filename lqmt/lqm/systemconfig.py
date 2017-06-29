class SystemConfig:
    def __init__(self):
        self.system_config = {
            'tools': {
                'Checkpoint': {
                    'module': 'to_checkpoint', 'config_class': 'CheckpointConfig', 'tool_class': 'ToCheckpoint'
                },
                'PaloAlto': {
                    'module': 'to_paloalto', 'config_class': 'PaloAltoConfig', 'tool_class': 'ToPaloAlto',
                    'additional_paths': ['tpl']
                },
                'CSV': {
                    'module': 'to_csv', 'config_class': 'CSVConfig', 'tool_class': 'ToCSV'
                },
                'CEF': {
                    'module': 'to_cef', 'config_class': 'CEFConfig', 'tool_class': 'ToCEF'
                },
                'ArcSight': {
                    'module': 'to_arcsight', 'config_class': 'ArcSightConfig', 'tool_class': 'ToArcSight'
                },
                'SysLog': {
                    'module': 'to_syslog', 'config_class': 'SysLogConfig', 'tool_class': 'ToSysLog'
                },
                'FlexText': {
                    'module': 'to_flextext', 'config_class': 'FlexTextConfig', 'tool_class': 'ToFlexText'
                },
                'Splunk': {
                    'module': 'to_splunk', 'config_class': 'SplunkConfig', 'tool_class': 'ToSplunk'
                },
                'Bro': {
                    'module': 'to_bro', 'config_class': 'BroConfig', 'tool_class': 'ToBro'
                },
                'MBL': {
                    'module': 'to_mbl', 'config_class': 'MBLConfig', 'tool_class': 'ToMBL'
                }
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
                }
            }
        }

    def getConfig(self):
        return self.system_config
