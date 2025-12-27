import tkinter as tk
import soundfile as sf
import tkinter.filedialog as fd
import numpy as np
import matplotlib.pyplot as plt


class App(tk.Tk):
    def	__init__(self):
        super().__init__()
        self.data = None

        self.title('Spectrogram')
        # Tạo widget
        self.cvs_figure = tk.Canvas(self, width = 600, height = 600, relief = tk.SUNKEN, border = 1)

        lblf_upper = tk.LabelFrame(self)
        btn_open = tk.Button(lblf_upper, text = 'Open', width = 10, command= self.btn_open_click)
        btn_cut = tk.Button(lblf_upper, text = 'Cut', width = 10, command= self.btn_cut_click)
        btn_spectrogram = tk.Button(lblf_upper, text = 'Spectrogram', width = 10, command= self.btn_spectrogram_click)

        btn_open.grid(row = 0, padx = 5, pady = 5)
        btn_cut.grid(row = 1, padx = 5, pady = 5)

        btn_spectrogram.grid(row = 2, padx = 5, pady = 5)
        
        # Đưa widget lên lưới
        self.cvs_figure.grid(row = 0, column = 0, rowspan = 2, padx = 5, pady = 5)
        lblf_upper.grid(row = 0, column = 1, padx = 5, pady = 6, sticky = tk.N)

    def btn_open_click(self):
        filetypes = (("Wave file", "*.wav"),)
        filename = fd.askopenfilename(title="Open wave files", filetypes=filetypes)
        if filename:
            print(filename)
        self.data, fs = sf.read(filename, dtype = 'int16')
        L = len(self.data)
        N = L // 600
        lst_values =[]
        for i in range(1, N+1):
            s = '%10d' % i
            lst_values.append(s)
        yc = 450
        # Xoá canvas
        self.cvs_figure.delete(tk.ALL)
        for x in range(0, 600-1):
            a = self.data[x*N]
            b = self.data[(x+1)*N]
            y1 = (int(a) + 32767) * 300 // 65535 - 150
            y2 = (int(b) + 32767) * 300 // 65535 - 150
            self.cvs_figure.create_line(x, yc-y1, x+1, yc-y2, fill = 'green')

    def btn_cut_click(self):
        index_bat_dau = 27
        bat_dau = index_bat_dau*600
        index_ket_thuc = 37
        ket_thuc = index_ket_thuc*600
        data_temp = self.data[bat_dau:ket_thuc]
        L = len(data_temp)
        N = L // 600

        print('L =', L)
        print('N =', N)
        yc = 450
        # Xoá canvas
        self.cvs_figure.delete(tk.ALL)
        for x in range(0, 600-1):
            a = self.data[x*N]
            b = self.data[(x+1)*N]
            y1 = (int(a) + 32767) * 300 // 65535 - 150
            y2 = (int(b) + 32767) * 300 // 65535 - 150
            self.cvs_figure.create_line(x, yc-y1, x+1, yc-y2, fill = 'green')

    def btn_spectrogram_click(self):
        index_bat_dau = 27
        bat_dau = index_bat_dau*600
        index_ket_thuc = 37
        ket_thuc = index_ket_thuc*600
        data_temp = self.data[bat_dau:ket_thuc]
        data_temp = data_temp.astype('float32')
        data_temp = data_temp/32768
        L = len(data_temp)
        N = L // 600
        pad_zeros = np.zeros((112,), dtype='float32')
        for x in range(0, 600):
            a = x*N
            b = x*N + 400
            frame = data_temp[a:b]
            y = np.hstack((frame, pad_zeros))
            Y = np.fft.fft(y, 512)
            scale = 200.0
            S = scale*np.sqrt(Y.real**2 + Y.imag**2)
            S = np.clip(S, 0.001, 400)
            dark = -(S - 512)/512*255
            dark = dark[:257]
            dark = dark.astype(np.int32)
            yc = 300
            for k in range(0,257):
                mau = '#%02X%02X%02X' % (dark[k],dark[k],dark[k])
                self.cvs_figure.create_line(x, yc - k, x, yc - (k+1), fill = mau)
            pass

    


if __name__ == "__main__":
    app	=	App()
    app.mainloop()
