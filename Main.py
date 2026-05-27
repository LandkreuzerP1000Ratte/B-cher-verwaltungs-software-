    


# I'm sorry



import os
import tkinter as tk
from datetime import *
from tkinter import *
from tkinter import ttk
import keyboard as key
import pyperclip
import cv2
from PIL import Image, ImageTk

#--------
#18ad1f
#-------


try:
    from screeninfo import get_monitors
    primary = next((m for m in get_monitors() if m.is_primary), None)
    screen_width = primary.width - 10
    screen_height = primary.height - 10
except:
    screen_width = 1920
    screen_height = 1080

work_in_progress = True # wenn True Passwort eingabe nicht nötig
manu_oder_auto = "auto"
pause = None
extra_window_ändere_pause = None
buecher = []
checkbox_vars = {}  # reset

table_entries = []
selected_row = None
columns = ["index" ,"barcode","titel","autor","verlag","status","wer","art", "cover"]

print(f'{screen_width}\n{screen_height}')

# -------------------------
# Datenklasse für ein Buch
# -------------------------
class Book:
    def __init__(self, index, barcode, titel, autor, verlag, status, wer, art, cover):
        # Attribute eines Buches
        self.index = index
        self.titel = titel
        self.autor = autor
        self.verlag = verlag
        self.barcode = barcode
        self.status = status
        self.wer = wer
        self.art = art
        self.cover = cover
        

    def __str__(self):
        # Darstellung eines Buches als String (für Listboxen)
        return f"{self.index} | {self.barcode} | {self.titel} | {self.autor} | {self.verlag} | {self.status} | {self.wer} | {self.art} | {self.cover}"
    
#-------------------------------------------------------

def donothing():  # guter anfang
    pass

#-------------------------------------------------------

def reload_table():
    
    global buecher

    tree.delete(*tree.get_children())

    for index, buch in enumerate(buecher):
        tag = "evenrow" if index % 2 == 0 else "oddrow"

        tree.insert(
            "",
            "end",
            values=(
                buch.index,
                buch.barcode,
                buch.titel,
                buch.autor,
                buch.verlag,
                buch.status,
                buch.wer,
                buch.art,
                buch.cover
            ),
            tags=(tag,)
        )

#---------------------------------------------------------------------
#---------------------------------------------------------------------
#---------------------------------------------------------------------

def make_cover(tree):
    global root2
    global cap
    global canvas
    global bar
    cap = cv2.VideoCapture(0)

    root2 = tk.Toplevel(root)
    root2.title("DroidCam Crop Tool")

    canvas = tk.Canvas(root2)
    canvas.pack()


    bar = None

    btn = Button(root2, text="Screenshot", command=barcode)
    btn.pack()

    key.add_hotkey("space", barcode)

    show_frame()
    root2.mainloop()

    cap.release()


def save(current_frame, bar):
    path = os.path.join(__location__, "data", "covers")
    cv2.imwrite(os.path.join(path, f"{bar}.png"), current_frame)
    barcode_win.destroy()
    key.remove_hotkey("space", barcode)

def redo():
    barcode_win.destroy()
    make_cover(tree)


