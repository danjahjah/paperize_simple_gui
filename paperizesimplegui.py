import tkinter as tk
from tkinter import filedialog
from tkinter import ttk

import configparser, os, math, time
import sys
import paperize.main as paperize


QrCorrectionLevelList = ["L", "M", "Q", "H",]

def convert_size(size_bytes) -> str:
  """Convert file size to human readable"""
  if size_bytes == 0:
     return "0B"
  size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
  i = int(math.floor(math.log(size_bytes, 1024)))
  p = math.pow(1024, i)
  s = round(size_bytes / p, 2)
  return "%s %s" % (s, size_name[i])


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title('File2QR converter')
        self.geometry('600x400')
        self.QrCorrectionLevel = "M"

        for c in range(3): self.columnconfigure(index=c, weight=1) 
        self.rowconfigure(index=0, weight=1)
        self.rowconfigure(index=1, weight=0)

        self.text = tk.Text(height=12)
        self.text.grid(row=0, column=0, columnspan=3, sticky="nsew" )
        self.text.tag_config('warning', background="yellow", foreground="red")

        self.btn_paper = ttk.Button(text="File2QR", command=self.proceed_file)
        self.btn_paper.grid(row=1, column=0, ipadx=6, ipady=6, padx=5, pady=5)

        self.btn_file = ttk.Button(text="QR2File", command= self.proceed_text)
        self.btn_file.grid(row=1, column=1, ipadx=6,  ipady=6, padx=5, pady=5)




    def append_text(self, text):
      self.text.insert(tk.END, text)

    def append_text_error(self, text):
      self.text.insert(tk.END, text, 'warning')


    def proceed_text(self):
       
      filename=[]
      res, size = self.open_file()

      if res is None:
          self.append_text_error( f"Error opening file\n")
          return

      print(res, size)
      filename.append(res)

      self.append_text( f"Conversion start\n")
      self.update()

      

      try:
          paperize.mode_file(filename)
      except Exception as e:
        self.append_text_error( f"Error occured while converting:\n{e}\n") 
        self.append_text( f"Conversion not complete\n") 
        return
      self.append_text( f"Conversion complete\n")


    def proceed_file(self):
        filename=[]
        res, size = self.open_file()

        if res is None:
          self.append_text_error( f"Error opening file\n")
          return

        size_print = convert_size(size)

        filename.append(res)

        self.append_text(f"{filename[0]} {size_print}\n")
        self.append_text( f"Conversion start\n")
        self.update()
        start = time.time()
        try:
          paperize.mode_paper(filename, self.QrCorrectionLevel)
        except Exception as e:
          self.append_text_error( f"Error occured while converting:\n{e}\n") 
          self.append_text( f"Conversion not complete\n") 
          return

        end = time.time()
        elapsed = end-start
        self.append_text( f"Conversion complete in {round(elapsed,2)} sec.\n")


    def get_settings(self):
        global QrCorrectionLevelList
        config = configparser.ConfigParser()

        if not os.path.exists('config.ini'):
          config.add_section('Settings')
          config.set('Settings', 'QrCorrectionLevel', 'M')

          with open('config.ini', 'w') as config_file:
            config.write(config_file)

          self.append_text( f"Created config.ini\n")


        config.read('config.ini')
        self.QrCorrectionLevel = config.get('Settings', 'QrCorrectionLevel')
        if self.QrCorrectionLevel not in QrCorrectionLevelList:
          self.append_text_error( "QrCorrectionLevelList Error, set to M")
          self.QrCorrectionLevel = "M"
        
    def open_file(self) -> str:
      filepath = filedialog.askopenfilename()
      if filepath != "":   
        return filepath, os.stat(filepath).st_size
      else:
        return None, None




if __name__ == "__main__":
    app = App()
    app.get_settings()
    app.mainloop()