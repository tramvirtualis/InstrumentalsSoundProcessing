import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as msb
import sounddevice as sd
import soundfile as sf
import threading
import queue
import tkinter.filedialog as fd

class App(tk.Tk):
    def	__init__(self):
        super().__init__()
        self.title('Speech Recording')

        self.recording = False
        self.file_exists = False
        self.file_name = None
        self.q = queue.Queue()
        self.data = None
        self.index = -1

        self.cvs_figure = tk.Canvas(self, width = 600, height =300)
        lblf_upper = tk.LabelFrame(self)

        btn_open = tk.Button(lblf_upper, text = 'Open', width = 8, command = self.btn_open_click)
        btn_cut = tk.Button(lblf_upper, text = 'Cut', width = 8, command = self.btn_cut_click)
        btn_record = tk.Button(lblf_upper, text = 'Record', width =8, command=lambda m=1:self.threading_rec(m))
        btn_stop = tk.Button(lblf_upper, text = 'Stop', width =8, command=lambda m=2:self.threading_rec(m))
        btn_play = tk.Button(lblf_upper, text = 'Play', width =8, command=lambda m=3:self.threading_rec(m))

        btn_open.grid(row = 0, column= 1, padx = 5, pady = 5)
        btn_cut.grid(row = 1, column= 1, padx = 5, pady = 5)
        btn_record.grid(row = 2, column = 1, padx = 5, pady = 5)
        btn_stop.grid(row = 3, column = 1, padx = 5, pady = 5)
        btn_play.grid(row = 4, column = 1, padx = 5, pady = 5)

        lblf_lower = tk.LabelFrame(self)
        self.factor_zoom = tk.StringVar()
        self.cbo_zoom = ttk.Combobox(lblf_lower, width = 7, textvariable = self.factor_zoom)
        self.cbo_zoom['state'] = 'readonly'
        self.cbo_zoom.bind('<<ComboboxSelected>>', self.factor_zoom_changed)

        btn_next = tk.Button(lblf_lower, text='Next', width=8, command=self.btn_next_click)
        btn_prev = tk.Button(lblf_lower, text='Prev', width=8, command=self.btn_prev_click)

        self.cbo_zoom.grid(row=0, padx=5, pady=5)
        btn_next.grid(row=1, padx=5, pady=5)
        btn_prev.grid(row=2, padx=5, pady=5)
        
        self.cvs_figure.grid(row= 0, column = 0, padx =5, pady =5, rowspan=2)
        lblf_upper.grid(row=0, column=1, padx=5, pady=6, sticky=tk.N)
        lblf_lower.grid(row=1, column=1, padx=5, pady=6, sticky=tk.S)

        self.cvs_figure.bind("<Button-1>", self.xu_ly_mouse)

    def xu_ly_mouse(self):
        x = event.x

    def factor_zoom_changed(self, event):
        factor_zoom = self.factor_zoom.get()
        self.index=-1
        print(factor_zoom)
    #Fit data into queue
    def callback(self, indata, frames, time, status):
        self.q.put(indata.copy())

    #Recording function
    def record_audio(self):
        #Declare global variables    
        #Set to True to record
        self.recording= True   
        global file_exists 
        #Create a file to save the audio
        msb.showinfo(message="Recording Audio. Speak into the mic")
        with sf.SoundFile("trial.wav", mode='w', samplerate=16000,
                            channels=1) as file:
        #Create an input stream to record audio without a preset time
                with sd.InputStream(samplerate=16000, channels=1, callback=self.callback):
                    while self.recording == True:
                        #Set the variable to True to allow playing the audio later
                        self.file_exists =True
                        #write into file
                        file.write(self.q.get())
    def factor_zoom_changed(self, event):
        factor_zoom = self.factor_zoom.get()
        self.index = -1
        print(factor_zoom)
    #Fit data into queue
    def callback(self, indata, frames, time, status):
        self.q.put(indata.copy())                    
    #Functions to play, stop and record audio
    #The recording is done as a thread to prevent it being the main process
    def threading_rec(self, x):
        if x == 1:
            #If recording is selected, then the thread is activated
            t1=threading.Thread(target= self.record_audio)
            t1.start()
        elif x == 2:
            #To stop, set the flag to false
            global recording
            recording = False
            msb.showinfo(message="Recording finished")
            self.data, samplerate = sf.read('trial.wav', dtype='int16')
            L = len(self.data)
            N = L // 600
            lst_values =[]
            for i in range(1, N+1):
                s = '%10d' % i
                lst_values.append(s)
            self.cbo_zoom['value'] = lst_values
            
            self.cvs_figure.delete(tk.ALL)
            for i in range(0, 600 - 1):
                x1 = self.data[i*N]
                y1 = int((int(x1) + 32768)*300//65535) - 150

                x2 = self.data[(i+1)*N]
                y2 = int((int(x2) + 32768)*300//65535) - 150

                self.cvs_figure.create_line(i, 150 - y1, i+1, 150 - y2, fill = 'orange')


        elif x == 3:
            #To play a recording, it must exist.
            if self.file_exists:
                #Read the recording if it exists and play it
                data, fs = sf.read("trial.wav", dtype='float32') 
                sd.play(data,fs)
                sd.wait()
            else:
                #Display and error if none is found
                msb.showerror(message="Record something to play")

    def btn_zoom_click(self):
        self.cvs_figure.delete(tk.ALL)
        yc = 150
        i = self.index
        for x in range(0, 600-1):
            a = self.data[i*600 + x]
            b = self.data[i*600 + x + 1]
            y1 = (int(a) + 32767) * 300 // 65535 - 150
            y2 = (int(b) + 32767) * 300 // 65535 - 150

            self.cvs_figure.create_line(x, yc-y1, x+1, yc-y2, fill = 'green')

    def btn_next_click(self):
        factor_zoom = self.factor_zoom.get()
        factor_zoom = int(factor_zoom.strip())
        data_temp = self.data[::factor_zoom]
        L = len(data_temp)
        self.cvs_figure.delete(tk.ALL)
        self.index = self.index+1
        print('index = ', self.index)
        for x in range(0,600 - 1):
            a1 = self.data[self.index*600 + x]
            y1 = (int(a1) + 32768)*300//65535 - 150
            a2 = self.data[self.index*600 + x+1]
            y2 = (int(a2) + 32768)*300//65535 - 150
            self.cvs_figure.create_line(x, 150 - y1, x + 1, 150 - y2)
    def btn_prev_click(self):
        factor_zoom = self.factor_zoom.get()
        factor_zoom = int(factor_zoom.strip())
        data_temp = self.data[::factor_zoom]
        L = len(data_temp)
        self.cvs_figure.delete(tk.ALL)
        self.index = self.index-1
        for x in range(0,600 - 1):
            a1 = self.data[self.index*600 + x]
            y1 = (int(a1) + 32768)*300//65535 - 150
            a2 = self.data[self.index*600 + x+1]
            y2 = (int(a2) + 32768)*300//65535 - 150
            self.cvs_figure.create_line(x, 150 - y1, x + 1, 150 - y2)

    def btn_open_click(self):
        filetypes = (("Wave files", "*.wav"),)
        self.filename = fd.askopenfilename(title="Open wave file", filetypes=filetypes)
        if self.filename:
            print(self.filename)
        self.data, fs = sf.read(self.filename, dtype='int16')
        L = len(self.data)
        N = L // 600
        lst_values =[]
        for i in range(1, N+1):
            s = '%10d' % i
            lst_values.append(s)
        self.cbo_zoom['value'] = lst_values
        
        self.cvs_figure.delete(tk.ALL)
        for i in range(0, 600 - 1):
            x1 = self.data[i*N]
            y1 = int((int(x1) + 32768)*300//65535) - 150

            x2 = self.data[(i+1)*N]
            y2 = int((int(x2) + 32768)*300//65535) - 150

            self.cvs_figure.create_line(i, 150 - y1, i+1, 150 - y2, fill = 'orange')

    def btn_cut_click(self):
        data_mix_1 = self.data[20*600:32*600]
        f = open('mix_01.bin', 'wt')
        f.write(data_mix_1)
        f.close()

        index = 30
        batDau = index*600
        ketThuc = (index + 1)*600
        data_temp = self.data[batDau:ketThuc]
        self.cvs_figure.delete(tk.ALL)
        for x in range(0, 600 - 1):
            x1 = data_temp[x]
            x2 = data_temp[(x + 1)]

            y1 = int((int(x1) + 32768)*300//65535) - 150
            y2 = int((int(x2) + 32768)*300//65535) - 150

            self.cvs_figure.create_line(x, 150 - y1, x+1, 150 - y2, fill = 'orange')


if	__name__	==	"__main__":
    app	=	App()
    app.mainloop()