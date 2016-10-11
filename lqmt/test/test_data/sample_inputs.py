CFM13ALERT = """
<!DOCTYPE IDMEF-Message PUBLIC "-//IETF//DTD RFC XXXX IDMEF v1.0//EN" "idmef-message.dtd">
    <IDMEF-Message xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns="http://www.anl.gov/cfm/1.3/IDMEF-Message" xsi:schemaLocation="http://www.anl.gov/cfm/1.3/IDMEF-Message/../../../resources/schemas/CFMMessage13.xsd">
      <Alert>
        <Analyzer analyzerid="Fake">
          <Node>
            <location>Fake National Lab</location>
            <name>Fake Name</name>
          </Node>
        </Analyzer>
        <AnalyzerTime>2016-02-21T22:50:02+0600</AnalyzerTime>
        <AdditionalData meaning="report schedule" type="string">5 minutes</AdditionalData>
        <AdditionalData meaning="number of alerts in this report" type="integer">2</AdditionalData>
        <AdditionalData meaning="report type" type="string">alerts</AdditionalData>
        <AdditionalData meaning="report start time" type="date-time">2016-02-21T22:45:53+0700</AdditionalData>
      </Alert>
      <Alert>
        <CreateTime>2016-02-21T22:45:53-0400</CreateTime>
        <Source>
          <Node>
            <Address category="ipv4-addr">
              <address>10.10.10.10</address>
            </Address>
          </Node>
        </Source>
        <Target>
          <Service>
            <port>22</port>
            <protocol>TCP</protocol>
          </Service>
        </Target>
        <Classification text="SSH scans against multiple hosts, direction:ingress, confidence:87, severity:high">
          <Reference meaning="Scanning" origin="user-specific">
            <name>SSH Attack</name>
            <url> </url>
          </Reference>
        </Classification>
        <Assessment>
          <Action category="block-installed"/>
        </Assessment>
        <AdditionalData meaning="restriction" type="string">private</AdditionalData>
        <AdditionalData meaning="recon" type="integer">0</AdditionalData>
        <AdditionalData meaning="prior offenses" type="integer">11</AdditionalData>
        <AdditionalData meaning="duration" type="integer">86400</AdditionalData>
        <AdditionalData meaning="alert threshold" type="integer">0</AdditionalData>
        <AdditionalData meaning="OUO" type="integer">0</AdditionalData>
        <AdditionalData meaning="top level domain owner" type="string">The Republic of Fake</AdditionalData>
      </Alert>
    </IDMEF-Message>
    """

CFM20ALERT = """
<CFMAlert xmlns="http://www.anl.gov/cfm/2.0/current/CFMAlert">
    <Version>2.0</Version>
    <Alert>
        <AlertID>1cdf6f8f-20da-488e-9132-bbf850621418</AlertID>
        <AlertTimestamp>1468350602</AlertTimestamp>
        <IndicatorSet>
            <Indicator>
                <Type>ipv6sourceaddress</Type>
                <Constraint>IPv6ColonHexEquality</Constraint>
                <Value>8675:a289:5:102c::bd8:baac</Value>
            </Indicator>
        </IndicatorSet>
        <ReasonList>
            <Reason>
                <ReasonCategory>Exploit</ReasonCategory>
                <ReasonDescription>The WAF detected a scan for vulnerable web applications</ReasonDescription>
            </Reason>
        </ReasonList>
        <ActionList>
            <Action>
                <ActionCategory>Block</ActionCategory>
                <ActionTimestamp>1468350602</ActionTimestamp>
            </Action>
        </ActionList>
        <AlertExtendedAttribute>
            <Field>confidence</Field>
            <Value>80</Value>
        </AlertExtendedAttribute>
        <AlertExtendedAttribute>
            <Field>severity</Field>
            <Value>high</Value>
        </AlertExtendedAttribute>
    </Alert>
</CFMAlert>
"""

