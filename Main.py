
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
import subprocess
import pygetwindow as gw


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
checkbox_vars = {}

table_entries = []
selected_row = None
button = None
columns = ["index" ,"barcode","titel","autor","verlag","status","wer","art", "cover"]

# -------------------------
# Datenklasse für ein Buch
# -------------------------
class Book:
    def __init__(self, index, barcode, titel, autor, verlag, status, wer, art, cover):
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
        return f"{self.index} | {self.barcode} | {self.titel} | {self.autor} | {self.verlag} | {self.status} | {self.wer} | {self.art} | {self.cover}"
    
    class Schuler:
        def __init__(self, index, name, ausgeliehen, was, verbot, bis, stand):
            self.index = index
            self.name = name
            self.ausgeliehen = ausgeliehen
            self.was = was
            self.verbot = verbot
            self.bis = bis
            self.stand = stand

        def __str__(self):
            return f"{self.index} | {self.name} | {self.ausgeliehen} | {self.was} | {self.verbot} | {self.bis} | {self.wer} | {self.stand}"

#-------------------------------------------------------

def donothing():  # guter anfang
    pass

#-------------------------------------------------------

def reload_table(art):

    global buecher

    tree.delete(*tree.get_children())

    if art == "bucher":
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

    elif art == "schuler":
        pass

    else:
        print(f"{art} is not an option")


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
    root2.title("new cover")

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
    key.remove_hotkey("space")

def redo():
    barcode_win.destroy()
    make_cover(tree)


def barcode():

    key.remove_hotkey("space")
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
        bar = values[1]
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
    print("f")
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

def save_books(tree):
    global buecher

    # Erst gefilterte Änderungen zurück in die globale Liste schreiben
    alle_buecher = lade_buecher("formated_books.txt")

    # Index-basiertes Dict der geladenen Bücher
    buecher_dict = {b.index: b for b in alle_buecher}

    # Sichtbare Einträge im Tree aktualisieren
    for item_id in tree.get_children():
        values = tree.item(item_id, "values")
        idx = str(values[0])
        if idx in buecher_dict:
            b = buecher_dict[idx]
            b.index   = values[0]
            b.barcode = values[1]
            b.titel   = values[2]
            b.autor   = values[3]
            b.verlag  = values[4]
            b.status  = values[5]
            b.wer     = values[6]
            b.art     = values[7]
            b.cover   = values[8]


    path = os.path.join(__location__, "data", "formated_books.txt")
    with open(path, "w", encoding="utf-8") as f:
        for b in buecher_dict.values():
            line = f"{b.index} | {b.barcode} | {b.titel} | {b.autor} | {b.verlag} | {b.status} | {b.wer} | {b.art} | {b.cover}"
            f.write(line + "\n")
            print(f"saved: {line}")

#-------------------------------------------------------

def delete_selected_row():
    selected = tree.selection()

    if selected:
        index = tree.index(selected[0])
        tree.delete(selected)
        del buecher[index]

    reload_table("bucher")
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

#-------------------------------------------------------

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

#---------------------------------------------------------

def create_table(parent, buecher):
    global tree

    style = ttk.Style()
    style.theme_use("default")

    style.configure(
        "Treeview",
        background="white",
        fieldbackground="white",
        foreground="lightgrey"
    )

    style.map("Treeview",
        background=[("selected", "#26A760")]
    )

    style.map(
        "Treeview.Heading",
        background=[("active", "#278652")],
        foreground=[("active", "white")]
    )

    style.configure(
        "Treeview",
        rowheight=25,
        borderwidth=1,
        relief="solid"
    )

    style.configure(
        "Treeview.Heading",
        font=("Arial", 14, "bold"),
        background="#278652",
        foreground="white",
        relief="groove",
        borderwidth=1

    )
    tree = ttk.Treeview(
        parent,
        columns=columns,
        show="headings",
        selectmode="browse",
        height=52
    )

    style.configure(
    "Vertical.TScrollbar",
    background="#289157",
    troughcolor="#26774a",
    arrowcolor="white",
    bordercolor="#289157",
    lightcolor="#289157",
    darkcolor="#1a5c38"
    
    )

    style.map(
        "Vertical.TScrollbar",
        background=[("active", "#26A760")]
    )

    tree.tag_configure("evenrow", background="#289157")
    tree.tag_configure("oddrow", background="#26774a")


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

#---------------------------------------------------------

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

    reload_table("bucher")

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

