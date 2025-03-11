import subprocess

def funzione_jpeg():
    header = "ff d8 ff e0 00 10 4a 46" #JFIF
    header_exif = 'ff d8 ff e1'
    trailer = "ff d9"
    h_list = [header, header_exif]
    for h in h_list:
        result = subprocess.check_output(f'dd if=11-carve-fat.dd | hexdump -C | grep -E "{h}"', shell=True, cwd='/home/kali/Downloads/11-carve-fat')
        output = result.decode().split('\n')
        for t in output:
            if t=='':
                output.remove(t)

        for i in range(len(output)):
            skip = int(output[i][0:8],16)
            cmd = subprocess.check_output(f'dd if=11-carve-fat.dd skip={skip} bs=1 | hexdump -C | grep -E "{trailer}" -m 4', shell=True, cwd='/home/kali/Downloads/11-carve-fat')
            # mi prendo le prime 4 occorrenze perchè il trailer trovato alla prima potrebbe non essere quello corretto, come nel caso dell'immagine shark.jpg
            # quindi faccio una count_list e provo l'estrazione con diversi valori di count
            output1 = cmd.decode().split('\n')
            count_list = list()
            for j in range(len(output1)):
                elemento = output1[j]
                if elemento:
                    count = int(elemento[0:8],16)
                else:
                    break
                elemento1 = elemento.split()
                c = 0
                for k in range(len(elemento1)-1):
                    if elemento1[k] == 'ff' and elemento1[k+1] == 'd9': # cerco il valore trailer
                        break
                    elif len(elemento1[k])==2:
                        c+=1
                count = count + c + 2
                count_list.append(count)

            j = 0
            flag = False
            for value in count_list:
                if not flag:
                    print(f'Value{j}: ', value)
                    if h==header_exif:
                        i = 'exif' # modifico il nome dell'immagine per non sovrascrivere quelle già estratte
                    cmd = subprocess.check_output(f'dd if=11-carve-fat.dd skip={skip} count={value} bs=1 of=immagine{i}_{j}.jpg', shell=True, cwd='/home/kali/Downloads/11-carve-fat')
                    try:
                        cmd1 = subprocess.check_output(f'dd if=immagine{i}_{j}.jpg | hexdump -C | head -n 5 | grep -E "45 78 69 66"', shell=True, cwd='/home/kali/Downloads/11-carve-fat')  # cerco la stringa 'Exif'
                    except subprocess.CalledProcessError as e:
                        print('File JFIF')
                        cmd2 = subprocess.check_output(f'printf \'\x43\' | dd of=immagine{i}_{j}.jpg bs=1 seek=23 conv=notrunc',shell=True, cwd='/home/kali/Downloads/11-carve-fat')

                    try :
                        cmd3 = subprocess.check_output(f'identify immagine{i}_{j}.jpg',shell=True, cwd='/home/kali/Downloads/11-carve-fat')
                        if len(cmd3)!=0:
                            flag=True
                    except subprocess.CalledProcessError as e:
                        print(f'L\'immagine{i}_{j} è corrotta e verrà rimossa')
                        cmd4 = subprocess.check_output(f'rm immagine{i}_{j}.jpg',shell=True, cwd='/home/kali/Downloads/11-carve-fat')
                    j += 1

        # se il comando cmd1 trova la stringa 'Exif' nei bytes 24-27 allora non devo sovrascrivere il 23esimo byte col valore 43
        # se invece il file è Jfif allora devo controllare che il 23esimo byte (Bogus Marker Length) nell'header sia uguale a 43 ed eventualmente sovrascriverlo
        # utilizzo il valore 'flag' per evitare di produrre duplicati, mi fermo quando estraggo un'immagine correttamente