def barcode():
    global current_frame
    global bar
    global barcode_win

    barcode_win = tk.Toplevel(root)
    barcode_win.title("Edit")
    barcode_win.geometry("700x600")

    root2.destroy()

    if current_frame is not None:
        frame_rgb = cv2.cvtColor(current_frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(img)

        panel = Label(barcode_win, image=imgtk)
        panel.image = imgtk
        panel.pack()

    e = Entry(barcode_win, font=(12))
    e.pack()
    e.focus_set()

    Button(barcode_win, text="save", command=lambda: save(current_frame, e.get())).pack(anchor="center")
    Button(barcode_win, text="redo", command=lambda: redo()).pack(anchor="center")

    selection = tree.selection()
    if selection:
        values = tree.item(selection[0])["values"]
        bar = values[0]
        e.insert(0, bar)


def show_frame():

    global current_frame

    ret, frame = cap.read()
    if ret:
        current_frame = frame

        h, w = frame.shape[:2]

        # Canvas nur setzen wenn nötig (verhindert Flackern)
        if canvas.winfo_width() != w or canvas.winfo_height() != h:
            canvas.config(width=w, height=h)

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = Image.fromarray(frame_rgb)
        imgtk = ImageTk.PhotoImage(image=img)

        canvas.imgtk = imgtk

        # Wichtig: vorher löschen, sonst werden Bilder gestapelt
        canvas.delete("all")
        canvas.create_image(0, 0, anchor="nw", image=imgtk)

    root2.after(10, show_frame)

#---------------------------------------------------------------------
#---------------------------------------------------------------------
#---------------------------------------------------------------------

def delete(tree):

    selection = tree.selection()
    if selection:
        values = tree.item(selection[0])["values"]
        bar = values[0]
        bar = str(bar) + ".png"


    path = os.path.join(__location__, "data", "covers", bar)
    os.remove(path)


#-------------------------------------------------------

def sort_buecher(event=None):
    global buecher

    suchtext = entry1.get().lower()
    kategorie = opt.get().lower()

    alle_buecher = lade_buecher(os.path.join(__location__, "data", "formated_books.txt"))

    if suchtext == "":
        buecher = alle_buecher
    else:
        buecher = []

        for buch in alle_buecher:
            wert = getattr(buch, kategorie, "").lower()
            if suchtext in wert:
                buecher.append(buch)

    reload_table()

#-------------------------------------------------------

def delete_selected_row():
    selected = tree.selection()

    if selected:
        index = tree.index(selected[0])
        tree.delete(selected)
        del buecher[index]

    reload_table()
#-------------------------------------------------------

def config_window():
    global config_window
    config_window = Toplevel(root)
    config_window.title("Bearbeiten")
    disableChildren(frame_bearbeiten)
    config_window.geometry("300x150")
    center_window(passwort_entry, round((screen_width / 2) - 300), round((screen_height / 2) - 150))
    passwort_entry.resizable(False, False)

#-------------------------------------------------------

def lade_buecher(dateiname):
    buecher = []
    path = os.path.join(__location__, "data", dateiname)

    if not os.path.exists(path):
        print(f"Datei nicht gefunden: {path}")
        return buecher

    with open(path, "r", encoding="utf-8") as f:
        for zeile in f:
            werte = [w.strip() for w in zeile.split("|")]
            # fehlende Werte mit leeren Strings auffüllen
            werte += [""] * (9 - len(werte))
            buecher.append(Book(*werte[:9]))

    return buecher

#-------------------------------------------------------

def copy_from_treeview(tree, column_index):
    selection = tree.selection()

    if not selection:
        return

    values = tree.item(selection[0])["values"]

    try:
        value = values[column_index]
        pyperclip.copy(str(value))
    except IndexError:
        print("Error")
        pass

#-------------------------------------------------------

def popup(event):
    # select row under mouse
    iid = tree.identify_row(event.y)
    if iid:
        # mouse pointer over item
        tree.selection_set(iid)

        try:
            m.tk_popup(event.x_root, event.y_root)
        finally:
            m.grab_release()

    elif iid == "":
        iid = tree.identify_region(event.x, event.y)

        if iid == "heading":
            try:
                heading_m.tk_popup(event.x_root, event.y_root)
            finally:
                m.grab_release()

    else:
        # mouse pointer not over item
        # occurs when items do not fill frame
        # no action required
        pass

#-------------------------------------------------------

def apply_column_visibility():
    """Spalten ein-/ausblenden anhand der Checkboxen."""
    for col, var in checkbox_vars.items():
        if var.get():
            tree.column(col, width=120, stretch=True)
        else:
            tree.column(col, width=0, minwidth=0, stretch=False)


def pop_change_headings():
    global change_headings
    global checkbox_vars

    # Verhindert doppeltes Öffnen
    if 'change_headings' in globals() and change_headings.winfo_exists():
        change_headings.lift()
        return

    change_headings = Toplevel(frame_bearbeiten)
    center_window(change_headings, 300, 300)
    change_headings.title("Change Headings")
    change_headings.lift()

    # Aktuellen Zustand der checkbox_vars verwenden (bereits beim Start befüllt)
    # Falls checkbox_vars noch leer: Fallback auf on_start()
    saved = {col: checkbox_vars[col].get() for col in checkbox_vars} if checkbox_vars else (on_start() or {})

    checkbox_vars = {}  # neu aufbauen für dieses Fenster

    for en, c in enumerate(columns, start=1):
            if c == "index":
                pass
            else:
                initial = saved.get(c, True)
                var = tk.BooleanVar(value=initial)
                checkbox_vars[c] = var
                Checkbutton(change_headings, text=c, variable=var).grid(row=en, sticky="w", padx=10)

    Button(
        change_headings,
        text="Anwenden",
        command=apply_column_visibility
    ).grid(row=len(columns) + 1, pady=10)

#-------------------------------------------------------

def create_table(parent, buecher):
    global tree

    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "Treeview",
        background="white",
        fieldbackground="white",
        foreground="black"
    )

    style.map("Treeview",
        background=[("selected", "#347083")]
    )

    # Gridlines aktivieren
    style.configure(
        "Treeview",
        rowheight=25,
        borderwidth=1,
        relief="solid"
    )

    style.configure(
        "Treeview.Heading",
        font=("Arial", 14, "bold"),
        borderwidth=1,
        relief="solid"
    )

    tree = ttk.Treeview(
        parent,
        columns=columns,
        show="headings",
        selectmode="browse",
        height=52
    )

    tree.tag_configure("oddrow", background="#f2f2f2")
    tree.tag_configure("evenrow", background="white")

    scrollbar = ttk.Scrollbar(parent, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scrollbar.set)

    tree.grid(row=0, column=0, sticky="nsew")
    scrollbar.grid(row=0, column=1, sticky="ns")

    parent.columnconfigure(0, weight=1)
    parent.rowconfigure(0, weight=1)

    for col in columns:
        tree.heading(col, text=col.capitalize())

        if col == "index":
            tree.column(col, width=0, minwidth=0, stretch=False)
        else:
            tree.column(col, anchor="w", stretch=True)

    get_width(tree)

    # Daten einfügen
    for buch in buecher:

        tag = "evenrow" if int(buch.index) % 2 == 0 else "oddrow"

        tree.insert(
            "",
            "end",
            values=(
                buch.index,
                buch.barcode,
                buch.titel,
                buch.autor,
                buch.verlag,
                buch.status,
                buch.wer,
                buch.art,
                buch.cover
            ),
            tags=(tag,)
        )

    tree.bind("<Button-3>", popup)

