import os

runs = 0

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

path1 = os.path.join(__location__, "resources\\formated_books.txt")  #output
path2 = os.path.join(__location__, "resources\\books_to_formate.txt")#books to formate




with open(path1, "w", encoding="utf-8")as f1:
    with open(path2, "r", encoding="utf-8") as f2:
        for line in f2:

            l = line.split("\t")

            for strings in l:
                runs += 1
                if runs == 1:
                    f1.write(strings + " | ")
                
                elif runs == 2:
                    f1.write(strings + " | ")

                elif runs == 3:
                    f1.write(strings + " | ")

                elif runs == 4:
                    f1.write(strings + " | ")

                elif runs == 5:
                    pass

                elif runs == 6:
                    f1.write("nein" + " | ")

                elif runs == 7:
                    f1.write("/" + " | ")

                elif runs == 8:
                    f1.write(strings)
                    runs = 0

                print(f"{runs} {strings}")