import subprocess
import time
from multiprocessing import Pool
from urllib.parse import urlparse
import requests
import re
import os 

link = 'https://www119.vipanicdn.net/streamhls/395c00c8e81e269aa76202288b5c4727/ep.1.1709288211.m3u8'

class M3u8:
    def __init__(self, m3u8_dir:str = 'm3u8/', working_dir:str='hls/') -> None:
        self.working_dir = working_dir
        self.m3u8_dir = m3u8_dir

    def download(self, link:str, name:str, path:str=''):
        # host = urlparse(link).netloc
        try:
            res = requests.get(link)
            master_m3u8_arr = self.master_m3u8_scraper(res.text)
            main_link = link.split('/list')[0] + '/' 
            for index, obj in enumerate(master_m3u8_arr):
                ultimate_link = str(main_link + obj['link_part']) 
                resolution = obj['resolution']
                master_m3u8_arr[index]['link_part'] = ultimate_link
                master_m3u8_arr[index]['name'] = f'{path}{resolution}_{name}.ts'

            with Pool(len(master_m3u8_arr)) as p:
                p.map(self.vidplay_download, master_m3u8_arr)
        except Exception as err:
            self.none_vidplay_download(link=link, name=name, path=self.working_dir)

    def none_vidplay_download(self, link:str, name:str='namelessMonster', path:str=''):
        name_path = path + name
        command = ['ffmpeg', '-y', '-loglevel', 'quiet', '-i', link, '-c', 'copy', f'{name_path}.ts']
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.scaling(name_path)

    def vidplay_download(self, obj:dict):
        link = obj['link_part']
        name = obj['name']
        print(name)
        command = ['ffmpeg', '-y', '-loglevel', 'quiet', '-i', link, '-c', 'copy', name]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.ts_to_mp4(name)
        self.ts_to_m3u8(name)

    def ts_to_m3u8(self, name:str):
        output_name = name.split('.')[0] + '.m3u8'
        splited = output_name.split('/')
        splited.insert(-1, self.m3u8_dir)
        output_name = '/'.join(splited)
        ffmpeg_command = ['ffmpeg', '-y', '-loglevel', 'quiet', '-i', name, '-c:v', 'copy', '-c:a', 'copy', '-hls_time', '10', '-hls_list_size', '0', output_name]
        subprocess.run(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def ts_to_mp4(self, name:str):
        output_name = name.split('.')[0] + '.mp4'
        command = ['ffmpeg', '-y', '-loglevel', 'quiet', '-i', name, '-c', 'copy', output_name]
        # subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    def master_m3u8_scraper(self, m3u8_text:str):
        splited = m3u8_text.splitlines()
        pattern = r'BANDWIDTH=(\d+),RESOLUTION=(\d+x\d+)'
        arr = []
        for index, line in enumerate(splited):
            if line.startswith('#EXT-X-STREAM-INF:'):
                match = re.search(pattern=pattern, string=line)
                if match:
                    bandwidth = match.group(1)
                    resolution = match.group(2)
                    link = splited[index+1]
                    obj = {'resolution': resolution ,'bandwith': bandwidth , 'link_part' : link}
                    arr.append(obj)
                else:
                    print('sorry no match found ')
                    arr.append(None)
        return arr
                
    def convert_quality(self, file_name:str):
        name = file_name.split('/')[-1]
        splited = name.split('_')
        resolution = splited[0]
        input_file_name = self.working_dir + splited[1]
        command = ['ffmpeg', '-y', '-loglevel', 'quiet', '-i', input_file_name, '-vf', f'scale={resolution}', '-c:a', 'copy', file_name]
        subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.ts_to_mp4(name=file_name)
        self.ts_to_m3u8(name=file_name)

    def scaling(self, input_file:str):
        resolutions = ['640x360', '1280x720', '1920x1080']
        file_name = input_file.split('/')[-1]
        arr = [f'{self.working_dir}{reso}_{file_name}.ts' for reso in resolutions]
 
        with Pool(3) as p:
            p.map(self.convert_quality, arr)
        return arr

    def convert_m3u8(self, args):
        url, output_file = args
        ffmpeg_command = ['ffmpeg', '-i', url, '-c:v', 'copy', '-c:a', 'copy', '-hls_time', '10', '-hls_list_size', '0', output_file]
        subprocess.run(ffmpeg_command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    def files_to_m3u8(self, path_list:list, save_folder:str=''):
        start_time = time.time()
        arr = [(path, f'{save_folder}/{path.split("/")[-1].rsplit(".", 1)[0]}.m3u8') for path in path_list]
        with Pool(len(path_list)) as p:
            p.map(self.convert_m3u8, arr)

        print('Total time:', time.time() - start_time)

    def link_m3u8_files(self, input_files):
        out_file = f'{self.working_dir}/{self.m3u8_dir}/master_' + input_files[0].split('_')[-1]
        with open(out_file, 'w') as outfile:
            outfile.write("#EXTM3U\n")
            outfile.write("#EXT-X-VERSION:3\n\n")
            for file_path in input_files:
                file_path = file_path
                bandwidth, resolution = self.bandwith_resolution(file_path)
                outfile.write(f"# {resolution} variant\n")
                outfile.write(f"#EXT-X-STREAM-INF:BANDWIDTH={bandwidth},RESOLUTION={resolution}\n")
                outfile.write(f"{file_path.split('/')[-1]}\n\n")

    def bandwith_resolution(self, file_path:str):
        resolution = file_path.split('/')[-1].split('.')[0].split('_')[0]
        bandwith = self.extract_bandwidth(resolution=resolution)
        return bandwith, resolution

    def extract_bandwidth(self, resolution):
        if resolution == '640x360':
            return '720000'
        elif resolution == '1280x720':
            return '1800000'
        elif resolution == '1920x1080':
            return '4500000'
        else:
            return '1000000'

    def main_m3u8(self, link:str, name):
        self.download(link, name, path=self.working_dir)
        m3u8_list = os.listdir(f'{self.working_dir}/{self.m3u8_dir}')
        m3u8_list = [file for file in m3u8_list if file.endswith('.m3u8') and file.startswith('master_') == False]
        self.link_m3u8_files(m3u8_list)

# Example usage
# if __name__ == "__main__":
#     m = M3u8()
#     m.main_m3u8(link, 'sakib')
