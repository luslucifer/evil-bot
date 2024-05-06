import sqlite3
from modules.upload import send
from modules.download import download_file_link
from modules.m3u8 import M3u8
from modules.db import insert_data_into_db,create_table
import subprocess
import os 
import requests
import json
import m3u8

# print(send('ehh.txt','test/x.txt'))
test_m3u8 = 'https://www119.vipanicdn.net/streamhls/395c00c8e81e269aa76202288b5c4727/ep.1.1709288211.360.m3u8'
link = 'https://www119.vipanicdn.net/streamhls/395c00c8e81e269aa76202288b5c4727/ep.1.1709288211.m3u8'

class FileSystem :
    def __init__(self,working_dir:str='hls',m3u8_dir:str='m3u8') -> None:
         self.working_dir:str = working_dir
         self.m3u8_dir:str = m3u8_dir
         self.create_folder_if_not_exists(working_dir)
         self.create_folder_if_not_exists(f'{working_dir}/{m3u8_dir}')
         self.vidsrc:str = 'https://vidsrc-bc567b0e907e.herokuapp.com'
         create_table()

    def create_folder_if_not_exists(self,folder_path):
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
            print(f"Folder '{folder_path}' created.")
        else:
            print(f"Folder '{folder_path}' already exists.")


    def download_video_files(self,url:str, name:str):
        # Run ffmpeg command to download HLS playlist and segments
        m = M3u8()
        m.main_m3u8(link=url,name=name)

    def m3u8_parser(self,m3u8_file:str) :
        playlist = m3u8.load(m3u8_file)
        seg = playlist.segments
        segments_arr = [segment.uri for segment in seg]
        return segments_arr 


    

    def get_m3u8(self,imdb_id:str|int,ss:str|None = None ,ep:str|None=None ):
        if ss and ep : 
            return requests.get(f'{self.vidsrc}/tv/{imdb_id}/{ss}/{ep}').json()
        elif ss==None and ep == None : 
            return requests.get(f'{self.vidsrc}/movie/{imdb_id}').json()
        
    
    def ts_upload(self,list_dir:str , folder_path:str):
        arr = []
        scraped_data = {}
        exicuted = False
        for file in list_dir : 
            if not file.endswith('.m3u8') and file.endswith('.ts') : 
                print(f'processing:{file}')
                sent = send(file,f'{folder_path}/{file}')
                obj = sent['result']['document']
                file_id = obj['file_id']
                download_link = download_file_link(file_id=file_id)
                obj['link'] = download_link
                arr.append(obj)
                if exicuted ==False :
                    for key, value in sent['result'].items():
                            # Skip the 'document' key
                        if key != 'document':
                            # Add the key and value to the scraped_data dictionary
                            scraped_data[key] = value
                    exicuted =True
        return arr,scraped_data

    def m3u8_files_uploader(self,folder_path:str,imdb_id:str|None=None ,ss:str|None=None,ep:str|None=None):
        list_dir = os.listdir(path=folder_path)
        # arr,scraped_data = self.ts_upload(list_dir,folder_path)
        with open('ehh.json','r') as file : 
            arr = json.load(file)

        with open('st.json','r') as file : 
            scraped_data = json.load(file)

        scraped_data['imdb_id'] = imdb_id
        scraped_data['ss'] = ss
        scraped_data['ep'] = ep


        for f in list_dir:
            if f.startswith('master_'):
                        list_dir.remove(f)
                        list_dir.append(f)
        # print(list_dir)
        
        for f in list_dir :
            print(len(arr))
            if f.endswith('.m3u8') or  f.startswith('master_'):
                print(f'm3u8 processing {f}')
                with open(f'{folder_path}/{f}','r+') as file :
                    splited = file.read().splitlines() 
                    for index,line in enumerate(splited):
                        line = line.replace(' ' ,'')
                        # print(line)
                        for obj in arr : 
                            if line.endswith('.ts') or line.endswith('.m3u8') == True : 
                                if obj['file_name'] == line :
                                    print(f'editing : {line}')
                                    print(obj['link'])
                                    splited[index] = obj['link']
                                    print ('match found loop broked ')
                                    break
                    file.seek(0)    
                    file.truncate()
                    joined = '\n'.join(splited)
                    file.write(joined)

                
                sent = send(filename=f,path=f'{folder_path}/{f}')
                obj = sent['result']['document']
                download_link = download_file_link(obj['file_id'])
                obj['link'] = download_link
                arr.append(obj)
                print(len(arr))
                scraped_data['m3u8_link'] = download_link
                scraped_data['files_list'] = arr
            # print(scraped_data)
        with open ('st.json','w') as file : 
            json.dump(scraped_data,file,indent=2)           
        with open ('ehh.json','w') as file : 
            json.dump(arr,file,indent=2)
        return scraped_data
       
    def main(self, imdb_id:str ,ss:str|int|None = None , ep:str|int|None = None): 
        try:
            
            m3u8 = self.get_m3u8(imdb_id=imdb_id,ss=ss,ep=ep)['m3u8'][0]
            print(m3u8)
            self.download_video_files(m3u8,'mr_k')
            self.m3u8_files_uploader(folder_path=f'{self.working_dir}/{self.m3u8_dir}',imdb_id=imdb_id,ss=ss,ep=ep)
            os.rmdir(self.working_dir)
        except Exception as err : 
            print (err)



if __name__ == '__main__': 
    # f.main(123)
    with open('Total.txt','r') as file : 
        arr = file.read().splitlines()
    for i in arr:
        f = FileSystem()
        f.main(imdb_id=i)



