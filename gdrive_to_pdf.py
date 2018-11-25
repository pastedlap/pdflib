from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from apiclient.http import MediaIoBaseDownload
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from io import StringIO
import io,os,codecs

#=========================================================
#CONCERT THE PDF STREAM TO UTF8 TEXT
def pdf_to_text2(fstream):
        rsrcmgr = PDFResourceManager()
        sio = StringIO()
        codec = 'utf-8'
        laparams = LAParams()
        device = TextConverter(rsrcmgr, sio, codec=codec, laparams=laparams)
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        for page in PDFPage.get_pages(fstream):
                try:interpreter.process_page(page)
                except:
                    print('COULD NOT PROCESS PAGE')    
                    pass
 
        text = sio.getvalue()
        device.close()
        sio.close()
        return text

"""
=========================================================
CONVERT ALL THE PDF FILES IN THE GIVEN FOLDER INTO UTF8 TXT FILESS
"""
def processFolder(folder_id,service):
    if not os.path.exists(folder_id):os.mkdir(folder_id)
     # Call the Drive v3 API
    results = service.files().list(q="'"+folder_id+"' in parents",
        pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        print('No files found.')
    else:
        print('Files:')
        for item in items:
            fname=item['name']
            if not fname.endswith('.pdf'):continue
            print('processing {0} '.format(fname))#, item['id']))
            file_id =item['id']
            request = service.files().get_media(fileId=file_id) #mimeType='application/pdf')
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                print ("Download %d%%." % int(status.progress() * 100))
           
            text=pdf_to_text2(fh)
            fw=codecs.open(folder_id+'/'+fname+'.txt','w',encoding='utf8')
            fw.write(text)
            fw.close()

#===========================================

def main(folder_id):
    #create a connection to google drive.
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', 'https://www.googleapis.com/auth/drive.readonly')
        creds = tools.run_flow(flow, store)
    service = build('drive', 'v3', http=creds.authorize(Http()))
    
    processFolder(folder_id, service)

#===========================================

if __name__ == '__main__':
    folder_id='1RyntetHv4TORxfkW7Ayf4osw6vjcIrdL'
    main(folder_id)