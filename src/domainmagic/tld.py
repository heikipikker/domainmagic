
from domainmagic import updatefile
import collections

@updatefile('/tmp/tlds-alpha-by-domain.txt','http://data.iana.org/TLD/tlds-alpha-by-domain.txt',minimum_size=1000)
def get_IANA_TLD_list():
    tlds=[]
    content=open('/tmp/tlds-alpha-by-domain.txt').readlines()
    for line in content:
        if line.strip()=='' or line.startswith('#'):
            continue
        tlds.extend(line.lower().split())
    return list(sorted(tlds))
    

class TLDMagic(object):
    def __init__(self):
        self.tldtree={}
        self._add_iana_tlds()
        
    def _add_iana_tlds(self):
        for tld in get_IANA_TLD_list():
            self.add_tld(tld)
    
    def get_tld(self,domain):
        """get the tld from domain, returning the best possible xTLD"""
        parts=domain.split('.')
        parts.reverse()
        tldparts=self._walk(parts,self.tldtree)
        tldparts.reverse()
        tld= '.'.join(tldparts)
        return tld
    
    def _walk(self,l,node,path=None):
        if path==None:
            path=[]
        
        if len(l)==0:
            return path
        
        if l[0] in node:
            path.append(l[0])
            return self._walk(l[1:],node[l[0]],path)
        
        return path
                
    def _dict_update(self,d, u):
        for k, v in u.iteritems():
            if isinstance(v, collections.Mapping):
                r = self._dict_update(d.get(k, {}), v)
                d[k] = r
            else:
                d[k] = u[k]
        return d
    
    def _list_to_dict(self,l):
        """translate a list into a tree path"""
        d={}
        if len(l)==0:
            return d
        else:
            d[l[0]]=self._list_to_dict(l[1:])
            return d

    def add_tld(self,tld):
        """add a new tld to the list"""
        parts=tld.split('.')
        parts.reverse()
        update=self._list_to_dict(parts)
        self.tldtree=self._dict_update(self.tldtree, update)

    def add_tlds_from_file(self,filename):
        for line in open(filename,'r').readlines():
            if line.startswith('#') or line.strip()=='':
                continue
            tlds=line.split()
            for tld in tlds:
                self.add_tld(tld)
            
    
    
if __name__ == '__main__':
    t = TLDMagic()
    t.add_tld('bay.livefilestore.com')
    t.add_tld('co.uk')
    
    for test in ['kaboing.bla.bay.livefilestore.com','yolo.doener.com','blubb.co.uk']:
        print "%s -> %s"%(test,t.get_tld(test))
    