def funzione_gif():
    header1 = '47 49 46 38 39 61'
    header2 = '47 49 46 38 37 61'
    trailer = '00 3b'
    h_list = [header1, header2]
    for h in h_list:
        try:
            cmd1 = subprocess.check_output(f'dd if=11-carve-fat.dd | hexdump -C | grep -E "{h}"', shell=True, cwd='/home/kali/Downloads/11-carve-fat')
            cmd1 = cmd1.decode().split('\n')
            skip = int(cmd1[0][0:8], 16)
            cmd2 = subprocess.check_output(
                f'dd if=11-carve-fat.dd skip={skip} bs=1 | hexdump -C | grep -E "{trailer}" -m 1', shell=True,
                cwd='/home/kali/Downloads/11-carve-fat')
            cmd2 = cmd2.decode().split('\n')
            partial_count = int(cmd2[0][0:8], 16)
            output = cmd2[0].split()
            c = 0
            for i in range(len(output) - 1):
                if output[i] == '00' and output[i + 1] == '3b':
                    break
                elif len(output[i]) == 2:
                    c += 1
            count = partial_count + c + 2
            cmd3 = subprocess.check_output(f'dd if=11-carve-fat.dd skip={skip} count={count} bs=1 of=gif.gif', shell=True, cwd='/home/kali/Downloads/11-carve-fat')
        except subprocess.CalledProcessError as e:
            print(f'header: "{h}" non trovato')

def funzione_pdf():
    header = '25 50 44 46 2d'
    trailer1 = '45 4f 46 0d'
    trailer2 = '46 0a'
    t_list = [trailer1, trailer2]

    for t in t_list:
        cmd = subprocess.check_output(f'dd if=11-carve-fat.dd | hexdump -C | grep -E "{header}"', shell=True,
                                      cwd='/home/kali/Downloads/11-carve-fat')
        cmd = cmd.decode().split('\n')
        for n in cmd:
            if not n:
                cmd.remove(n)
        for i in range(len(cmd)):
            output = cmd[i]
            skip = int(output[0:8], 16)
            try:
                cmd1 = subprocess.check_output(
                    f'dd if=11-carve-fat.dd skip={skip} bs=1 | hexdump -C | grep -E "{t}" -m 2', shell=True,
                    cwd='/home/kali/Downloads/11-carve-fat', timeout=20)
            except subprocess.TimeoutExpired as e:
                break
            cmd1 = cmd1.decode().split('\n')
            for m in cmd1:
                if not m:
                    cmd1.remove(m)

            for j in range(len(cmd1)):
                part_count = int(cmd1[j][0:8], 16)
                outp = cmd1[j].split()

                if t == trailer1:
                    c1 = 0
                    for k in range(len(outp) - 1):
                        if outp[k] == '45' and outp[k + 1] == '4f' and outp[k + 2] == '46' and outp[k + 3] == '0d':
                            break
                        elif len(outp[k]) == 2:
                            c1 += 1
                    count = part_count + c1 + 4
                    cmd2 = subprocess.check_output(
                        f'dd if=11-carve-fat.dd skip={skip} count={count} bs=1 of=pdf{i}_{j}t1.pdf', shell=True,
                        cwd='/home/kali/Downloads/11-carve-fat')
                elif t == trailer2:
                    c2 = 0
                    for k in range(len(outp) - 1):
                        if outp[k] == '46' and outp[k + 1] == '0a':
                            break
                        elif len(outp[k]) == 2:
                            c2 += 1
                    count = part_count + c2 + 2
                    cmd3 = subprocess.check_output(
                        f'dd if=11-carve-fat.dd skip={skip} count={count} bs=1 of=pdf{i}_{j}t2.pdf', shell=True,
                        cwd='/home/kali/Downloads/11-carve-fat')


if __name__=='__main__':
    choice = input('Inserisci il formato di file da cercare [J]PG, [G]IF, [P]DF: ')
    match choice:
        case 'J':
            print('Sto cercando immagini jpeg...')
            funzione_jpeg()
        case 'G':
            print('Sto cercando gif...')
            funzione_gif()
        case 'P':
            print('Sto cercando file pdf...')
            funzione_pdf()