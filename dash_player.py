import xml.etree.ElementTree as ET
import urllib.parse

class SegmentBase:
    def __init__(self, element):
        self.initialization = None
        self.index_range = None
        
        if element is not None:
            # Parse index range
            index_range = element.get('indexRange')
            if index_range:
                start, end = map(int, index_range.split('-'))
                self.index_range = (start, end)
            
            # Parse initialization range
            init_elem = element.find('{urn:mpeg:dash:schema:mpd:2011}Initialization')
            if init_elem is not None:
                init_range = init_elem.get('range')
                if init_range:
                    start, end = map(int, init_range.split('-'))
                    self.initialization = (start, end)

class Period:
    def __init__(self, element):
        self.adaptation_sets = []
        for adapt_set in element.findall('{urn:mpeg:dash:schema:mpd:2011}AdaptationSet'):
            self.adaptation_sets.append(AdaptationSet(adapt_set))

class AdaptationSet:
    def __init__(self, element):
        self.content_type = element.get('contentType') or element.get('mimeType', '').split('/')[0]
        self.mime_type = element.get('mimeType')
        self.codecs = element.get('codecs')
        self.lang = element.get('lang')
        self.representations = []
        for rep in element.findall('{urn:mpeg:dash:schema:mpd:2011}Representation'):
            self.representations.append(Representation(rep))

class Representation:
    def __init__(self, element):
        self.id = element.get('id')
        self.bandwidth = element.get('bandwidth')
        self.mime_type = element.get('mimeType')
        self.codecs = element.get('codecs')
        
        # Get BaseURL
        base_url_elem = element.find('{urn:mpeg:dash:schema:mpd:2011}BaseURL')
        self.base_url = base_url_elem.text if base_url_elem is not None else None
        
        # Get SegmentBase
        segment_base_elem = element.find('{urn:mpeg:dash:schema:mpd:2011}SegmentBase')
        self.segment_base = SegmentBase(segment_base_elem)

class MPD:
    def __init__(self, root, base_url):
        self.base_url = base_url
        self.periods = []
        
        # Get MPD level BaseURL
        base_url_elem = root.find('{urn:mpeg:dash:schema:mpd:2011}BaseURL')
        if base_url_elem is not None and base_url_elem.text:
            self.base_url = urllib.parse.urljoin(self.base_url, base_url_elem.text)
            
        for period in root.findall('{urn:mpeg:dash:schema:mpd:2011}Period'):
            self.periods.append(Period(period))

class DashPlayer:
    def __init__(self, mpd_url):
        self.mpd_url = mpd_url
        self.base_url = self._get_base_url(mpd_url)
        self.mpd = self._parse_mpd()

    def _get_base_url(self, url):
        return url.rsplit('/', 1)[0] + '/'

    def _parse_mpd(self):
        import urllib.request
        
        try:
            # Download and parse the MPD file
            if self.mpd_url.startswith('file://'):
                path = urllib.parse.urlparse(self.mpd_url).path
                with open(path, 'rb') as f:
                    mpd_content = f.read()
            else:
                with urllib.request.urlopen(self.mpd_url) as response:
                    mpd_content = response.read()
            
            root = ET.fromstring(mpd_content)
            return MPD(root, self.base_url)
            
        except Exception as e:
            raise Exception(f"Failed to parse MPD file: {str(e)}")

    def get_audio_adaptation_set(self):
        """Helper method to get the audio adaptation set"""
        if not self.mpd or not self.mpd.periods:
            return None
            
        for adaptation_set in self.mpd.periods[0].adaptation_sets:
            if adaptation_set.mime_type and adaptation_set.mime_type.startswith('audio'):
                return adaptation_set
        return None

    def get_media_url(self, representation):
        """Get the complete media URL for a representation"""
        if representation.base_url.startswith('http'):
            return representation.base_url
        else:
            return urllib.parse.urljoin(self.mpd.base_url, representation.base_url)
