### Narnia - Simple Python Web Server 
### Author: Joseph Kennedy
### 
import sys, socket, time, struct, os, re, logging
from datetime import datetime
from collections import namedtuple

### Constants
DEBUG = True
DEBUG_REQUEST = True
narnia_version = '0.00001'

### Classes

### Config Class
###

class NarniaConfig:
    config_path = 'config/narnia.cfg'
    mime_path = 'config/mime.types'
    access_log = 'logs/access.log'
    error_log = 'logs/error.log'
    root = 'html'
    default_pages = "index.htm,index.html,index.php,index.asp"
    

### Request Class
###

class RequestData:
    def __init__(self):
        self.request_type = ''
        self.response_type = ''
        self.error = False
        self.error_type = ''
        self.path = ''
        self.data = ''
    
class MimeTypes:
    typeLookup = {}
    types = []


class HTTPObject:
    def __init__(self):
        self.path = ''
        self.content_type = ''
        self.error = False
        self.error_type = ''
        self.data = ''
    

### Global
###
naConfig = NarniaConfig()
naMime = MimeTypes()
### Functions

### Main
###

def main(argv):
    try:
        ### Map Content to file types
        load_mime_types()
        ### Logging
        logging.basicConfig(filename=naConfig.error_log,level=logging.DEBUG)
        ### Network
        host = '0.0.0.0'
        port = int(argv)
        my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        my_socket.bind((host, port))
        my_socket.listen(5)
        
        all_data = []
        
        ### Banner to console
        welcome_banner()
        while 666:
            conn, addr = my_socket.accept()
            r_request = RequestData()
            f_object = HTTPObject()
            all_data = receive_data(conn)
            conn.setblocking(1)
            if DEBUG_REQUEST:
                logging.debug('main::RequestString: ' + ''.join(all_data))
            r_request.data = ''.join(all_data)
            r_request.path = ''
            ### Parse Client Request
            r_request = parse_request(r_request)
            if r_request.error == False:
                if r_request.path != '':
                    f_object.path = r_request.path
                    f_object = file_read(f_object)
                    if f_object.error==False:
                        response_object(conn,f_object)
                    else:
                        response_notfound(conn)
                else:
                    if DEBUG:
                       logging.debug('main::Bad path!')
            else:
                if DEBUG:
                    logging.debug('main::Bad Parse: ' + str(r_request.error) + ':'
                     + r_request.error_type)
                                     
            #response_forbidden(conn)
            try:
                access_log.close
                error_log.close
                conn.shutdown(1)
                conn.close
            except NameError:
                pass
    except Exception as e:
        print 'Narnia - Exit!'
        if DEBUG:
            logging.debug('main::Exception->' + str(type(e)) + ':' + str(e))
        try:
            access_log.close
            error_log.close
            conn.shutdown(1)
            conn.close
        except:
            pass
        sys.exit(0)
    

### Receive Data
###     Input: Connection

def receive_data(conn):
    arr_data = []
    mydata = ''
    timeout = 1
    begin=time.time()
    conn.setblocking(0)
    ### Binary Tides
    ### http://www.binarytides.com/receive-full-data-with-the-recv-socket-function-in-python/
    while 1:
        if arr_data and time.time() - begin > timeout:
            return arr_data
        elif time.time() - begin > timeout * 2:
            return arr_data

        try:
            mydata = conn.recv(1024)
            if mydata:
                arr_data.append(mydata)
                begin = time.time()
            else:
                time.sleep(0.1)
        except:
            pass    
    


### Parse Requests and pass to other functions
###     Input: raw string data from request

