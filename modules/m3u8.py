import subprocess
import time
from multiprocessing import Pool
from urllib.parse import urlparse
import requests
import re
import os 
# from .main import FileSystem

link = 'https://www119.vipanicdn.net/streamhls/395c00c8e81e269aa76202288b5c4727/ep.1.1709288211.m3u8'


class M3u8:
    def __init__(self,m3u8_dir:str = 'm3u8/',working_dir:str='hls/') -> None:
        # FileSystem(hls_folder=f'{working_dir}/{m3u8_dir}')
        self.working_dir = working_dir
        self.m3u8_dir= m3u8_dir

    def download(self,link:str,name:str,path:str=''):
        host = urlparse(link).netloc
        # if host == 'gamn.v44381c4b81.site':
        try:
            res = requests.get(link)
            master_m3u8_arr =self.master_m3u8_scraper(res.text)
            main_link = link.split('/list')[0]+'/' 
            # print(main_link)
            for index,obj in enumerate(master_m3u8_arr) :
                ultimate_link =  str(main_link + obj['link_part']) 
                resolution = obj['resolution']
                master_m3u8_arr[index]['link_part'] = ultimate_link
                master_m3u8_arr[index]['name']=f'{path}{resolution}_{name}.ts'

            with Pool(len(master_m3u8_arr)) as p : 
                p.map(self.vidplay_download,master_m3u8_arr)
        except Exception as err :    
            self.none_vidplay_download(link=link,name=name,path=self.working_dir)
    def none_vidplay_download(self,link:str,name:str='namelessMonster',path:str=''):
        name_path= path+name
        command = ['ffmpeg', '-y' , '-i', link, '-c', 'copy', f'{name_path}.ts']
        subprocess.run(command)
        self.scaling(name_path) 
        
        



    def vidplay_download(self,obj:dict):
        # print(obj)
        link = obj['link_part']
        name = obj['name']
        print(name)
        command = ['ffmpeg','-y', '-i', link, '-c', 'copy', name]
        subprocess.run(command) 
        #converting ts to mp4 
        self.ts_to_mp4(name)
        self.ts_to_m3u8(name)


    def ts_to_m3u8(self,name:str):
        # print(name)
        output_name:str = name.split('.')[0]+'.m3u8'
        splited = output_name.split('/')
        splited.insert(-1,self.m3u8_dir)
        output_name = '/'.join(splited)
        # print(output_name)
        # print(output_name)
        ffmpeg_command = ['ffmpeg','-y','-i', name, '-c:v', 'copy', '-c:a', 'copy', '-hls_time', '5', '-hls_list_size', '0' , output_name]
        subprocess.run(ffmpeg_command)


    def ts_to_mp4(self,name:str):
        output_name = name.split('.')[0]+'.mp4'
        command = ['ffmpeg','-y','-i', name, '-c', 'copy', output_name]
        subprocess.run(command)
    
    def master_m3u8_scraper(self,m3u8_text:str) : 
        splited = m3u8_text.splitlines()
        pattern = r'BANDWIDTH=(\d+),RESOLUTION=(\d+x\d+)'
        arr = []
        for index,line in enumerate(splited) : 
            if line.startswith('#EXT-X-STREAM-INF:'): 
                match = re.search(pattern=pattern,string=line)
                if match : 
                    bandwidth = match.group(1)
                    resolution = match.group(2)
                    link = splited[index+1]
                    obj = {'resolution':resolution ,'bandwith':bandwidth , 'link_part' : link}
                    # print(obj)
                    arr.append(obj)
                    # print(bandwidth,resolution)
                else :
                    print('sorry no match found ')
                    arr.append(None)
        return arr
                    
                
    
    def convert_quality(self,file_name:str):
        # print(file_name)
        name = file_name.split('/')[-1]
        splited = name.split('_')
        resolution = splited[0]
        input_file_name = self.working_dir+splited[1]
        command = ['ffmpeg', '-y', '-i', input_file_name, '-vf', f'scale={resolution}', '-c:a', 'copy', file_name]
        subprocess.run(command)
        self.ts_to_mp4(name=file_name)
        self.ts_to_m3u8(name=file_name)

    def scaling(self,input_file:str):
        resolutions = ['640x360', '1280x720', '1920x1080']
        file_name= input_file.split('/')[-1]
        arr = [f'{self.working_dir}{reso}_{file_name}.ts' for reso in resolutions]
 
        with Pool(3) as p : 
            p.map(self.convert_quality,arr)
        return arr
        
        
    def convert_m3u8(self,args):
        url, output_file = args
        ffmpeg_command = ['ffmpeg', '-i', url, '-c:v', 'copy', '-c:a', 'copy', '-hls_time', '10', '-hls_list_size', '0', output_file]
        subprocess.run(ffmpeg_command)

    def files_to_m3u8(self,path_list: list, save_folder: str = ''):
        start_time = time.time()
        arr = [(path, f'{save_folder}/{path.split("/")[-1].rsplit(".", 1)[0]}.m3u8') for path in path_list]
        with Pool(len(path_list)) as p:
            p.map(self.convert_m3u8, arr)

        print('Total time:', time.time() - start_time)

    def link_m3u8_files(self,input_files):
        print(input_files)
        out_file = f'{self.working_dir}/{self.m3u8_dir}/master_' + input_files[0].split('_')[-1]
        # print(output_name)
        with open(out_file, 'w') as outfile:
            outfile.write("#EXTM3U\n")
            outfile.write("#EXT-X-VERSION:3\n\n")
            # Iterate over input files and write variant playlists to the output file
            for file_path in input_files:
                # bandwidth,resolution = self.extract_resolution(file_path)
                file_path:str = file_path
                bandwidth,resolution = self.bandwith_resolution(file_path)
                print('ehh')
                outfile.write(f"# {resolution} variant\n")
                outfile.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={resolution}\n")
                outfile.write(f"{file_path.split('/')[-1]}\n\n")

    def bandwith_resolution(self,file_path:str):
        # Extract resolution from file path (e.g., '720p')
        resolution = file_path.split('/')[-1].split('.')[0].split('_')[0]
        bandwith = self.extract_bandwidth(resolution=resolution)
        return bandwith,resolution
        # print(bandwith)

        # return file_path.split('/')[-1].split('.')[0].split('_')[1]

    def extract_bandwidth(self,resolution):
        # Example: assuming bandwidth is derived from the resolution (you can adjust this logic as needed)
        # resolution = self.extract_resolution(file_path)
        if resolution == '640x360':
            return '720000'
        elif resolution == '1280x720':
            return '1800000'
        elif resolution == '1920x1080':
            return '4500000'
        else:
            return '1000000'  # Default bandwidth
        
    def main_m3u8(self,link:str,name):
        self.download(link,name,path=self.working_dir,)
        m3u8_list = os.listdir(f'{self.working_dir}/{self.m3u8_dir}')
        m3u8_list = [file for file in m3u8_list if file.endswith('.m3u8') and file.startswith('master_')==False ]
        self.link_m3u8_files(m3u8_list)

        pass
# if __name__ == '__main__':
#     m = M3u8()
#     url = 'https://gamn.v44381c4b81.site/_v2-pvzv/12a3c523f9105800ed8c394685aeeb0bc22eaf5c15bbbded021e7baea93ece832257df1a4b6125fcfa38c35da05dee86aad28d46d73fc4e9d4e5a23a5271f0d631c612e30918b40914c3f4ee3f107d122631832f445560c69b8dbc08c7e06cd23e0fe14d5636ea56bcea6611b65b0296ea2a/h/list;15a38634f803584ba8926411d7bee906856cab0654b5bfb3.m3u8'
#     m.main_m3u8(link,'sakib')

