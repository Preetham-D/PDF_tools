import tkinter as tk
from tkinter import filedialog, messagebox, Listbox, MULTIPLE, END
from PyPDF2 import PdfReader, PdfWriter


class PDFDeletePagesGUI:
    def __init__(self, master):
        self.master = master
        master.title("PDF Page Deletion Tool")
        master.geometry("450x500")
        master.resizable(False, False)

        self.pdf_path = None

        tk.Button(master, text="Open PDF", width=18, command=self.open_pdf).pack(pady=10)

        self.listbox = Listbox(master, selectmode=MULTIPLE, width=40, height=20)
        self.listbox.pack(pady=10)

        tk.Button(master, text="Delete Selected Pages", width=20, bg="#cc0000", fg="white",
                  command=self.delete_pages).pack(pady=10)

    # ----------------------------------
    # Open PDF and list pages
    # ----------------------------------
    def open_pdf(self):
        self.pdf_path = filedialog.askopenfilename(
            title="Select PDF",
            filetypes=[("PDF Files", "*.pdf")]
        )

        if not self.pdf_path:
            return

        try:
            reader = PdfReader(self.pdf_path)
            num_pages = len(reader.pages)

            self.listbox.delete(0, END)
            for i in range(num_pages):
                self.listbox.insert(END, f"Page {i+1}")

        except Exception as e:
            messagebox.showerror("Error", f"Unable to open PDF:\n{e}")
            self.pdf_path = None

    # ----------------------------------
    # Delete selected pages
    # ----------------------------------
    def delete_pages(self):
        if not self.pdf_path:
            messagebox.showwarning("No PDF", "Please open a PDF first.")
            return

        selected = self.listbox.curselection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select pages to delete.")
            return

        try:
            reader = PdfReader(self.pdf_path)
            writer = PdfWriter()

            pages_to_delete = set(selected)  # zero-based indexes
            total_pages = len(reader.pages)

            for i in range(total_pages):
                if i not in pages_to_delete:
                    writer.add_page(reader.pages[i])

            save_path = filedialog.asksaveasfilename(
                title="Save Updated PDF",
                defaultextension=".pdf",
                filetypes=[("PDF Files", "*.pdf")]
            )

            if not save_path:
                return

            with open(save_path, "wb") as output:
                writer.write(output)

            messagebox.showinfo("Success", f"PDF saved:\n{save_path}")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to modify PDF:\n{e}")


# ----------------------------------
# Run GUI
# ----------------------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFDeletePagesGUI(root)
    root.mainloop()
