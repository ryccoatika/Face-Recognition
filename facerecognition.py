from future.moves import tkinter as tk
from tkinter import filedialog
from tkinter import simpledialog
from tkinter import messagebox
import sqlModule
import face_recognition
from PIL import ImageTk, Image
import cv2
import numpy as np

known_face_names = []
known_face_encodings = []


# untuk merefresh variable known_face... dengan database
def refresh():
    # untuk mengakses variable global
    global known_face_names
    global known_face_encodings
    known_face_names = []
    known_face_encodings = []
    # get data nama dan face encoding dari database
    cursor = sqlModule.get_people_encoding()
    for row in cursor:
        known_face_names.append(row[0])
        known_face_encodings.append(list(map(float, (row[1].split(' ')))))


# box refresh untuk merefresh box yang terdapat di window add dan delete
def box_refresh(listbox):
    # menghapus semua item dalam box
    listbox.delete(0, tk.END)
    # merefresh list known_face...
    refresh()
    # mengakses variable known_face...
    global known_face_names

    # menampilkan item yang ada di variable known_face ke listbox
    idx = 1
    for name in known_face_names:
        listbox.insert(idx, name)
        idx = idx + 1


# function untuk command ketika menu add face ditekan
def add_face():
    # memunculkan window baru dan listbox (tambah wajah)
    addwindow = tk.Toplevel(mainWindow)
    listbox = tk.Listbox(addwindow)

    # refreshing listbox
    box_refresh(listbox)

    # function untuk command saat button add photo ditekan
    def add_photos():
        # menampilkan filedialog untuk mengambil file pada filesystem
        mainWindow.filename = filedialog.askopenfilename(initialdir='~',
                                                         title='Select a Picture',
                                                         filetypes=(('jpeg files', '*.jpg'),
                                                                    ('jpeg files', '*.jpeg'),
                                                                    ('all files', '*.*')))
        # jika terdapat file yang dipilih
        if mainWindow.filename != ():
            # menampilkan simple dialog untuk memasukkan nama
            name = simpledialog.askstring('Input', 'What\'s your name?', parent=mainWindow)
            # jika form nama tidak kosong
            if name is not None:
                # load image file to variable
                image = face_recognition.load_image_file(mainWindow.filename)
                # encode image
                face_encode = face_recognition.face_encodings(image)
                # jika gambar valid (terdapat wajah)
                if face_encode != []:
                    # menambahkan nama dan gambar ke database
                    sqlModule.insert_people_encoding(name, face_encode)
                    # merefresh listbox
                    box_refresh(listbox)
                # jika tidak ada wajah yang terdeteksi
                else:
                    print('face not detected')
            # jika form nama kosong
            else:
                print('name must be filled')
        # jika tidak ada file yang dipilih
        else:
            print('no file selected')

    # menambahkan button tambah photo
    add_btn = tk.Button(addwindow, text='Add photo', command=add_photos)
    add_btn.pack(side=tk.BOTTOM)

    listbox.pack()


# function untuk command ketika menu delete face ditekan
def del_face():
    # memunculkan window baru dan listbox (hapus wajah)
    del_window = tk.Toplevel(mainWindow)
    listbox = tk.Listbox(del_window)

    # merefresh listbox
    box_refresh(listbox)

    # function untuk command ketika tombol delete ditekan
    def del_name():
        # jika terdapat nama yang dipilih dalam listbox
        if listbox.curselection() != ():
            # mengampil nama yang dipilih
            nama = listbox.get(listbox.curselection())
            # menampilkan messagebox question yes or no
            msg_box = messagebox.askyesno('Delete Face', 'Are you sure want to delete ' + nama
                                          + ' face?', icon='warning')
            # jika menekan tombol yes
            if msg_box:
                # menghapus data wajah berdasarkan nama
                sqlModule.delete_people_encoding(nama)
                # merefresh listbox
                box_refresh(listbox)

    # menambahkan button delete wajah
    del_btn = tk.Button(del_window, text='Delete', command=del_name)
    del_btn.pack(side=tk.BOTTOM)

    listbox.pack()


# function untuk menampilkan camera pada window
def show_recog_cam():
    # menentukan lebar dan tinggi video yang ditampilkan
    width, height = 800, 600
    # make an instance
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    # mengambil per frame dari video
    _, frame = cam.read()
    # mengubah ukuran untuk mempercepat proses
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    # reversing image
    rgb_small_frame = small_frame[:, :, ::-1]

    # mengakses variable global
    global known_face_names
    global known_face_encodings

    # get face location and encodings
    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
    face_names = []
    # get all data from face_encodings
    for face_encoding in face_encodings:
        # digunakan jika wajah yang didapat tidak terdapat di database
        name = 'stranger'
        # jika known_face tidak kosong atau di database terdapat data wajah yang disimpan
        if known_face_names != []:
            # compare wajah yang tersimpan dengan wajah yang terdeteksi pada setiap frame video
            # compare_faces returning list nilai T atau F dari face yg match
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding, tolerance=0.4)
            # mendapatkan euclidean distance dari face yang dicompare
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            # np.argmin digunakan untuk mendapatkan index dari list of array yang memiliki nilai minimum
            best_match_index = np.argmin(face_distances)
            # jika index best_match_index pada list matches adalah True
            if matches[best_match_index]:
                # get nama dari list known_face_names
                name = known_face_names[best_match_index]
        # menambahkan nama kedalam list nama yang terdeteksi
        face_names.append(name)

    # create rectangle pada frame berdasar face yang terdeteksi
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # diperbesar karena tadi frame diperkecil
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # menggambar rectangle dan text pada wajah
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (right+6, top+10), font, 0.8, (0, 255, 0), 1)

    # convert color from BGR to RGBA
    cv2img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    # get image from array
    img = Image.fromarray(cv2img)
    # create instance of ImageTk and add it into mainwindow
    imgtk = ImageTk.PhotoImage(image=img)
    main_window.imgtk = imgtk
    main_window.configure(image=imgtk)
    main_window.after(8, show_recog_cam)


if __name__ == '__main__':
    mainWindow = tk.Tk()
    mainWindow.bind('<Escape>', lambda e: mainWindow.quit())
    main_window = tk.Label(mainWindow)
    main_window.pack()

    # initiate connection to database
    sqlModule.init_connection()

    # refreshing known_face... list
    refresh()

    menuBar = tk.Menu(mainWindow)

    fileMenu = tk.Menu(menuBar, tearoff=0)
    fileMenu.add_command(label='Add New Face', command=add_face)
    fileMenu.add_command(label="Delete Face", command=del_face)
    fileMenu.add_separator()
    fileMenu.add_command(label='Exit', command=mainWindow.quit)
    menuBar.add_cascade(label='File', menu=fileMenu)

    mainWindow.config(menu=menuBar)
    show_recog_cam()
    mainWindow.mainloop()