def change_info_text(buton):
    global button

    if buton == "left":
        button = "left"
        info_text_left()
        info_button_left.config(relief="sunken")
        info_button_right.config(relief="raised")
    else:
        button = "right"
        info_text_right()
        info_button_left.config(relief="raised")
        info_button_right.config(relief="sunken")

#-------------------------------------------------------

def info_text_left(event=None):
    global button

    if button == "left":
        selection = tree.selection()

        for widget in info_frame.winfo_children():
            if widget != info_button_left and widget != info_button_right:
                widget.destroy()

        if not selection:
            Label(info_frame, text="Kein Buch ausgewählt", bg="#30aa67",
                fg="white", font=("Arial", 9, "italic")).pack(padx=5, pady=30)
            return

        values = tree.item(selection[0])["values"]

        Frame(info_frame, bg="#26774a", height=30).pack(fill="x")

        for c, v in zip(columns, values):
            if c == "index":
                continue
            Label(info_frame, text=c.capitalize(), bg="#1fc76a", fg="white",
                font=("Arial", 9, "bold"), anchor="w").pack(fill="x", padx=5, pady=(5, 0))
            Label(info_frame, text=v, bg="#30aa67", fg="white",
                font=("Arial", 9), anchor="w").pack(fill="x", padx=10)

    # Cover laden
        data = dict(zip(columns, values))
        cover_name = data.get("barcode", "")

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
    else:
        pass

#-------------------------------------------------------

def info_text_right():
    global info_frame

    for widget in info_frame.winfo_children():
        if widget != info_button_left and widget != info_button_right:
            widget.destroy()

    Button(info_frame, text="current", bg="#289157", activebackground="#289157", fg="white", activeforeground="white").pack(pady=20)
    Button(info_frame, text="schüler", bg="#289157", activebackground="#289157", fg="white", activeforeground="white").pack()
    Button(info_frame, text="ich weis doch auch nicht", bg="#289157", activebackground="#289157", fg="white", activeforeground="white").pack()

#-------------------------------------------------------

def check_covers():
    alle_buecher = lade_buecher("formated_books.txt")
    covers_path = os.path.join(__location__, "data", "covers")

    for buch in alle_buecher:
        image_path = os.path.join(covers_path, f"{buch.barcode}.png")
        buch.cover = "True" if os.path.exists(image_path) else "False"

    path = os.path.join(__location__, "data", "formated_books.txt")
    with open(path, "w", encoding="utf-8") as f:
        for b in alle_buecher:
            line = f"{b.index} | {b.barcode} | {b.titel} | {b.autor} | {b.verlag} | {b.status} | {b.wer} | {b.art} | {b.cover}"
            f.write(line + "\n")

    reload_table("bucher")

#-------------------------------------------------------

def cover_bearbeiten():

    selection = tree.selection()
    if selection:
        values = tree.item(selection[0])["values"]
        bar = values[1]

    path = os.path.join(__location__, "data", "covers")
    subprocess.run(['explorer', (os.path.join(path, f"{bar}.png"))])

    wins = gw.getWindowsWithTitle('Windows-Fotoanzeige')

    if wins:
        wins[0].activate()

#-------------------------------------------------------



# -------------------------
# Hauptprogramm
# -------------------------
root = Tk()
root.title("Bücherverwaltung")
root.attributes("-fullscreen", True)
root.protocol("WM_DELETE_WINDOW", on_close)
root.bind_all("<MouseWheel>", on_mousewheel)
root.config(bg="#289157")

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

print(__location__)

# Frames erstellen (Seiten)
frame_start = Frame(root, bg="#289157")
frame_bearbeiten = Frame(root, bg="#26774a")


# Alle Frames im Fenster platzieren (übereinander)
for frame in (frame_start, frame_bearbeiten):
    frame.place(relwidth=1, relheight=1)



# -------------------------
# Startseite mit Login links
# -------------------------
frame_start = Frame(root, bg="#289157")
frame_start.place(relwidth=1, relheight=1)

# Container für Left | Separator | Right 
start_container = Frame(frame_start, bg="#289157")
start_container.pack(side="right", fill="both", expand=True)

# -------------------------
# LEFT FRAME
# -------------------------
frame_start_left = Frame(start_container, bg="#289157")
frame_start_left.pack(side="left", fill="both", expand=True)


# -------------------------
# RIGHT FRAME
# -------------------------
frame_start_right = Frame(start_container, bg="#289157")
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
container = Frame(frame_bearbeiten, bg="#289157")
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
    if index != 0:
        drop_down_op.append(x)

opt = StringVar(value="barcode")

