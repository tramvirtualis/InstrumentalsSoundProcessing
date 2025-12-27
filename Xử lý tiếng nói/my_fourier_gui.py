import tkinter as tk
import soundfile as sf
import tkinter.filedialog as fd
import numpy as np
import matplotlib.pyplot as plt


class App(tk.Tk):
    def	__init__(self):
        super().__init__()
        self.data = None

        self.title('Speech Signal Processing')
        # Tạo widget
        self.cvs_figure = tk.Canvas(self, width = 600, height = 300, relief = tk.SUNKEN, border = 1)

        lblf_upper = tk.LabelFrame(self)
        btn_open = tk.Button(lblf_upper, text = 'Open', width = 8, command= self.btn_open_click)
        btn_cut = tk.Button(lblf_upper, text = 'Cut', width = 8, command= self.btn_cut_click)
        btn_spectrum = tk.Button(lblf_upper, text = 'Spectrum', width = 8, command= self.btn_spectrum_click)

        btn_open.grid(row = 0, padx = 5, pady = 5)
        btn_cut.grid(row = 1, padx = 5, pady = 5)

        btn_spectrum.grid(row = 2, padx = 5, pady = 5)
        
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
        yc = 150
        # Xoá canvas
        self.cvs_figure.delete(tk.ALL)
        for x in range(0, 600-1):
            a = self.data[x*N]
            b = self.data[(x+1)*N]
            y1 = (int(a) + 32767) * 300 // 65535 - 150
            y2 = (int(b) + 32767) * 300 // 65535 - 150
            self.cvs_figure.create_line(x, yc-y1, x+1, yc-y2, fill = 'green')

    def btn_cut_click(self):
        index = 30
        batDau = index*600
        ketThuc = (index +1)*600
        data_temp = self.data[batDau:ketThuc]
        yc = 150
        # Xoá canvas
        self.cvs_figure.delete(tk.ALL)
        for x in range(0, 600-1):
            a = data_temp[x]
            b = data_temp[(x+1)]
            y1 = (int(a) + 32767) * 300 // 65535 - 150
            y2 = (int(b) + 32767) * 300 // 65535 - 150
            self.cvs_figure.create_line(x, yc-y1, x+1, yc-y2, fill = 'green')

    def btn_spectrum_click(self):
        index = 30
        batDau = index*600
        ketThuc = (index +1)*600
        x = self.data[batDau:ketThuc]
        N = 16000
        x = x/32768
        x = x.astype(np.float32)
        L = len(x)
        y = np.zeros((L,), dtype= np.float32)
        a = 0.98
        for i in range(1,L):
            if i == 0:
                y[i] = x[i] - a*x[i]
            else:
                y[i] = x[i] - a*x[i-1]

        Y = np.fft.fft(y, N)
        S = np.sqrt(Y.real**2 + Y.imag**2)
        S = 20*np.log10(S)
        # S = (S+1)**1.5
        print(S)
        S = S[:N//2+1]
        plt.plot(S)
        plt.show()
        print(S)

def btn_spectrum_pre_empha_click(self):
        index = 30
        batDau = index*600
        ketThuc = (index +1)*600
        x = self.data[batDau:ketThuc]
        N = 16000
        x = x/32768
        x = x.astype(np.float32)
        X = np.fft.fft(x, N)
        S = np.sqrt(X.real**2 + X.imag**2)
        S = 20*np.log10(S+1)
        # S = (S+1)**1.5
        print(S)
        S = S[:N//2+1]
        plt.plot(S)
        plt.show()
        print(S)


if __name__ == "__main__":
    app	=	App()
    app.mainloop()
