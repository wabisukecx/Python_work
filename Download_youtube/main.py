# -------------------------------------------------------------------------------
# Name:        Download Youtube
# Author:      wabisuke
# Created:     14/08/2021
# Copyright:   (c) wabisuke 2021
# -------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
import tkinter as tk
import youtube_dl


def main():
    # Start extract Youtube base on operation mode & url
    def btn_click():
        ope_mode = selval.get()
        youtube_url = txt_box.get()
        ydl_opts = {}

        if ope_mode == 0:
            ydl_opts = {'format': 'bestaudio/best',
                        'postprocessors': [{
                            'key': 'FFmpegExtractAudio',
                            'preferredcodec': 'mp3',
                            'preferredquality': '192'
                        }],
                        }

        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([youtube_url])

    if __name__ == '__main__':

        # Main window setting
        root = tk.Tk()
        root.geometry("560x140")
        root.title("youtube-dl")

        # Radio button for operation mode
        rdo_txt = ["音声のみ抜き出す", "映像を抜き出す"]
        selval = tk.IntVar()

        for i in range(len(rdo_txt)):
            rdo = tk.Radiobutton(root, value=i,
                                 variable=selval,
                                 text=rdo_txt[i])
            rdo.place(x=40 + (i * 130), y=20)

        # Text box label
        txt_lbl = tk.Label(text="Youtubeのアドレス : ")
        txt_lbl.place(x=45, y=58)

        # Text box for Youtube link url
        txt_box = tk.Entry(width=60)
        txt_box.place(x=160, y=60)

        # Button for extract youtube
        btn = tk.Button(root, text="ダウンロード", command=btn_click)
        btn.place(x=460, y=100)
        root.mainloop()


if __name__ == '__main__':
    main()