search_options = tk.Menubutton(frame_bearbeiten,
    textvariable=opt,
    bg="#289157",
    fg="white",
    activebackground="#289157",
    activeforeground="white",
    font=("Calibri", 11),
    relief="flat",
    bd=0,
    highlightthickness=0,
    indicatoron=True,
    width=10
)

menu = tk.Menu(search_options, tearoff=0,
    bg="#289157",
    fg="white",
    activebackground="#289157",
    activeforeground="white",
    font=("Calibri", 11),
    borderwidth=0,
    relief="flat",
    activeborderwidth=0
)

menu.config(bg="#289157")

for option in drop_down_op:
    menu.add_command(label=option, command=lambda o=option: opt.set(o))

search_options.config(menu=menu)
search_options.place(x=1899-260, y=15)

#------------------------------------------------------------------------------

entry1 = Entry(frame_bearbeiten, width=40, background="#289157")
entry1.place(x=1900-262, y=40)
entry1.focus_set()

entry1.bind("<KeyRelease>", sort_buecher)

#------------------------------------------------------------------------------

Time = tk.StringVar()  # Tkinter-Variable für Label/Button
pause = tk.StringVar()
datum(Time, pause)

#------------------------------------------------------------------------------

Button2 = Button(frame_bearbeiten ,bg="#289157", fg="white", textvariable=Time, width=15 ,height=(1) ,font=("Arial", 8)).place(x=1773, y=0)

#------------------------------------------------------------------------------

Button3 = Button(frame_bearbeiten ,bg="#289157", fg="white", textvariable=pause ,command=ändere_pause ,width=6, height=(1) ,font=("Arial", 8)).place(x=1873, y=0)

#------------------------------------------------------------------------------


table_frame = Frame(container, bg="#289157")
table_frame.grid(row=0, column=0, sticky="nsew")

buecher = "formated_books.txt"
buecher = lade_buecher(buecher)  
create_table(table_frame, buecher)

tree.bind("<<TreeviewSelect>>", info_text_left)

#------------------------------------------------------------------------------

ttk.Separator(frame_bearbeiten, orient="horizontal", ).place(
    relx=0.836,
    rely=0.08,
    relwidth=0.19)

#------------------------------------------------------------------------------


info_frame = Frame(frame_bearbeiten, bg="#26774a")
info_frame.place(relx=0.836, rely=0.09, relwidth=0.164, relheight=0.91)


info_button_left = Button(frame_bearbeiten, text="Bücher", bg="#289157",
    activebackground="#289157", fg="white", relief="sunken",
    activeforeground="white",
    command=lambda: change_info_text(buton="left"))
info_button_left.place(relx=0.836, rely=0.0818, relwidth=0.0815)

info_button_right = Button(frame_bearbeiten, text="Frames", bg="#289157",
    activebackground="#289157", fg="white", relief="raised",
    activeforeground="white",
    command=lambda: change_info_text(buton="right"))
info_button_right.place(relx=0.916, rely=0.0818, relwidth=0.084)


#------------------------------------------------------------------------------

info_text_left()

#------------------------------------------------------------------------------

m = Menu(root, tearoff=0, bg="#289157", activebackground="#289157", fg="white")


m1 = Menu(m, tearoff=0)
m1.config(bg="#289157", fg="white")
m.add_cascade(label="Kopieren", menu=m1)

m1.add_command(label="Barcode", command=lambda: copy_from_treeview(tree, 0))
m1.add_command(label="Titel", command=lambda: copy_from_treeview(tree, 1))
m1.add_command(label="Autor", command=lambda: copy_from_treeview(tree, 2))
m1.add_command(label="Verlag", command=lambda: copy_from_treeview(tree, 3))


m2 = Menu(m, tearoff=0)
m2.config(bg="#289157", fg="white")
m.add_cascade(label="Bild", menu=m2)

m2.add_command(label="Neues Bild", command=lambda: make_cover(tree))
m2.add_command(label="Bild Bearbeiten", command=cover_bearbeiten)
m2.add_command(label="Check Covers", command=check_covers)
m2.add_command(label="Löschen", command=lambda: delete(tree))


m.add_separator()
m.add_command(label="Löschen")
m.add_command(label="Neu")
m.add_command(label="Bearbeiten", command=info_text_left)

heading_m = Menu(root,tearoff=0)

heading_m.add_command(label="change headings", command=pop_change_headings)


zeige_frame(frame_start)
zeige_frame(frame_bearbeiten)
password()
root.mainloop()