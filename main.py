import tkinter as tk
import platform
from PIL import Image, ImageTk
import os
import os.path
import httplib2
import urllib.request as urllib2
import re
import base36
import pytesseract
import threading
from tkinter import ttk
import webbrowser

str_words_to_find = ''
str_words_to_ignore = ''


# CREATING MAIN-WINDOW
class Main(tk.Frame):
    def __init__(self, _root):
        super().__init__(root)
        self.os_info = platform.platform()
        print(self.os_info)
        self.root = _root
        self.images = []
        self.image_buttons = {}
        if not os.path.exists('images'):
            os.makedirs('images')
        self.init_main()
        self.thread_create_canvas = threading.Thread(target=self.create_canvas, daemon=True)

    def init_main(self):

        # CREATING TOOLBAR AND ITS LABELS, ENTRIES AND BUTTON(download)
        if self.os_info.startswith('Linux'):
            self.toolbar_2 = tk.Frame(root, bg='#fafafa', bd=2)
            self.toolbar_2.pack(side=tk.TOP, fill=tk.X)
            self.button_instruction = tk.Button(self.toolbar_2,
                                                text=' Click here to open https://prnt.sc/ and upload any '
                                                     'picture, then copy'' last symbols (example = ohu1pw) ', bg='#444',
                                                font='Arial 10', fg='#fafafa')
            self.button_instruction.pack(side=tk.LEFT, padx=193)
            self.button_instruction.bind('<1>', lambda e: webbrowser.open_new('https://prnt.sc/'))
            self.toolbar = tk.Frame(root, bg='#fafafa', bd=2)
            self.toolbar.pack(side=tk.TOP, fill=tk.X)
            self.button_refresh = tk.Button(self.toolbar, bg='#fafafa', text='Reload',
                                            command=self.redrawing_canvas)
            self.button_refresh.pack(side=tk.LEFT)
            self.label_last_url = tk.Label(self.toolbar, text='Last symbols of URL: *', bg='#fafafa')
            self.label_last_url.pack(side=tk.LEFT, padx=5)
            self.entry_last_url = tk.Entry(self.toolbar, width=14)
            self.entry_last_url.pack(side=tk.LEFT, padx=5)
            self.label_amount_images = tk.Label(self.toolbar, text='Amount of pictures: *', bg='#fafafa')
            self.label_amount_images.pack(side=tk.LEFT, padx=5)
            self.entry_amount_images = tk.Entry(self.toolbar, width=14)
            self.entry_amount_images.pack(side=tk.LEFT, padx=5)
            self.button_more_setting = tk.Button(self.toolbar, font='Arial 12', bg='#fafafa', text='More settings',
                                                 command=self.open_settings)
            self.button_more_setting.pack(side=tk.LEFT, padx=5)
            self.button_download = tk.Button(self.toolbar, text='Download', bg='#fafafa', font='Arial 12')
            self.button_download.bind('<1>', lambda event: threading.Thread(target=self.upload_files, daemon=True,
                                                                            args=(self.entry_last_url.get(),
                                                                                  self.entry_amount_images.get())).start())

            self.button_download.pack(side=tk.LEFT, padx=5)
            self.button_delete = tk.Button(self.toolbar, text='Delete all', bg='#fafafa', font='Arial 12',
                                           command=self.delete_files)
            self.button_delete.pack(side=tk.LEFT, padx=5)

            self.create_canvas()

        else:
            self.toolbar_2 = tk.Frame(root, bg='#fafafa', bd=2)
            self.toolbar_2.pack(side=tk.TOP, fill=tk.X)
            self.button_instruction = tk.Button(self.toolbar_2,
                                                text=' Click here to open https://prnt.sc/ and upload any '
                                                     'picture, then copy'' last symbols (example = ohu1pw) ', bg='#444',
                                                font='Arial 11', fg='#fafafa')
            self.button_instruction.pack(side=tk.LEFT, padx=143)
            self.button_instruction.bind('<1>', lambda e: webbrowser.open_new('https://prnt.sc/'))
            self.toolbar = tk.Frame(root, bg='#fafafa', bd=2)
            self.toolbar.pack(side=tk.TOP, fill=tk.X)
            self.button_refresh = tk.Button(self.toolbar, bg='#fafafa', text='Reload', font='Arial 13',
                                            command=self.redrawing_canvas)
            self.button_refresh.pack(side=tk.LEFT)
            self.label_last_url = tk.Label(self.toolbar, text='Last symbols of URL: *', font='Arial 13', bg='#fafafa')
            self.label_last_url.pack(side=tk.LEFT, padx=5)
            self.entry_last_url = tk.Entry(self.toolbar, font='Arial 13', width=14)
            self.entry_last_url.pack(side=tk.LEFT, padx=5)
            self.label_amount_images = tk.Label(self.toolbar, text='Amount of pictures: *', font='Arial 13', bg='#fafafa')
            self.label_amount_images.pack(side=tk.LEFT, padx=5)
            self.entry_amount_images = tk.Entry(self.toolbar, font='Arial 13', width=14)
            self.entry_amount_images.pack(side=tk.LEFT, padx=5)
            self.button_more_setting = tk.Button(self.toolbar, font='Arial 13', bg='#fafafa', text='More settings',
                                                 command=self.open_settings)
            self.button_more_setting.pack(side=tk.LEFT, padx=5)
            self.button_download = tk.Button(self.toolbar, text='Download', bg='#fafafa', font='Arial 13')
            self.button_download.bind('<1>', lambda event: threading.Thread(target=self.upload_files, daemon=True,
                                                                            args=(self.entry_last_url.get(),
                                                                                  self.entry_amount_images.get())).start())
            self.button_download.pack(side=tk.LEFT, padx=5)
            self.button_delete = tk.Button(self.toolbar, text='Delete all', bg='#fafafa', font='Arial 13',
                                           command=self.delete_files)
            self.button_delete.pack(side=tk.LEFT, padx=5)
            self.create_canvas()

    def open_url(self, e):
        webbrowser.open_new('https://prnt.sc/')