#-------------------------------------------------------

def get_width(tree):
    path = os.path.join(__location__, "data.txt")

    if not os.path.exists(path):
        return

    with open(path, "r", encoding="utf-8") as data:
        line = data.readline().strip()
        cols = line.split(" / ")

        for col in cols:
            print(col)
            if ":" not in col:
                continue

            name, width = col.split(":")
            name = name.strip()
            width = int(width.strip())

            if width == 0:
                tree.column(name, width=0, minwidth=0, stretch=False)
                
            else:
                tree.column(name, width=width)

#-------------------------------------------------------

def save_books(tree):
    path = os.path.join(__location__, "data", "formated_books.txt")

    with open(path, "w", encoding="utf-8") as f:
        for item_id in tree.get_children():
            values = tree.item(item_id, "values")
            line = " | ".join(str(v) for v in values)
            f.write(line + "\n")
            print(f"saved: {line}")

#-------------------------------------------------------

def update_time():
    jetzt = datetime.now()
    Time.set(jetzt.strftime("%Y.%m.%d | %H:%M"))
    root.after(1000, update_time)

#-------------------------------------------------------

def pause_invent():
    global pause

    if pause.get() == "Pause 2":
        pause.set("Pause 1")
    elif pause.get() == "Pause 1":
        pause.set("Pause 2")
    else:
        print("ValueError loc = def pause_invent")
        print(pause.get())
        pass

