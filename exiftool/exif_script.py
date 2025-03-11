# Questo script organizza le foto in cartelle in base alla posizione geografica (nazione, città),
# estendendo le funzionalità del comando exiftool
import requests as r
import subprocess

cmd0 = subprocess.check_output(f'ls -l', shell=True, cwd='/home/kali/Desktop/geoimgr_photos')
cmd0_1 = cmd0.decode().split()
lista_immagini = [e for e in cmd0_1 if e.endswith('jpg')==True]

for nome_img in lista_immagini:
    command = subprocess.check_output(f'exiftool {nome_img} -GPS\\Latitude -GPS\\Longitude', shell=True, cwd='/home/kali/Desktop/geoimgr_photos')
    cmd = command.decode().split()
    lat_deg = int(cmd[3])
    lat_min = int(cmd[5].strip('\''))
    lat_sec = float(cmd[6].strip('\"'))
    lat_dir = cmd[7]
    lon_deg = int(cmd[11])
    lon_min = int(cmd[13].strip('\''))
    lon_sec = float(cmd[14].strip('\"'))
    lon_dir = cmd[15]

    def convert_dms_to_dd_lat(d, m, s):
        dd_coord = (d + (m / 60) + (s / 3600)) * (-1 if lat_dir in ['W', 'S'] else 1)
        return dd_coord

    def convert_dms_to_dd_lon(d, m, s):
        dd_coord = (d + (m / 60) + (s / 3600)) * (-1 if lon_dir in ['W', 'S'] else 1)
        return dd_coord

    dd_lat = convert_dms_to_dd_lat(lat_deg, lat_min, lat_sec)
    dd_lon = convert_dms_to_dd_lon(lon_deg, lon_min, lon_sec)
    print(dd_lat, dd_lon)

    payload = {'lat':dd_lat, 'lon':dd_lon, 'format':'json', 'apiKey':'1272397f00ca4183b3968cbb071e38d4'}
    req = r.get('https://api.geoapify.com/v1/geocode/reverse', params=payload)
    req = req.json()
    req=req['results']
    city = req[0]['city'].replace(" ","")
    country = (req[0]['country']).replace(" ","")
    print(req)

    cmd1 = subprocess.check_output(f'mkdir -p {country}/{city}', shell=True, cwd='/home/kali/Desktop/geoimgr_photos')
    cmd2 = subprocess.check_output(f'mv ./{nome_img} ./{country}/{city}', shell=True, cwd='/home/kali/Desktop/geoimgr_photos')



