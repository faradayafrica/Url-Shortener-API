# from bs4 import BeautifulSoup
# from urllib.request import urlopen

# external_sites_html = urlopen("https://www.w3schools.com/bootstrap5/tryit.asp?filename=trybs_form_toggle_switch&stacked=h").read()

# soup = BeautifulSoup(external_sites_html, "html.parser")
# # Now we can get the tags of the external site from the soup variable.
# title = soup.title.string

# print(title)


import re
import subprocess
from subprocess import TimeoutExpired
from bs4 import BeautifulSoup, Comment
from urllib.parse import urljoin

class Metadata:
    url = ""
    type = "" # https://ogp.me/#types
    title = ""
    description = ""
    image = ""

    def __str__(self):
        return "{url: " + self.url + ", type: " + self.type + ", title: " + self.title + ", description: " + self.description + ", image: " + self.image + "}"

class Metadatareader:

    @staticmethod
    def get_metadata_from_url_in_text(text):
        # look for the first url in the text
        # and extract the url metadata
        urls_in_text = Metadatareader.get_urls_from_text(text)
        if len(urls_in_text) > 0:
            return Metadatareader.get_url_metadata(urls_in_text[0])
        return Metadata()

    @staticmethod
    def get_urls_from_text(text):
        # look for all urls in text
        # and convert it to an array of urls
        regex = r"(?:(?:https?|ftp):\/\/|\b(?:[a-z\d]+\.))(?:(?:[^\s()<>]+|\((?:[^\s()<>]+|(?:\([^\s()<>]+\)))?\))+(?:\((?:[^\s()<>]+|(?:\(?:[^\s()<>]+\)))?\)|[^\s`!()\[\]{};:\'\".,<>?«»“”‘’]))?"
        return re.findall(regex, text)

    @staticmethod
    def get_url_metadata(url):
        # get final url after all redirections
        # then get html of the final url
        # fill the meta data with the info available
        url = Metadatareader.get_final_url(url)
        url_content = Metadatareader.get_url_content(url)
        soup = BeautifulSoup(url_content, "html.parser")
        metadata = Metadata()

        metadata.url = url
        metadata.type = "website"

        for meta in soup.findAll("meta"):
            # priorize using Open Graph Protocol
            # https://ogp.me/
            metadata.type = Metadatareader.get_meta_property(meta, "og:type", metadata.type)
            metadata.title = Metadatareader.get_meta_property(meta, "og:title", metadata.title)
            metadata.description = Metadatareader.get_meta_property(meta, "og:description", metadata.description)
            metadata.image = Metadatareader.get_meta_property(meta, "og:image", metadata.image)
            if metadata.image:
                metadata.image = urljoin(url, metadata.image)

        if not metadata.title and soup.title:
            # use page title
            metadata.title = soup.title.text

        if not metadata.image:
            # use first img element
            images = soup.find_all('img')
            if len(images) > 0:
                metadata.image = urljoin(url, images[0].get('src'))

        if not metadata.description and soup.body:
            # use text from body
            for text in soup.body.find_all(string=True):
                if text.parent.name != 'script' and text.parent.name != 'style' and not isinstance(text, Comment):
                    metadata.description += text

        if metadata.description:
            # remove white spaces and break lines
            metadata.description = re.sub('\n|\r|\t', ' ', metadata.description)
            metadata.description = re.sub(' +', ' ', metadata.description)
            metadata.description = metadata.description.strip()

        return metadata

    @staticmethod
    def get_final_url(url, timeout=5):
        # get final url after all redirections
        # get http response header
        # look for the "Location: " header
        proc = subprocess.Popen([
                    "curl",
                    "-Ls",#follow redirect 301 and silently
                    "-I",#dont download html body
                    url
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            out, err = proc.communicate(timeout=timeout)
        except TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
        header = str(out).split("\\r\\n")
        for line in header:
            if line.startswith("Location: "):
                return line.replace("Location: ", "")
        return url

    @staticmethod
    def get_url_content(url, timeout=5):
        # get url html
        proc = subprocess.Popen([
                    "curl",
                    "-i",
                    "-k",#ignore ssl certificate requisite
                    "-L",#follow redirect 301
                    url
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            out, err = proc.communicate(timeout=timeout)
        except TimeoutExpired:
            proc.kill()
            out, err = proc.communicate()
        return out

    @staticmethod
    def get_meta_property(meta, property_name, default_value=""):
        if 'property' in meta.attrs and meta.attrs['property'] == property_name:
            return meta.attrs['content']
        return default_value
    
    
# content = "https://stdntpartners.sharepoint.com/sites/Community/Shared%20Documents/Forms/AllItems.aspx?ct=1673012603812&or=Teams%2DHL&ga=1&id=%2Fsites%2FCommunity%2FShared%20Documents%2FSocial%20Stories%2FSubmissions%20for%202023%20Welcome%20Video"
# metadata = Metadatareader.get_metadata_from_url_in_text(content)
# print(metadata.url)
# print(metadata.title)
# print(metadata.description)
# print(metadata.image)