# DELETE ALL FILES FROM 'IMAGES' DIRECTORY
    def clear_images_frame(self):
        list = self.images_frame.grid_slaves()
        for l in list:
            l.destroy()

# CREATING SCROLLBAR, CANVAS, FRAME and PUT IMAGES INTO THE FRAME
    def create_canvas(self):
        self.image_canvas = tk.Canvas(root)
        self.scroll_y = tk.Scrollbar(root, orient='vertical', command=self.image_canvas.yview)
        self.images_frame = tk.Frame(self.image_canvas)
        self.clear_images_frame()
        counter = 0
        y = 1
        img_counter = 0
        self.images_list = [name for name in os.listdir('./images') if os.path.isfile('./images/' + name)]
        self.images = []
        for _img in self.images_list:
            try:
                self.img = Image.open('images/' + _img)
            except OSError:
                continue
            img_width = self.img.width
            img_height = self.img.height
            try:
                self.img = self.img.resize((158, 158), Image.BILINEAR)
            except IOError:
                continue
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
        self.image_canvas.create_window(0, 0, anchor='nw', window=self.images_frame)
        self.image_canvas.update_idletasks()
        self.image_canvas.configure(scrollregion=self.image_canvas.bbox('all'), yscrollcommand=self.scroll_y.set)
        self.image_canvas.pack(fill='both', expand=True, side='left')
        self.scroll_y.pack(fill='y', side='right')

# DOWNLOAD SCREENSHOTS FROM LIGHTSHOT VIA GENERATED URL
    def upload_files(self, last_url, amount):
        global str_words_to_find
        global str_words_to_ignore
        number = base36.loads(last_url)
        processed = 0
        succeeded = 0
        self.progressbar_frame = tk.Frame(root, bd=2)
        self.progressbar_frame.pack(side=tk.TOP, fill=tk.X)
        self.label_processing = tk.Label(self.progressbar_frame, text='Processed {0} of {1}'.format(processed, amount),
                                         font='Arial 15')
        self.label_processing.pack(side=tk.TOP)
        self.progressbar_downloading = ttk.Progressbar(self.progressbar_frame, length=150)
        self.progressbar_downloading.pack(side=tk.TOP)
        self.progressbar_downloading['value'] = 0
        self.progressbar_downloading['maximum'] = int(amount)
        self.redrawing_canvas()
        for _ in range(int(amount)):
            url = 'https://prnt.sc/{0}'.format(base36.dumps(number-1))
            number -= 1
            req = urllib2.Request(url, headers={'User-Agent': 'Magic Browser'})
            content1 = urllib2.urlopen(req).read().decode('utf-8')
            imgurl_temp = re.search(r'img .+src=".+" crossorigin', content1)
            img_url = re.search(r'http.+.png', imgurl_temp.group(0))
            if img_url != None:
                h = httplib2.Http('.cache')
                response, content = h.request(img_url.group(0))
                with open('./images/{0}.png'.format(base36.dumps(number)), 'wb') as out:
                    out.write(content)
                if str_words_to_find != '' or str_words_to_ignore != '':
                    text = pytesseract.image_to_string("./images/{0}.png".format(base36.dumps(number)), lang="rus+eng").lower()
                    temp_var = 0
                    check_var = False
                    if str_words_to_find != '':
                        check_var = True
                        for s in str_words_to_find.split(','):
                            if text.find(s) != -1:
                                temp_var = 1
                                break
                    if str_words_to_ignore != '':
                        for s in str_words_to_ignore.split(','):
                            if text.find(s) != -1:
                                temp_var = -1
                                break
                    if temp_var == -1 or (temp_var == 0 and check_var):
                        if os.path.exists('images/{0}.png'.format(base36.dumps(number))):
                            os.remove('images/{0}.png'.format(base36.dumps(number)))
                    else:
                        self.redrawing_canvas()
                        succeeded += 1
                else:
                    succeeded += 1
            self.progressbar_downloading.step(1)
            processed += 1
            self.label_processing['text'] = 'Processed {0} of {1} (found: {2})'.format(processed, amount, succeeded)
        self.redrawing_canvas()
        self.progressbar_frame.destroy()

