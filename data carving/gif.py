import subprocess

header = '25 50 44 46 2d'
trailer1 = '45 4f 46 0d'
trailer2 = '46 0a'
t_list = [trailer1, trailer2]

for t in t_list:
    cmd = subprocess.check_output(f'dd if=11-carve-fat.dd | hexdump -C | grep -E "{header}"', shell=True, cwd='/home/kali/Downloads/11-carve-fat')
    cmd = cmd.decode().split('\n')
    for n in cmd:
            if not n:
                cmd.remove(n)
    for i in range(len(cmd)):
        output = cmd[i]
        skip = int(output[0:8], 16)
        try:
            cmd1 = subprocess.check_output(f'dd if=11-carve-fat.dd skip={skip} bs=1 | hexdump -C | grep -E "{t}" -m 2', shell=True, cwd='/home/kali/Downloads/11-carve-fat', timeout=20)
        except subprocess.TimeoutExpired as e:
            break
        cmd1 = cmd1.decode().split('\n')
        for m in cmd1:
            if not m:
                cmd1.remove(m)

        for j in range(len(cmd1)):
            part_count = int(cmd1[j][0:8],16)
            outp = cmd1[j].split()

            if t==trailer1:
                c1 = 0
                for k in range(len(outp)-1):
                    if outp[k]=='45' and outp[k+1]=='4f' and outp[k+2]=='46' and outp[k+3]=='0d':
                        break
                    elif len(outp[k])==2:
                        c1+=1
                count = part_count + c1 + 4
                cmd2 = subprocess.check_output(f'dd if=11-carve-fat.dd skip={skip} count={count} bs=1 of=pdf{i}_{j}t1.pdf', shell=True, cwd='/home/kali/Downloads/11-carve-fat')
            elif t==trailer2:
                c2 = 0
                for k in range(len(outp)-1):
                    if outp[k]=='46' and outp[k+1]=='0a':
                        break
                    elif len(outp[k])==2:
                        c2+=1
                count = part_count + c2 + 2
                cmd3 = subprocess.check_output(f'dd if=11-carve-fat.dd skip={skip} count={count} bs=1 of=pdf{i}_{j}t2.pdf', shell=True, cwd='/home/kali/Downloads/11-carve-fat')