#-------------------------------------------------------

def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x = int((screen_width / 2) - (width / 2))
    y = int((screen_height / 2) - (height / 2))
    root.geometry(f"{width}x{height}+{x}+{y-150}")

#-------------------------------------------------------

def datum(Time, pause):
    def update_time():
        if not frame_bearbeiten.winfo_exists():
            return

        jetzt = datetime.now()
        jahr = int(jetzt.strftime("%Y"))
        monat = int(jetzt.strftime("%m"))
        tag = int(jetzt.strftime("%d"))
        stunde = int(jetzt.strftime("%H"))
        minute = int(jetzt.strftime("%M"))

        Time.set(f"{jahr:04d}.{monat:02d}.{tag:02d} | {stunde:02d}:{minute:02d}")

        # pause bestimmen
        if manu_oder_auto == "auto":
            if stunde > 9 or (stunde == 9 and minute >= 45):
                pause.set("Pause 2")
            else:
                pause.set("Pause 1")
        else:
            pass

        root.after(1000, update_time)

    update_time()

#-------------------------------------------------------

def change_button3_text():
    global manu_oder_auto

    if manu_oder_auto == "auto":
        manu_oder_auto = "manu"
        Button3.config(text="Manuel")

    elif manu_oder_auto == "manu":
        manu_oder_auto = "auto"
        Button3.config(text="Automatisch")

#-------------------------------------------------------

def ändere_pause():
    global extra_window_ändere_pause

    # Falls Fenster nie existierte oder bereits geschlossen wurde:
    if extra_window_ändere_pause is None or not extra_window_ändere_pause.winfo_exists():

        extra_window_ändere_pause = Toplevel(root)
        center_window(extra_window_ändere_pause, 300, 150)
        extra_window_ändere_pause.title("Pause ändern")
        extra_window_ändere_pause.lift()

        Button1 = Button(extra_window_ändere_pause, command=pause_invent,
                         text="Pause ändern", font=("Arial", 14))
        Button1.pack(anchor="center", pady=10)

        global Button3
        Button3 = Button(extra_window_ändere_pause, command=change_button3_text,
                         text="Automatisch", font=("Arial", 14))
        Button3.pack(anchor="center", pady=10)
    else:
        extra_window_ändere_pause.lift()

#-------------------------------------------------------

def zeige_frame(frame):
    frame.tkraise()

#-------------------------------------------------------

def disableChildren(parent):
    for child in parent.winfo_children():
        wtype = child.winfo_class()
        if wtype not in ('Frame', 'Labelframe', 'TFrame', 'TLabelframe', 'TSeparator'):
            child.configure(state='disable')
        else:
            disableChildren(child)

#-------------------------------------------------------

def enableChildren(parent):
    for child in parent.winfo_children():
        wtype = child.winfo_class()
        print(wtype)
        if wtype not in ('Frame', 'Labelframe', 'TFrame', 'TLabelframe', 'TSeparator'):
            child.configure(state='normal')
        else:
            enableChildren(child)

#-------------------------------------------------------

def destroy_all():
    root.destroy()

#-------------------------------------------------------

def check_login():
    if entry_passwort_entry.get() == "Biblio01":
        passwort_entry_label.config(text="✅ Zugriff erlaubt", fg="green")
        enableChildren(frame_start)
        passwort_entry.destroy()
    else:
        passwort_entry_label.config(text="❌ Falsches Passwort", fg="red")

#-------------------------------------------------------

