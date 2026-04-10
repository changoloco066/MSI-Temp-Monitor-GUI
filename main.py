from temp_reader import TempReader
from ui import App

if __name__ == "__main__":
    reader = TempReader()
    try:
        app = App(reader)
        app.mainloop()
    finally:
        reader.close()