STIXTLP = """<stix:STIX_Package
        xmlns:cyboxCommon="http://cybox.mitre.org/common-2"
        xmlns:cybox="http://cybox.mitre.org/cybox-2"
        xmlns:cyboxVocabs="http://cybox.mitre.org/default_vocabularies-2"
        xmlns:AddressObj="http://cybox.mitre.org/objects#AddressObject-2"
        xmlns:ArtifactObj="http://cybox.mitre.org/objects#ArtifactObject-2"
        xmlns:FileObj="http://cybox.mitre.org/objects#FileObject-2"
        xmlns:URIObj="http://cybox.mitre.org/objects#URIObject-2"
        xmlns:marking="http://data-marking.mitre.org/Marking-1"
        xmlns:tlpMarking="http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1"
        xmlns:indicator="http://stix.mitre.org/Indicator-2"
        xmlns:stixCommon="http://stix.mitre.org/common-1"
        xmlns:stixVocabs="http://stix.mitre.org/default_vocabularies-1"
        xmlns:stix="http://stix.mitre.org/stix-1"
        xmlns:CFM="http://www.anl.gov/cfm/stix"
        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
        xsi:schemaLocation="
        http://cybox.mitre.org/common-2 http://cybox.mitre.org/XMLSchema/common/2.1/cybox_common.xsd
        http://cybox.mitre.org/cybox-2 http://cybox.mitre.org/XMLSchema/core/2.1/cybox_core.xsd
        http://cybox.mitre.org/default_vocabularies-2 http://cybox.mitre.org/XMLSchema/default_vocabularies/2.1/cybox_default_vocabularies.xsd
        http://cybox.mitre.org/objects#AddressObject-2 http://cybox.mitre.org/XMLSchema/objects/Address/2.1/Address_Object.xsd
        http://cybox.mitre.org/objects#ArtifactObject-2 http://cybox.mitre.org/XMLSchema/objects/Artifact/2.1/Artifact_Object.xsd
        http://cybox.mitre.org/objects#FileObject-2 http://cybox.mitre.org/XMLSchema/objects/File/2.1/File_Object.xsd
        http://cybox.mitre.org/objects#URIObject-2 http://cybox.mitre.org/XMLSchema/objects/URI/2.1/URI_Object.xsd
        http://data-marking.mitre.org/Marking-1 http://stix.mitre.org/XMLSchema/data_marking/1.1.1/data_marking.xsd
        http://data-marking.mitre.org/extensions/MarkingStructure#TLP-1 http://stix.mitre.org/XMLSchema/extensions/marking/tlp/1.1.1/tlp_marking.xsd
        http://stix.mitre.org/Indicator-2 http://stix.mitre.org/XMLSchema/indicator/2.1.1/indicator.xsd
        http://stix.mitre.org/common-1 http://stix.mitre.org/XMLSchema/common/1.1.1/stix_common.xsd
        http://stix.mitre.org/default_vocabularies-1 http://stix.mitre.org/XMLSchema/default_vocabularies/1.1.1/stix_default_vocabularies.xsd
        http://stix.mitre.org/stix-1 http://stix.mitre.org/XMLSchema/core/1.1.1/stix_core.xsd" id="CFM:STIXPackage-21856f56-eb97-50ca-bfb0-bd425e3d01c0" version="1.1.1" timestamp="2016-03-29T19:33:13+03:00">
        <stix:STIX_Header>
            <stix:Title>Test PDF</stix:Title>
            <stix:Package_Intent xsi:type="stixVocabs:PackageIntentVocab-1.0">Indicators</stix:Package_Intent>
            <stix:Description>Ransomware Update</stix:Description>
            <stix:Handling>
                <marking:Marking>
                    <marking:Controlled_Structure>//node() | //@*</marking:Controlled_Structure>
                    <marking:Marking_Structure xsi:type='tlpMarking:TLPMarkingStructureType' color="AMBER"/>
                </marking:Marking>
            </stix:Handling>
            <stix:Information_Source>
                <stixCommon:Identity>
                    <stixCommon:Name>Fake</stixCommon:Name>
                </stixCommon:Identity>
                <stixCommon:Time>
                    <cyboxCommon:Produced_Time>2016-03-23T16:45:05+04:00</cyboxCommon:Produced_Time>
                </stixCommon:Time>
            </stix:Information_Source>
        </stix:STIX_Header>
        <stix:Indicators>
            <stix:Indicator id="CFM:Indicator-c2cfe2c4-ebde-548e-bacd-53e3d996c883" timestamp="2016-03-29T19:33:13+01:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Title>Original CRISP Report Document</indicator:Title>
                <indicator:Description>CRISP-16-307.pdf</indicator:Description>
                <indicator:Observable id="CFM:Observable-980d16cc-91d8-51c6-b957-8bfa539a5439">
                    <cybox:Object id="CFM:Object-8c4c2194-54a6-56d2-bd2b-4f5c8b130ab5">
                        <cybox:Properties xsi:type="ArtifactObj:ArtifactObjectType" suspected_malicious="false" type="File" content_type="application/pdf">
                            <ArtifactObj:Packaging>
                                <ArtifactObj:Encoding algorithm="Base64"/>
                            </ArtifactObj:Packaging>
                            <ArtifactObj:Raw_Artifact><![CDATA[JVBERi0xLjMKJcTl8uXrp/Og0MTGCjQgMCBvYmoKPDwgL0xlbmd0aCA1IDAgUiAvRmlsdGVyIC9GbGF0ZURlY29kZSA+PgpzdHJlYW0KeAErVAhUKFQwNAIhUwsLVPRgo=]]></ArtifactObj:Raw_Artifact>
                        </cybox:Properties>
                    </cybox:Object>
                </indicator:Observable>
            </stix:Indicator>
            <stix:Indicator id="CFM:Indicator-3e732203-d463-50ba-b6c2-26c11032a204" timestamp="2016-03-29T19:33:13+02:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Type xsi:type="stixVocabs:IndicatorTypeVocab-1.1">IP Watchlist</indicator:Type>
                <indicator:Description>CRISP Report Indicator</indicator:Description>
                <indicator:Observable id="CFM:Observable-810a21f8-85aa-5425-ab07-69c94d72b60c">
                    <cybox:Object id="CFM:Object-2b703a03-81ab-5af9-bb53-e7641cbd8e76">
                        <cybox:Properties xsi:type="AddressObj:AddressObjectType" category="ipv4-addr">
                            <AddressObj:Address_Value condition="Equals">10.10.10.10</AddressObj:Address_Value>
                        </cybox:Properties>
                    </cybox:Object>
                </indicator:Observable>
            </stix:Indicator>
            <stix:Indicator id="CFM:Indicator-82b0c3f9-95d4-5ec7-9e09-30b0bf87cfcd" timestamp="2016-03-29T19:33:13+05:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Type xsi:type="stixVocabs:IndicatorTypeVocab-1.1">IP Watchlist</indicator:Type>
                <indicator:Description>CRISP Report Indicator</indicator:Description>
                <indicator:Observable id="CFM:Observable-03e0bab9-a13e-55cf-93d4-cf707aeb831d">
                    <cybox:Object id="CFM:Object-9eb91b53-603a-53e5-9228-958e81c24949">
                        <cybox:Properties xsi:type="AddressObj:AddressObjectType" category="ipv4-addr">
                            <AddressObj:Address_Value condition="Equals">13.13.13.13</AddressObj:Address_Value>
                        </cybox:Properties>
                    </cybox:Object>
                </indicator:Observable>
            </stix:Indicator>
            <stix:Indicator id="CFM:Indicator-52c46f7c-cca9-5d2e-9d3b-a3b1744dcf52" timestamp="2016-03-29T19:33:13+06:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Type xsi:type="stixVocabs:IndicatorTypeVocab-1.1">IP Watchlist</indicator:Type>
                <indicator:Description>CRISP Report Indicator</indicator:Description>
                <indicator:Observable id="CFM:Observable-691072b3-c6a4-5615-9c78-cb5977864bb5">
                    <cybox:Object id="CFM:Object-44b996e6-7769-54e0-b5c7-bab92fc8791e">
                        <cybox:Properties xsi:type="AddressObj:AddressObjectType" category="ipv4-addr">
                            <AddressObj:Address_Value condition="Equals">12.12.12.12</AddressObj:Address_Value>
                        </cybox:Properties>
                    </cybox:Object>
                </indicator:Observable>
            </stix:Indicator>
            <stix:Indicator id="CFM:Indicator-052c65e0-c667-5e4c-9970-ac9ddd3511b3" timestamp="2016-03-29T19:33:13+07:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Type xsi:type="stixVocabs:IndicatorTypeVocab-1.1">IP Watchlist</indicator:Type>
                <indicator:Description>CRISP Report Indicator</indicator:Description>
                <indicator:Observable id="CFM:Observable-1680f55e-8cd8-5d28-8d33-8488ee747581">
                    <cybox:Object id="CFM:Object-4fa49509-2f5c-5c66-a86f-0babf49a0e33">
                        <cybox:Properties xsi:type="AddressObj:AddressObjectType" category="ipv4-addr">
                            <AddressObj:Address_Value condition="Equals">11.11.11.11</AddressObj:Address_Value>
                        </cybox:Properties>
                    </cybox:Object>
                </indicator:Observable>
            </stix:Indicator>
            <stix:Indicator id="CFM:Indicator-1cf2d34d-007a-5a50-b7c1-cce9faf6f968" timestamp="2016-03-29T19:33:13+08:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Type xsi:type="stixVocabs:IndicatorTypeVocab-1.1">IP Watchlist</indicator:Type>
                <indicator:Description>CRISP Report Indicator</indicator:Description>
                <indicator:Observable id="CFM:Observable-686ec0d4-59a0-5909-bfbc-eb31c37becd5">
                    <cybox:Object id="CFM:Object-1f397c22-5d3d-50eb-98e9-6acd82fa329c">
                        <cybox:Properties xsi:type="AddressObj:AddressObjectType" category="ipv4-addr">
                            <AddressObj:Address_Value condition="Equals">14.14.14.14</AddressObj:Address_Value>
                        </cybox:Properties>
                    </cybox:Object>
                </indicator:Observable>
            </stix:Indicator>
            <stix:Indicator id="CFM:Indicator-92130d2c-c3e6-5ed9-bcdc-c826c5d2c5b4" timestamp="2016-03-29T19:33:13+07:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Description>CRISP Report Indicator</indicator:Description>
                <indicator:Observable id="CFM:Observable-6f106c1e-2ff9-518b-9c36-6edbe59b36e6">
                    <cybox:Object id="CFM:Object-1b6d7388-4c63-5687-9b57-d9dad435bfc4">
                        <cybox:Properties xsi:type="FileObj:FileObjectType">
                            <FileObj:File_Path condition="Equals">D://replacement.exe</FileObj:File_Path>
                        </cybox:Properties>
                    </cybox:Object>
                </indicator:Observable>
            </stix:Indicator>
            <stix:Indicator id="CFM:Indicator-1bed1aca-30e1-5ad3-8bee-6c1dfbff157d" timestamp="2016-03-29T19:33:13+06:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Description>CRISP Report Indicator</indicator:Description>
                <indicator:Observable id="CFM:Observable-fa7faba7-7dc4-5bb9-a436-31c726039150">
                    <cybox:Object id="CFM:Object-3391be65-9462-5d30-b1e3-7ff813943bff">
                        <cybox:Properties xsi:type="FileObj:FileObjectType">
                            <FileObj:File_Path condition="Equals">/user/strange/object.sh</FileObj:File_Path>
                        </cybox:Properties>
                    </cybox:Object>
                </indicator:Observable>
            </stix:Indicator>
            <stix:Indicator id="CFM:Indicator-8b3ac40a-8595-50fe-bea1-fbd1d85cc428" timestamp="2016-03-29T19:33:13+00:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Description>CRISP Report Indicator</indicator:Description>
                <indicator:Observable id="CFM:Observable-6be0296d-d22c-5460-bb3f-7626173874bd">
                    <cybox:Object id="CFM:Object-533cd91f-5a13-548d-8bfb-5e0c3741e74e">
                        <cybox:Properties xsi:type="FileObj:FileObjectType">
                            <FileObj:File_Path condition="Equals">C://window32/tst.dat</FileObj:File_Path>
                        </cybox:Properties>
                    </cybox:Object>
                </indicator:Observable>
            </stix:Indicator>
            <stix:Indicator id="CFM:Indicator-a9b071be-fa18-5b49-9d15-e487836adb49" timestamp="2016-03-29T19:33:13+00:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Description>CRISP Report Indicator</indicator:Description>
                <indicator:Observable id="CFM:Observable-78fb6ef8-b249-5538-8ce7-07addd671a03">
                    <cybox:Object id="CFM:Object-3893bb9a-339d-52bd-84b7-aba7cb19b92b">
                        <cybox:Properties xsi:type="FileObj:FileObjectType">
                            <FileObj:File_Path condition="Equals">webmail.p55.be</FileObj:File_Path>
                        </cybox:Properties>
                    </cybox:Object>
                </indicator:Observable>
            </stix:Indicator>
            <stix:Indicator id="CFM:Indicator-2e95d2ac-1b08-5f38-8522-2f4b2ef3686c" timestamp="2016-03-29T19:33:13+00:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Type xsi:type="stixVocabs:IndicatorTypeVocab-1.1">URL Watchlist</indicator:Type>
                <indicator:Description>CRISP Report Indicator</indicator:Description>
                <indicator:Observable id="CFM:Observable-5b7cf542-0c1d-5331-966a-9596b2530f10">
                    <cybox:Object id="CFM:Object-9711b917-fff8-5c3e-acee-dee057dbbda7">
                        <cybox:Properties xsi:type="URIObj:URIObjectType" type="URL">
                            <URIObj:Value condition="Equals">bad.domain.be/poor/path</URIObj:Value>
                        </cybox:Properties>
                    </cybox:Object>
                </indicator:Observable>
            </stix:Indicator>
            <stix:Indicator id="CFM:Indicator-5fd6c616-d923-5e70-916d-dca3a2d1ee02" timestamp="2016-03-29T19:33:13+00:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Type xsi:type="stixVocabs:IndicatorTypeVocab-1.1">URL Watchlist</indicator:Type>
                <indicator:Description>CRISP Report Indicator</indicator:Description>
                <indicator:Observable id="CFM:Observable-b28b198f-98a4-5126-8724-18cf8adb0fea">
                    <cybox:Object id="CFM:Object-07e004ab-51d6-5546-b7c4-7f2f9f99436e">
                        <cybox:Properties xsi:type="URIObj:URIObjectType" type="URL">
                            <URIObj:Value condition="Equals">fake.site.com/malicious.js</URIObj:Value>
                        </cybox:Properties>
                    </cybox:Object>
                </indicator:Observable>
            </stix:Indicator>
            <stix:Indicator id="CFM:Indicator-32d6ca0d-5896-57ff-84c6-8f18a7a70643" timestamp="2016-03-29T19:33:13+00:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Type xsi:type="stixVocabs:IndicatorTypeVocab-1.1">File Hash Watchlist</indicator:Type>
                <indicator:Description>CRISP Report Indicator</indicator:Description>
                <indicator:Observable id="CFM:Observable-cb615fd4-12c8-5232-949f-b38fd5ab6a3f">
                    <cybox:Object id="CFM:Object-5a68f003-c73b-590c-95a4-5db828f9eeb0">
                        <cybox:Properties xsi:type="FileObj:FileObjectType">
                            <FileObj:Hashes>
                                <cyboxCommon:Hash>
                                    <cyboxCommon:Type condition="Equals" xsi:type="cyboxVocabs:HashNameVocab-1.0">MD5</cyboxCommon:Type>
                                    <cyboxCommon:Simple_Hash_Value>595f44fec1e92a71d3e9e77456ba80d1</cyboxCommon:Simple_Hash_Value>
                                </cyboxCommon:Hash>
                            </FileObj:Hashes>
                        </cybox:Properties>
                    </cybox:Object>
                </indicator:Observable>
            </stix:Indicator>
            <stix:Indicator id="CFM:Indicator-1f59ad38-bb9f-5804-8585-9ad6264120a8" timestamp="2016-03-29T19:33:13+00:00" xsi:type='indicator:IndicatorType' version="2.1.1">
                <indicator:Type xsi:type="stixVocabs:IndicatorTypeVocab-1.1">File Hash Watchlist</indicator:Type>
                <indicator:Description>CRISP Report Indicator</indicator:Description>
                <indicator:Observable id="CFM:Observable-eaf5c06f-c0a6-5aaf-8716-a2fda646205d">
                    <cybox:Object id="CFM:Object-b7237e30-b62e-52db-979f-adddff1688e7">
                        <cybox:Properties xsi:type="FileObj:FileObjectType">
                            <FileObj:Hashes>
                                <cyboxCommon:Hash>
                                    <cyboxCommon:Type condition="Equals" xsi:type="cyboxVocabs:HashNameVocab-1.0">MD5</cyboxCommon:Type>
                                    <cyboxCommon:Simple_Hash_Value>627c1bfc48e7a29776d5c36102e13f98</cyboxCommon:Simple_Hash_Value>
                                </cyboxCommon:Hash>
                            </FileObj:Hashes>
                        </cybox:Properties>
                    </cybox:Object>
                </indicator:Observable>
            </stix:Indicator>
        </stix:Indicators>
    </stix:STIX_Package>
    """
