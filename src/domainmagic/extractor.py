import re
import os
import logging
import urlparse

from tld import get_IANA_TLD_list
from validators import REGEX_IPV4, REGEX_IPV6


def build_search_re(tldlist=None):
    if tldlist==None:
        tldlist=get_IANA_TLD_list()
    
    allowed_request_chars=r"-a-z0-9._/[\]?+%&="
    reg=r"(?:\b|(?<=:\"))" #start with boundary or " for href
    reg+=r"(?:https?://|ftp://)?" #protocol
    
    #TODO: username:pw@ ....
    
    #domain
    reg+=r"(?:" # domain types 
    
    #standard domain
    reg+=r"[-a-z0-9._]+\." #hostname
    reg+=r"(?:" #tldgroup
    reg+="|".join([x.replace('.','\.') for x in tldlist])
    reg+=r")\b"
    
    #dotquad
    reg+=r"|%s"%REGEX_IPV4
    
    #ip6
    reg+=r"|\[%s\]"%REGEX_IPV6
    
    reg+=r")" # end of domain types
    
    #request
    reg+=r"(?:(?:" #optional stuff after domain
    reg+=r"\/?" # optional / at end of domain
    reg+=r"(?=[^&])" # lookahead: & is not allowed here, this filters false positives if the domain is in a borked request string, eg "....bla.com&blubb=bloing"
    reg+="["+allowed_request_chars+"]+" # TODO: all chars allowed in a request string
    reg+=r"|\/))?"
    reg+=r"(?=(?:[^"+allowed_request_chars+"]|$))" #non-uri character or end of line
    #print "RE: %s"%reg
    return re.compile(reg,re.IGNORECASE)


def domain_from_uri(uri):
    """extract the domain(fqdn) from uri"""
    if '://' not in uri:
        uri="http://"+uri
    domain=urlparse.urlparse(uri.lower()).netloc
    return domain

class URIExtractor(object):
    """Extract URIs"""

    searchre = None
    skiplist = []
    
    def __init__(self):
        #TODO: skiplist
        if URIExtractor.searchre==None:
            URIExtractor.searchre=build_search_re()
        self.logger=logging.getLogger('uriextractor')
        
    def load_skiplist(self,filename):
        URIExtractor.skiplist = self._load_single_file(filename)
    
    def _load_single_file(self,filename):
        """return lowercased list of unique entries"""
        if not os.path.exists(filename):
            self.logger.error("File %s not found - skipping"%filename)
            return []
        content=open(filename,'r').read().lower()
        entries=content.split()
        del content
        return set(entries)
        
    def extracturis(self,plaintext):
        uris=[]
        uris.extend(re.findall(URIExtractor.searchre, plaintext))
        
        finaluris=[]
        #check skiplist$
        for uri in uris:
            try:
                domain=domain_from_uri(uri.lower())
            except Exception,e:
                self.logger.warn("Extract domain from uri %s failed : %s"%(uri,str(e)))
                continue
            skip=False
            for skipentry in URIExtractor.skiplist:
                if domain==skip or domain.endswith(".%s"%skipentry):
                    skip=True
                    break
            
            if not skip:
                finaluris.append(uri)
        return sorted(set(finaluris))


if __name__=='__main__':
    extractor=URIExtractor()
    print extractor.extracturis("hello http://www.wgwh.ch/?doener lol yolo.com .")
     