import lqmt.whitelist.master as master
import sys
from lqmt.whitelist.master import IndicatorTypes

def test(wl,indtype,indicator,expectedVal):
    try:
        iswl=wl.isWhitelisted(indtype,indicator)
        if iswl == expectedVal:
            print("{0} ({1})  passed".format(indicator,indtype))
        else:
            print("{0} ({1})  failed".format(indicator,indtype))
    except NotImplementedError as e:
            print("{0} ({1}) failed: {2}\n".format(indicator,indtype,e))

wl=master.MasterWhitelist(configFile="testdata/config.toml")
#IPV4 Addresses
test(wl,IndicatorTypes.ipv4, "192.168.1.1",True)  # matches by ip
test(wl,IndicatorTypes.ipv4, "192.168.2.5",True) # matches by subnet
test(wl,IndicatorTypes.ipv4, "192.168.1.2",False) # doesn't match

#IPV4 subnets
test(wl,IndicatorTypes.ipv4subnet,"192.168.2.0/26",True) # matches by inclusion in another subnet
test(wl,IndicatorTypes.ipv4subnet,"192.168.2.0/23",True) # matches due to contiguous 192.168.2/24 & 192.168.3.24 ranges equals 192.168.2/23 
test(wl,IndicatorTypes.ipv4subnet,"192.168.2.0/22",False) # doesn't match - to big
test(wl,IndicatorTypes.ipv4subnet,"192.168.20/24",False) # doesn't match

#IPV6 Addresses
#??
#IPV6 subnets
#??

#domains
test(wl,IndicatorTypes.domain,"thegoodguys.com",True)  # matches domain
test(wl,IndicatorTypes.domain,"badguy.com",False)  # doesn't match

#Host
test(wl,IndicatorTypes.host,"oneof.thegoodguys.com",True)   # Matches by domain
test(wl,IndicatorTypes.host,"really.goodguy.com",True) # matches by host
test(wl,IndicatorTypes.url,"very.badguy.com",False) # matches URL

#URL
test(wl,IndicatorTypes.url,"http://www.goodsite.com/blah?someparm=9&parm2=foo#anchor",True)
test(wl,IndicatorTypes.url,"http://www.badsite.com/blah?someparm=9&parm2=foo#anchor",False)


