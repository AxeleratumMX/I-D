from os import listdir
from os.path import isfile, join
import xml.sax
import re
from html.parser import HTMLParser

# Classes used for generate data to feed models
class DataReader:
    def open_stream(self):
        raise Exception('DataReader.open_stream not implemented yet')

    def read_data(self):
        raise Exception('DataReader.read_data not implemented yet')

    def has_more_data(self):
        raise Exception('DataReader.has_more_data not implemented yet')

    def close_stream(self):
        raise Exception('DataReader.close_stream not implemented yet')

# Data reader for one file. Read line by line.
class TextDataReader(DataReader):

    def __init__(self, filename, encoding='utf-8', **kwargs):
        self.filename = filename  
        self.encoding = encoding
        self.file = None   
        self.more_data = True 
        self.batch_line = None 
        super(TextDataReader, self).__init__(**kwargs)

    def open_stream(self):
        self.file = open(self.filename, 'r', encoding=self.encoding)

    def read_data(self):
        if self.batch_line == None:
            next_line = self.file.readline()
            if next_line == None:
                next_line = ''
        else:
            next_line = self.batch_line

        self.batch_line = self.file.readline()
        if not self.batch_line:
            self.more_data = False

        return next_line

    def has_more_data(self):
        return self.more_data

    def close_stream(self):
        self.file.close()

# Data reader for multiple files
class FilesDataReader(DataReader):

    def __init__(self, folder, encoding='utf-8', **kwargs):
        self.encoding = encoding
        self.files = [join(folder, f) for f in listdir(folder) if isfile(join(folder, f))]
        self.files_count = len(self.files)
        self.file_index = 0
        self.current_file = None
        super(FilesDataReader, self).__init__(**kwargs)

    def open_stream(self):
        self.current_file = TextDataReader(
                                self.files[self.file_index], 
                                encoding=self.encoding
                            )
        self.current_file.open_stream()

    def read_data(self):
        if self.current_file.has_more_data():
            result = self.current_file.read_data()
        else:
            self.file_index += 1
            self.current_file.close_stream()
            self.current_file = TextDataReader(
                                self.files[self.file_index], 
                                encoding=self.encoding
                            )
            self.current_file.open_stream()
            result = self.current_file.read_data()
        return result


    def has_more_data(self):
        if self.file_index >= self.files_count - 1:
            return self.current_file.has_more_data()

        return True

    def close_stream(self):
        self.current_file.close_stream()

# Data reader for wikipedia dump

class WikiDataReader(DataReader):

    class WikiParser(HTMLParser):

        def __init__(self, elements, clean_regex):
            self.elements = elements
            self.clean_regex = clean_regex
            self.reading = False
            self.data = ''
            self.status_stack = []

            HTMLParser.__init__(self)

        def handle_starttag(self, name, attrs):
            self.status_stack.append(self.reading)
            
            if name in self.elements:
                self.reading = True
            else:                
                self.reading = False

        def handle_endtag(self, name):
            self.reading = self.status_stack.pop()

        def handle_data(self, content):
            if self.reading:
                self.data += content.strip()
        
        def get_data(self):
            result = re.sub(self.clean_regex, '', self.data)
            self.data = ''
            return result

        
 
    
    def __init__(self, dump, elements=['text'], clean_regex=r'[^\w\s\.,;]', **kwargs):
        self.reader = TextDataReader(dump)
        self.parser = self.WikiParser(elements, clean_regex)
        self.htmlParser = HTMLParser()
        super(WikiDataReader, self).__init__(**kwargs)

    def open_stream(self):
        self.reader.open_stream()

    def read_data(self):
        data = self.reader.read_data()
        text = self.htmlParser.unescape(data)
        self.parser.feed(text)
        return self.parser.get_data()

    def has_more_data(self):
        return self.reader.has_more_data()

    def close_stream(self):
        self.parser.close()
        self.reader.close_stream()