def password():
    global passwort_entry_label
    global entry_passwort_entry
    global passwort_entry

    if work_in_progress == True:
        print("test")
        pass
    else:

        disableChildren(frame_start)
        passwort_entry = Toplevel(root)
        passwort_entry.title("Anmeldung")
        passwort_entry.geometry("300x150")
        center_window(passwort_entry, round((screen_width / 2) - 300), round((screen_height / 2) - 150))
        passwort_entry.resizable(False, False)
        passwort_entry.protocol('WM_DELETE_WINDOW', destroy_all)

        passwort_entry.transient(root)
        passwort_entry.grab_set()
        passwort_entry.attributes("-topmost", True)
        passwort_entry.focus_force()

        entry_passwort_entry = Entry(passwort_entry, show="*", text="password")
        entry_passwort_entry.pack(anchor=NW, padx=10, pady=7)

        login_button_button = Button(passwort_entry, text="login", command=check_login)
        

        passwort_entry_label = Label(passwort_entry, text="", font=("Arial", 11), bg="#f0f0f0")
        passwort_entry_label.pack(anchor=NW, padx=10)

        # Jetzt Return-Taste mit Login verknüpfen
        passwort_entry.bind('<Return>', lambda event: check_login())

#-------------------------------------------------------

def on_mousewheel(event):
    if not key.is_pressed("strg"):
        tree.yview_scroll(int(-1 * (event.delta / 120) * 4), "units")
    else:
        tree.yview_scroll(int(-1 * (event.delta / 120) * 0.5), "pages")

#-------------------------------------------------------

def on_close():
    colums = ("barcode", "titel", "autor", "verlag", "status", "wer", "art", "cover")
    path = os.path.join(__location__, "data.txt")

    with open(path, "w", encoding="utf-8") as data:

        # Zeile 1: Spaltenbreiten
        for colum in colums:
            width = tree.column(colum, "width")
            if colum != "cover":
                data.write(f"{colum}:{width} / ")
            else:
                data.write(f"{colum}:{width}\n")

        # Zeile 2: Checkbox-Sichtbarkeit (1 = sichtbar, 0 = versteckt)
        visibility = []
        for col in colums:
            val = checkbox_vars[col].get() if col in checkbox_vars else True
            visibility.append(f"{col}:{'1' if val else '0'}")
        data.write(" / ".join(visibility) + "\n")

    root.quit()

#-------------------------------------------------------

def on_start():
    """Lädt gespeicherte Checkbox-Sichtbarkeit aus data.txt (Zeile 2).
    Gibt Dict zurück: {"barcode": True, "titel": False, ...}
    oder None wenn Datei fehlt / Zeile 2 nicht existiert."""
    path = os.path.join(__location__, "data.txt")

    if not os.path.exists(path):
        return None

    with open(path, "r", encoding="utf-8") as data:
        lines = data.readlines()

    if len(lines) < 2:
        return None

    saved = {}
    for entry in lines[1].strip().split(" / "):
        if ":" in entry:
            name, val = entry.split(":", 1)
            saved[name.strip()] = val.strip() == "1"

    return saved

#-------------------------------------------------------

def info_text(event=None):
    """Zeigt alle Felder des ausgewählten Buches im info_frame an."""
    selection = tree.selection()

    for widget in info_frame.winfo_children():
        widget.destroy()

    if not selection:
        Label(info_frame, text="Kein Buch ausgewählt", bg="#34700c",
              fg="white", font=("Arial", 9, "italic")).pack(padx=5, pady=10)
        return

    values = tree.item(selection[0])["values"]

    # Felder anzeigen
    for c, v in zip(columns, values):
        if c == "index":
            continue
        Label(info_frame, text=c.capitalize(), bg="#1fc76a", fg="white",
              font=("Arial", 9, "bold"), anchor="w").pack(fill="x", padx=5, pady=(4, 0))
        Label(info_frame, text=v, bg="#30aa67", fg="white",
              font=("Arial", 9), anchor="w").pack(fill="x", padx=10)

# Cover laden
    data = dict(zip(columns, values))
    cover_name = data.get("index", "")

    if cover_name:
        image_path = os.path.join(__location__, "data", "covers", f"{cover_name}.png")
        print(image_path)

        if os.path.exists(image_path):
            img = Image.open(image_path)
            img.thumbnail((200, 200))
            imgtk = ImageTk.PhotoImage(img)

            panel = Label(info_frame, image=imgtk, bg="#26774a")
            panel.image = imgtk
            panel.pack(pady=10)
        else:
            Label(info_frame, text="Kein Cover gefunden", bg="#26774a",
                  fg="white", font=("Arial", 8, "italic")).pack(pady=5)
    

