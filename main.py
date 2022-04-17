# -*- coding: utf-8 -*-

# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.
import os
import intelligence


def print_hi(name):
    # Use a breakpoint in the code line below to debug your script.
    print(f'Hi, {name}')  # Press ⌘F8 to toggle the breakpoint.


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    print_hi('PyCharm')
    mp4 = "./1.mp4"
    # TODO：astral-karma-242001-0137aa59ffcd.json 是GCP生成的访问密钥，需要自行生成
    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = './astral-karma-242001-0137aa59ffcd.json'
    # TODO: 因为需要访问Google服务器，需要采用代理方式。可以设置你自己的代理端口，或者在EC2上运行
    os.environ['https_proxy'] = 'http://127.0.0.1:8889'
    srt_content = intelligence.asr_mp4(mp4)
    with open("1.srt", "w") as srt_file:
        srt_file.write(srt_content)
    # TODO: 调用vlc观看对比
    os.system("/Applications/VLC.app/Contents/MacOS/VLC " + mp4)

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