def parse_request(request):
    temp_data = ''.join(request.data)
    check_str = ''
    request.error = False
    pat = re.compile("(GET).* HTTP|(PUT).* HTTP|(POST).* HTTP|(HEAD).* HTTP")
    matches = pat.search(temp_data)
    if DEBUG:
        logging.debug('parse_request::start')
    if matches:
        check_str = str(matches.group(1)).strip("..")
        if DEBUG:
            logging.debug('parse_request::Match!')
        if check_str == 'GET':
            request.type = 'GET'
            return parse_get_request(request)
        elif check_str == 'PUT':
            request.type = 'PUT'
            return parse_put_request(request)
        elif check_str == 'POST':
            request.type = 'GET'
            return parse_post_request(request)
        elif check_str == 'HEAD':
            request.type = 'HEAD'
            return parse_head_request(request)
        else:
            if DEBUG:
                logging.debug('parse_request::request-> ' + check_str)
            request.error = True
            request.error_type = 'parse-invalid-method'
            return request
    else:
        if DEBUG:
            logging.debug('parse_request::No Match!')
        request.error = True
        request.error_type = 'parse-nomatch'
        return request
    


### Parse GET Requests
###     Input: raw data from request

def parse_get_request(request):
    temp_data = ''.join(request.data)
    request.error = False
    pat = re.compile(" \/([A-Za-z0-9\_\-\.\/]+) HTTP")
    matches = pat.search(temp_data)
    if matches:
        if DEBUG:
            logging.debug('parse_get_request::Match->' + str(matches.group(1)))
        request.path = str(matches.group(1))
        return request
    else:
        if DEBUG:
            logging.debug('parse_get_request::No Match!')
        request.error = True
        request.error_type = 'parse-get-nomatch'
        return request

### Parse PUT Requests
###     Input: raw data from request

def parse_put_request(request):
    return request

### Parse POST Requests
###     Input: raw data from request

def parse_post_request(request):
    return request

### Parse HEAD Requests
###     Input: raw data from request

def parse_head_request(request):
    temp_data = ''.join(request.data)
    request.error = False
    pat = re.compile(" \/([A-Za-z0-9\_\-\.\/]+) HTTP")
    matches = pat.search(temp_data)
    if matches:
        if DEBUG:
            logging.debug('parse_head_request::Match->' + str(matches.group(1)))
        request.path = str(matches.group(1))
        return request
    else:
        if DEBUG:
            logging.debug('parse_head_request::No Match!')
        request.error = True
        request.error_type = 'parse-get-nomatch'
        return request


### Read File Contents
###     Input: Path to the file
###     Output: HTTPObject()

def file_read(file):
    ### Next should be to check file attributes
    ### and extension to determine Content-Type :P
    m_file = file
    markup = ''
    test_path = naConfig.root + '/' + file.path
    pat = re.compile("[\w]+\.([\w]+)")
    matches = pat.search(m_file.path)
    if matches:
        r_match = str(matches.group(1))
        if r_match in naMime.typeLookup:
            m_file.content_type = naMime.types[naMime.typeLookup[r_match]]
            if DEBUG:
                logging.debug("file_read::Content-Type: " + str(m_file.content_type))
        else:
            m_file.content_type = 'Unknown-Type'
            m_file.error = True
            m_file.error_type +="no-type;"
        if(os.path.isfile(test_path)):
            f = open(test_path,'r')
            m_file.data = f.read()
            f.close()
            return m_file
        else:
            if DEBUG:
                logging.debug('file_read::Not File')
            m_file.error = True
            m_file.error_type +="no-file-found;"
            return m_file
    
### Response with Object
###

def response_object(conn, httpObject):
    mydate = datetime.now()
    if DEBUG:
        logging.debug('response_object::Start')
    arr_response = []
    arr_response.append(
                        "HTTP/1.1 200 OK\n"
                        "Date: " + str(mydate) + "\n"
                        "Server: Narnia (FreeBSD)\n"
                        "Access-Ranges: bytes\n"
                        "Content-Length: "+ str(len(httpObject.data)) + "\n"
                        "Connection: close\n"
                        "Content-Type: " + httpObject.content_type + "; charset=UTF-8\n\n" + httpObject.data
                        )
    conn.sendall(''.join(arr_response))
    if DEBUG:
        logging.debug('response_object:End')


### Response with Forbidden Error
###