#-------------------------------------------------------


# -------------------------
# Hauptprogramm
# -------------------------
root = Tk()
root.title("Bücherverwaltung")
root.attributes("-fullscreen", True)
root.protocol("WM_DELETE_WINDOW", on_close)
root.bind_all("<MouseWheel>", on_mousewheel)

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

print(__location__)

# Frames erstellen (Seiten)
frame_start = Frame(root, bg="#f0f0f0")
frame_bearbeiten = Frame(root, bg="#26774a")
frame_ausleihe = Frame(root, bg="#f0f0f0")
frame_pausen_protokoll = Frame(root, bg="#f0f0f0")
frame_einstellungen = Frame(root, bg="#f0f0f0")

# Alle Frames im Fenster platzieren (übereinander)
for frame in (frame_start, frame_bearbeiten, frame_ausleihe, frame_pausen_protokoll):
    frame.place(relwidth=1, relheight=1)

    menubar = Menu(root)
root.config(menu=menubar)


filemenu1 = Menu(menubar, tearoff=0)
menubar.add_cascade(label="genereal", menu=filemenu1)

filemenu1.add_command(label="test")
filemenu1.add_separator()
filemenu1.add_command(label="close", command=on_close)


filemenu2 = Menu(menubar, tearoff=0)
menubar.add_cascade(label="students", menu=filemenu2)

filemenu2.add_command(label="search", command=donothing)


filemenu3 = Menu(menubar, tearoff=0)
menubar.add_cascade(label="books", menu=filemenu3)

filemenu3.add_command(label="configure",   command=lambda: zeige_frame(frame_bearbeiten))
filemenu3.add_command(label="save",        command=lambda: save_books(tree))


filemenu4 = Menu(menubar, tearoff=0)
menubar.add_cascade(label="borrow", menu=filemenu4)


filemenu5 = Menu(menubar, tearoff=0)
menubar.add_cascade(label="protocol", menu=filemenu5)


# -------------------------
# Startseite mit Login links
# -------------------------
frame_start = Frame(root, bg="#f0f0f0")
frame_start.place(relwidth=1, relheight=1)

# Container für Left | Separator | Right 
start_container = Frame(frame_start, bg="#f0f0f0")
start_container.pack(side="right", fill="both", expand=True)

# -------------------------
# LEFT FRAME
# -------------------------
frame_start_left = Frame(start_container, bg="#f0f0f0")
frame_start_left.pack(side="left", fill="both", expand=True)

# -------------------------
# SEPARATOR
# -------------------------
separator = ttk.Separator(start_container, orient="vertical")
separator.place(
    x=int(start_container.winfo_screenwidth() * 0.5),
    y=0,
    relheight=1
)

# -------------------------
# RIGHT FRAME
# -------------------------
frame_start_right = Frame(start_container, bg="#f0f0f0")
frame_start_right.pack(side="left", fill="both", expand=True)

# Rechte Seite = Buttons
frame_buttons = Frame(frame_start_right,
                       bg="#000000")
frame_buttons.pack(side="right",
                    anchor="n",
                      padx=100)

buttons = []
btn1 = Button(frame_buttons, text="Bücher bearbeiten",
               font=("Arial", 20),
                 command=lambda: zeige_frame(frame_bearbeiten))

if work_in_progress != True:
    btn1.config(state="disabled")
btn1.pack(pady=20)
buttons.append(btn1)




# -------------------------
# Bücher bearbeiten
# -------------------------
container = Frame(frame_bearbeiten, bg="#fffff0f0f0ff")
container.place(relx=0, rely=0, relwidth=0.835, relheight=1)

container.columnconfigure(0, weight=1)
container.rowconfigure(0, weight=1)

separator = ttk.Separator(frame_bearbeiten, orient="vertical")
separator.place(
    relx=0.835,
    rely=0,
    relheight=1)

#------------------------------------------------------------------------------

drop_down_op = []

