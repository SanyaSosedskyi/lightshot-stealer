import tkinter as tk
from PIL import Image, ImageTk
import os
import os.path
import httplib2
import urllib.request as urllib2
import re


# CREATING MAIN-WINDOW
class Main(tk.Frame):
    def __init__(self, _root):
        super().__init__(root)
        self.root = _root
        self.images = []
        self.image_buttons = {}
        self.init_main()
        self.upload_files()

    def init_main(self):
        # CREATING TOOLBAR AND ITS LABELS, ENTRIES AND BUTTON(download)
        self.toolbar = tk.Frame(root, bg='#fafafa', bd=2, height=40)
        self.toolbar.pack(side=tk.TOP, fill=tk.X)
        self.refresh_image_temp = Image.open('button_refresh.jpg')
        self.refresh_image_temp = self.refresh_image_temp.resize((40, 40), Image.ANTIALIAS)
        self.refresh_image = ImageTk.PhotoImage(self.refresh_image_temp)
        self.button_refresh = tk.Button(self.toolbar, bg='#333', image=self.refresh_image,
                                        command=self.show_images)
        self.button_refresh.pack(side=tk.LEFT)
        self.label_last_url = tk.Label(self.toolbar, text='Последние символы URL: ', bg='#fafafa')
        self.label_last_url.pack(side=tk.LEFT)
        self.entry_last_url = tk.Entry(self.toolbar)
        self.entry_last_url.pack(side=tk.LEFT)
        self.label_amount_images = tk.Label(self.toolbar, text='Количество изображений: ', bg='#fafafa')
        self.label_amount_images.pack(side=tk.LEFT, padx=5)
        self.entry_amount_images = tk.Entry(self.toolbar)
        self.entry_amount_images.pack(side=tk.LEFT)
        self.button_download = tk.Button(self.toolbar, text='Скачать', bg='#fafafa', font='Arial 12',
                                         command=self.upload_files)
        self.button_download.pack(side=tk.LEFT, padx=5)
        self.button_delete = tk.Button(self.toolbar, text='Удалить все', bg='#fafafa', font='Arial 12',
                                       command=self.delete_files)
        self.button_delete.pack(side=tk.LEFT, padx=5)

        # CREATING SCROLLBAR, CANVAS, FRAME and PUT IMAGES INTO THE FRAME
        self.image_canvas = tk.Canvas(root)
        self.scroll_y = tk.Scrollbar(root, orient='vertical', command=self.image_canvas.yview)
        self.images_frame = tk.Frame(self.image_canvas)
        self.show_images()

        self.image_canvas.create_window(0, 0, anchor='nw', window=self.images_frame)
        self.image_canvas.update_idletasks()
        self.image_canvas.configure(scrollregion=self.image_canvas.bbox('all'), yscrollcommand=self.scroll_y.set)
        self.image_canvas.pack(fill='both', expand=True, side='left')
        self.scroll_y.pack(fill='y', side='right')

# PRINT PHOTOS TO WINDOW FROM DIRECTORY 'images'
    def show_images(self):
        self.clear_images_frame()
        counter = 0
        y = 1
        img_counter = 0
        self.images_list = [name for name in os.listdir('./images') if os.path.isfile('./images/'+name)]
        self.images = []
        print(self.images_list)
        for _img in self.images_list:
            self.img = Image.open('images/'+_img)
            img_width = self.img.width
            img_height = self.img.height
            self.img = self.img.resize((158, 158), Image.ANTIALIAS)
            self.images.append(ImageTk.PhotoImage(self.img))
            if y == 7:
                y = 1
                counter += 1
            self.button_image = tk.Button(self.images_frame, image=self.images[img_counter])
            self.button_image.bind('<1>', self.open_image)
            self.image_buttons[self.button_image['image']] = (img_width, img_height, _img)
            self.button_image.grid(row=counter, column=y)
            y += 1
            img_counter += 1

    def clear_images_frame(self):
        list = self.images_frame.grid_slaves()
        for l in list:
            l.destroy()

    def upload_files(self):
        pass

    def delete_files(self):
        self.files = [file for file in os.listdir('./images')]
        for f in self.files:
            os.remove('./images/'+f)
        self.show_images()
    def open_image(self, event):
        Child(event.widget['image'], self.image_buttons)

# CREATING CHILD-WINDOW
class Child(tk.Toplevel):
    def __init__(self, _image_, image_buttons):
        tk.Toplevel.__init__(self)
        self._image_ = _image_
        self.image_buttons = image_buttons
        self.init_child()
    def init_child(self):
        self.title('Image')
        self.w = self.image_buttons[self._image_][0]
        self.h = self.image_buttons[self._image_][1]
        while self.w > 1000 or self.h >600:
            self.w = int(self.w*0.95)
            self.h = int(self.h*0.95)
        self.sw = int((root.winfo_screenwidth()-self.w)/2)
        self.sh = int((root.winfo_screenheight()-self.h)/2)
        self.geometry('{0}x{1}+{2}+{3}'.format(self.w+20, self.h+20, self.sw, self.sh))
        self.img = Image.open('images/'+self.image_buttons[self._image_][2])
        self.img = self.img.resize((self.w, self.h), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(self.img)
        self.label_big_image = tk.Label(self, width=self.w, height=self.h, image=self.image)
        self.label_big_image.pack()


# CREATING ROOT-WINDOW
root = tk.Tk()
app = Main(root)
app.pack()
root.title('Lightshot stealer')
sw = int((root.winfo_screenwidth()-1000)/2)
sh = int((root.winfo_screenheight()-600)/2)
root.geometry('{0}x{1}+{2}+{3}'.format(1000, 600, sw, sh))
root.resizable(False, False)
root.mainloop()
