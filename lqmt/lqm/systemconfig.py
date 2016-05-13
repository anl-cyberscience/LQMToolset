class SystemConfig:
    def __init__(self):
        self.system_config = {
            'tools': {
                'path': 'tools',
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
                }
            },
            'UnprocessedCSV': {
                'name': 'for-unprocessed',
                'fields': ['dataItemID', 'fileID', 'detectedTime', 'reportedTime', 'processedTime', 'indicator',
                           'indicatorType', 'indicatorDirection', 'secondaryIndicator', 'secondaryIndicatorType',
                           'secondaryIndicatorDirection', 'directSource', 'secondarySource', 'action1', 'duration1', 'action2',
                           'duration2', 'reason1', 'reference1', 'reason2', 'reference2', 'majorTags', 'minorTags',
                           'restriction', 'sensitivity', 'reconAllowed', 'priors', 'confidence', 'severity', 'relevancy',
                           'relatedID', 'relationType', 'comment', 'fileHasMore']
            },
            'parsers': {
                'path': 'lqm',
                'additional_paths': ['ft'],
                'cfm20': {
                    'module': 'lqmt.lqm.parsers.FlexTransform',
                    'parser_class': 'FlexTransformParser',
                    'configs': {
                        'LQMTools': 'resources/sampleConfigurations/lqmtools.cfg',
                        'Cfm20Alert': 'resources/sampleConfigurations/cfm20alert.cfg'
                    },
                    'format': 'Cfm20Alert'
                },
                'cfm13': {
                    'module': 'lqmt.lqm.parsers.FlexTransform',
                    'parser_class': 'FlexTransformParser',
                    'configs': {
                        'Cfm13Alert': 'resources/sampleConfigurations/cfm13.cfg',
                        'LQMTools': 'resources/sampleConfigurations/lqmtools.cfg'
                    },
                    'format': 'Cfm13Alert'
                }
            }
        }

    def getConfig(self):
        return self.system_config
