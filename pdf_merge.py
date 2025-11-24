import os
import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, SINGLE, END
from PyPDF2 import PdfMerger


class PDFMergerGUI:
    def __init__(self, master):
        self.master = master
        master.title("PDF Merge Tool")
        master.geometry("500x450")
        master.resizable(False, False)

        self.pdf_list = []

        # Listbox
        self.listbox = Listbox(master, selectmode=SINGLE, width=60, height=15)
        self.listbox.pack(pady=10)

        # Buttons frame
        btn_frame = tk.Frame(master)
        btn_frame.pack()

        tk.Button(btn_frame, text="Add PDFs", width=12, command=self.add_pdfs).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Remove", width=12, command=self.remove_selected).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Move Up", width=12, command=self.move_up).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(btn_frame, text="Move Down", width=12, command=self.move_down).grid(row=1, column=1, padx=5)

        # Merge button
        tk.Button(master, text="Merge PDFs", width=20, command=self.merge_pdfs, bg="#0078D7", fg="white").pack(pady=15)

    # -----------------------------
    # BUTTON FUNCTIONS
    # -----------------------------

    def add_pdfs(self):
        files = filedialog.askopenfilenames(title="Select PDF Files", filetypes=[("PDF Files", "*.pdf")])
        for f in files:
            self.pdf_list.append(f)
            self.listbox.insert(END, os.path.basename(f))

    def remove_selected(self):
        sel = self.listbox.curselection()
        if not sel:
            return
        index = sel[0]
        self.listbox.delete(index)
        del self.pdf_list[index]

    def move_up(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == 0:
            return
        index = sel[0]
        self.swap(index, index - 1)

    def move_down(self):
        sel = self.listbox.curselection()
        if not sel or sel[0] == len(self.pdf_list) - 1:
            return
        index = sel[0]
        self.swap(index, index + 1)

    def swap(self, i, j):
        self.pdf_list[i], self.pdf_list[j] = self.pdf_list[j], self.pdf_list[i]

        # Update listbox display
        items = list(self.listbox.get(0, END))
        items[i], items[j] = items[j], items[i]

        self.listbox.delete(0, END)
        for item in items:
            self.listbox.insert(END, item)

        self.listbox.select_set(j)

    def merge_pdfs(self):
        if not self.pdf_list:
            messagebox.showerror("Error", "No PDF files selected.")
            return

        save_path = filedialog.asksaveasfilename(
            title="Save Merged PDF As",
            defaultextension=".pdf",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if not save_path:
            return

        try:
            merger = PdfMerger()
            for pdf in self.pdf_list:
                merger.append(pdf)
            merger.write(save_path)
            merger.close()

            messagebox.showinfo("Success", f"Merged PDF created:\n{save_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to merge PDFs:\n{str(e)}")


# -----------------------------
# RUN APP
# -----------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFMergerGUI(root)
    root.mainloop()