for index, x in enumerate(columns):
    if index == 0:
        pass
    else:
        drop_down_op.append(x)



opt = StringVar(value="Barcode")
search_options = ttk.OptionMenu(frame_bearbeiten, opt, drop_down_op[0], *drop_down_op).place(x=1899-260 ,y=15)

#------------------------------------------------------------------------------

entry1 = Entry(frame_bearbeiten, width=40)
entry1.place(x=1900-262, y=40)
entry1.focus_set()

entry1.bind("<KeyRelease>", sort_buecher)

#------------------------------------------------------------------------------

Time = tk.StringVar()  # Tkinter-Variable für Label/Button
pause = tk.StringVar()
datum(Time, pause)

#------------------------------------------------------------------------------

Button2 = Button(frame_bearbeiten ,textvariable=Time ,width=15 ,height=(1) ,font=("Arial", 8)).place(x=1773, y=0)

#------------------------------------------------------------------------------

Button3 = Button(frame_bearbeiten ,textvariable=pause ,command=ändere_pause ,width=6, height=(1) ,font=("Arial", 8)).place(x=1873, y=0)

#------------------------------------------------------------------------------


table_frame = Frame(container, bg="#f0f0f0")
table_frame.grid(row=0, column=0, sticky="nsew")

buecher = "formated_books.txt"
buecher = lade_buecher(buecher)  
create_table(table_frame, buecher)

tree.bind("<<TreeviewSelect>>", info_text)

#------------------------------------------------------------------------------

ttk.Separator(frame_bearbeiten, orient="horizontal", ).place(
    relx=0.836,
    rely=0.08,
    relwidth=0.19)

#------------------------------------------------------------------------------

info_frame = Frame(frame_bearbeiten, bg="#26774a")
info_frame.place(relx=0.836, rely=0.09, relwidth=0.164, relheight=0.91)

#------------------------------------------------------------------------------

info_text()

#------------------------------------------------------------------------------

m = Menu(root, tearoff=0)


m1 = Menu(m, tearoff=0)
m.add_cascade(label="Kopieren", menu=m1)

m1.add_command(label="Barcode", command=lambda: copy_from_treeview(tree, 0))
m1.add_command(label="Titel", command=lambda: copy_from_treeview(tree, 1))
m1.add_command(label="Autor", command=lambda: copy_from_treeview(tree, 2))
m1.add_command(label="Verlag", command=lambda: copy_from_treeview(tree, 3))



m2 = Menu(m, tearoff=0)
m.add_cascade(label="Bild", menu=m2)

m2.add_command(label="Neues Bild", command=lambda: make_cover(tree))
m2.add_command(label="Bild Bearbeiten", command=donothing)
m2.add_command(label="Größe ändern", command=donothing)
m2.add_command(label="Löschen", command=lambda: delete(tree))


m.add_separator()
m.add_command(label="Löschen")
m.add_command(label="Neu")
m.add_command(label="Bearbeiten", command=info_text)

heading_m = Menu(root,tearoff=0)

heading_m.add_command(label="change headings", command=pop_change_headings)



#------------------------------------------------------------------------------

# -------------------------
# Ausleihe
# -------------------------
Label(frame_ausleihe,
       text="Ausleihe",
         font=("Arial", 28),
           bg="#f0f0f0").pack(pady=20)

#------------------------------------------------------------------------------

# -------------------------
# Einstellungen
# -------------------------
Label1 = Label(frame_einstellungen, text="Error 404", font=("Arial", 28), bg="#f0f0f0").pack(pady=20)
Label2 = Label(frame_einstellungen, text="Work in procress", font=("Arial", 28), bg="#f0f0f0").pack(pady=20)

# -------------------------
# Pausen Protokoll
# -------------------------

Label1 = Label(frame_pausen_protokoll, text="Ausleihe", font=("Arial", 28), bg="#f0f0f0").pack(pady=20)


# -------------------------
# Startseite anzeigen
# -------------------------

zeige_frame(frame_start)
zeige_frame(frame_bearbeiten)
password()
root.mainloop()