# Redrawing window
    def redrawing_canvas(self):
        self.image_canvas.destroy()
        self.scroll_y.destroy()
        self.images_frame.destroy()
        self.create_canvas()

# Deleting all images from the folder
    def delete_files(self):
        self.files = [file for file in os.listdir('./images')]
        for f in self.files:
            os.remove('./images/'+f)
        self.redrawing_canvas()

# Open image in a new window
    def open_image(self, event):
        Child(event.widget['image'], self.image_buttons)

# Open settings in a new window
    def open_settings(self):
        Settings()


# CREATING CHILD-WINDOW THAT MAKE IMAGE FULL SIZE
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
        while self.w > 1000 or self.h > 600:
            self.w = int(self.w*0.9)
            self.h = int(self.h*0.9)
        self.sw = int((root.winfo_screenwidth()-self.w)/2)
        self.sh = int((root.winfo_screenheight()-self.h)/2)
        self.geometry('{0}x{1}+{2}+{3}'.format(self.w+20, self.h+20, self.sw, self.sh))
        self.img = Image.open('images/'+self.image_buttons[self._image_][2])
        self.img = self.img.resize((self.w, self.h), Image.ANTIALIAS)
        self.image = ImageTk.PhotoImage(self.img)
        self.button_big_image = tk.Button(self, width=self.w, height=self.h, image=self.image, command=self.destroy)
        self.button_big_image.pack()


class Settings(tk.Toplevel):
    def __init__(self):
        tk.Toplevel.__init__(self)
        self.os_info = platform.platform()
        self.init_settings()
        sw = int((root.winfo_screenwidth() - 770) / 2)
        sh = int((root.winfo_screenheight() - 123) / 2)
        self.geometry('770x123+{0}+{1}'.format(sw, sh))

    def init_settings(self):
        global str_words_to_find
        global str_words_to_ignore
        if self.os_info.startswith('Windows'):
            self.settings_frame = tk.Frame(self, bg='#fafafa')
            self.settings_frame.pack(side=tk.TOP, fill=tk.BOTH)
            self.label_keywords_to_find = tk.Label(self.settings_frame, bg='#fafafa', font='Arial 13',
                                                   text='Words to be found on images(sepparate by comma, or leave empty): ')
            self.label_keywords_to_find.grid(row=1, column=1, padx=10, pady=10)
            self.entry_keywords_to_find = tk.Entry(self.settings_frame, width=20, font='Arial 13', bg='#fafafa')
            self.entry_keywords_to_find.insert('0', str_words_to_find)
            self.entry_keywords_to_find.grid(row=1, column=2, padx=10, pady=10)
            self.label_keywords_to_ignore = tk.Label(self.settings_frame, font='Arial 13',
                            bg='#fafafa', text='Ignore images which include words(sepparate by comma, or leave empty): ')
            self.label_keywords_to_ignore.grid(row=2, column=1, padx=10, pady=10)
            self.entry_keywords_to_ignore = tk.Entry(self.settings_frame, width=20, font='Arial 13', bg='#fafafa')
            self.entry_keywords_to_ignore.insert('0', str_words_to_ignore)
            self.entry_keywords_to_ignore.grid(row = 2, column = 2, padx=10, pady=10)
            self.button_apply = tk.Button(self.settings_frame, bg='#e6e8ff', font='Arial 13', text='Apply', width=20,
                                                                        command=self.apply_settings)
            self.button_apply.grid(row=3, column=2)
        else:
            self.settings_frame = tk.Frame(self, bg='#fafafa')
            self.settings_frame.pack(side=tk.TOP, fill=tk.BOTH)
            self.label_keywords_to_find = tk.Label(self.settings_frame, bg='#fafafa',
                                                   text='Words to be found on images(sepparate by comma, or leave empty): ')
            self.label_keywords_to_find.grid(row=1, column=1, padx=10, pady=10)
            self.entry_keywords_to_find = tk.Entry(self.settings_frame, width=20, bg='#fafafa')
            self.entry_keywords_to_find.insert('0', str_words_to_find)
            self.entry_keywords_to_find.grid(row=1, column=2, padx=10, pady=10)
            self.label_keywords_to_ignore = tk.Label(self.settings_frame,
                                                     bg='#fafafa',
                                                     text='Ignore images which include words(sepparate by comma, or leave empty): ')
            self.label_keywords_to_ignore.grid(row=2, column=1, padx=10, pady=10)
            self.entry_keywords_to_ignore = tk.Entry(self.settings_frame, width=20, bg='#fafafa')
            self.entry_keywords_to_ignore.insert('0', str_words_to_ignore)
            self.entry_keywords_to_ignore.grid(row=2, column=2, padx=10, pady=10)
            self.button_apply = tk.Button(self.settings_frame, bg='#e6e8ff', text='Apply', width=20,
                                          command=self.apply_settings)
            self.button_apply.grid(row=3, column=2)

    def apply_settings(self):
        global str_words_to_find
        str_words_to_find = self.entry_keywords_to_find.get()
        global str_words_to_ignore
        str_words_to_ignore = self.entry_keywords_to_ignore.get()
        self.destroy()


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