def response_forbidden(conn):
    mydate = datetime.now()
    if DEBUG:
        logging.debug('response_forbidden: Start')
    arr_response = []
    text = 'Forbidden'
    arr_response.append(
                        "HTTP/1.1 403 Forbidden\n"
                        "Date: " + str(mydate) + "\n"
                        "Server: Narnia (FreeBSD)\n"
                        "Access-Ranges: bytes\n"
                        "Content-Length: " + str(len(text)) + "\n"
                        "Connection: close\n"
                        "Content-Type: text/html; charset=UTF-8\n\n" + text
                        )
    conn.sendall(''.join(arr_response))
    

### Response with Not Found
###

def response_notfound(conn):
    mydate = datetime.now()
    if DEBUG:
        logging.debug('ResponseNotFound: Start')
    arr_response = []
    text = 'Not Found'
    arr_response.append(
                        "HTTP/1.1 404 Not Found\n"
                        "Date: " + str(mydate) + "\n"
                        "Server: Narnia (FreeBSD)\n"
                        "Access-Ranges: bytes\n"
                        "Content-Length: "+ str(len(text)) + "\n"
                        "Connection: close\n"
                        "Content-Type: text/html; charset=UTF-8\n\n" + text
                        )
    conn.sendall(''.join(arr_response))


### Load Mime Types from File
###

def load_mime_types():
    try:
        pat = re.compile(
            "^([\w\+\-\:\/\.]+)(?:([ \t]+([\w]+)))"
            "(?:[ \t]+(([\w]+))[ \t]+([\w]+)|)"
            "(?:[ \t]+(([\w]+))[ \t]+([\w]+)|)"
            "(?:[ \t]+(([\w]+))[ \t]+([\w]+)|)"
            "(?:[ \t]+(([\w]+))[ \t]+([\w]+)|)"
        )
        with open(naConfig.mime_path,'r') as file:
            i = 0
            for r_line in file:
                matches = pat.search(r_line)
                if matches:
                    count = len(matches.groups())
                    for r in range(2,count):
                        r_str = str(matches.group(r)).strip()
                        if r_str != '' and r_str not in naMime.typeLookup:
                            naMime.typeLookup[r_str] = i
                    naMime.types.append(str(matches.group(1)))
                    i+=1
                
        file.close
    except Exception as e:
        if DEBUG:
            logging.debug('load_mime_types::Exception->' + str(type(e)) + ':' + str(e))
        try:
            file.close()
        except:
            pass
    
### Welcome Banner
###
def load_config():
    pass
    
    
    

### Welcome Banner
###
def welcome_banner():
    temp_version = ''
    for chr in range(0,len(narnia_version)):
        temp_version = temp_version + '*' + narnia_version[chr:(chr+1)] + '* '
    
    print("*******************************************************************************\n"
    "                                                                               \n"
    "     ***** *     **                                                            \n"
    "  ******  **    **** *                                        *                \n"
    " **   *  * **    ****                                        ***               \n"
    "*    *  *  **    * *                                          *                \n"
    "    *  *    **   *                ***  ****                                    \n"
    "   ** **    **   *        ****     **** **** * ***  ****    ***        ****    \n"
    "   ** **     **  *       * ***  *   **   ****   **** **** *  ***      * ***  * \n"
    "   ** **     **  *      *   ****    **           **   ****    **     *   ****  \n"
    "   ** **      ** *     **    **     **           **    **     **    **    **   \n"
    "   ** **      ** *     **    **     **           **    **     **    **    **   \n"
    "   *  **       ***     **    **     **           **    **     **    **    **   \n"
    "      *        ***     **    **     **           **    **     **    **    **   \n"
    "  ****          **     **    **     ***          **    **     **    **    **   \n"
    " *  *****               ***** **     ***         ***   ***    *** *  ***** **  \n"
    "*     **                 ***   **                 ***   ***    ***    ***   ** \n"
    "*                                                                              \n"
    " **                                                                            \n"
    "           *** *** *** *** *** *** ***   *** *** *** *** *** *** ***           \n"
    "           *v* *e* *r* *s* *i* *o* *n*   " + temp_version + "           \n"
    "           *** *** *** *** *** *** ***   *** *** *** *** *** *** ***           \n"
    "*******************************************************************************\n"
    )

    
if __name__ == "__main__":
    main(sys.argv[1])
