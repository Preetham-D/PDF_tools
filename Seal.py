import os
import re
import sys
import logging
from PyPDF2 import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader


# ============================================================
# LOGGING SETUP
# ============================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ============================================================
# PATH HELPERS (EXE SAFE)
# ============================================================

def app_path():
    """
    Returns the folder where this script or EXE is located.
    Works for normal Python and PyInstaller EXE.
    """
    if getattr(sys, 'frozen', False):  # Running as EXE
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_PATH = app_path()

# def resource_path(filename):
#     """
#     Returns absolute path to the resource next to the script/EXE.
#     """
#     return os.path.join(BASE_PATH, filename)

def resource_path(filename):
    """
    Return path to resource for both EXE and .py execution.
    """
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = BASE_PATH

    return os.path.join(base_path, filename)


# ============================================================
# USER SETTINGS
# ============================================================

base_folder = os.path.join(BASE_PATH, "pdfs")     # PDFs folder relative to script
signature_width = 120
signature_height = 120
position_x = 450
position_y = 30
signature_alpha = 0.40

temp_stamp = os.path.join(BASE_PATH, "___temp_signature.pdf")


# ============================================================
# USER SEAL SELECTION
# ============================================================

def choose_seal():
    print("\nSelect the seal you want to apply:")
    print("Enter 1 for Enterprise Seal ")
    print("Enter 2 for Manufacturing Seal ")

    choice = input("\nEnter 1 or 2: ").strip()

    if choice == "1":
        seal_name = "signature_ent.png"
        logger.info("Enterprise seal selected.")
    elif choice == "2":
        seal_name = "signature_man.png"
        logger.info("Manufacturing seal selected.")
    else:
        print("Invalid choice. Defaulting to Enterprise Seal.")
        seal_name = "signature_ent.png"
        logger.warning("Invalid seal selection. Defaulting to Enterprise seal.")

    seal_path = resource_path(seal_name)

    if not os.path.exists(seal_path):
        raise FileNotFoundError(
            f"Seal file not found: {seal_path}\n"
            "Make sure the seal image is in the same folder as the script/EXE."
        )

    return seal_path


signature_file = choose_seal()


# ============================================================
# HELPERS
# ============================================================

def extract_decimal(filename):
    match = re.search(r'\d+(\.\d+)?', filename)
    return float(match.group()) if match else float('inf')


def create_signature_stamp(page_w, page_h, output_stamp):
    logger.debug(f"Creating signature stamp for page size {page_w} x {page_h}")

    c = canvas.Canvas(output_stamp, pagesize=(page_w, page_h))

    try:
        c.setFillAlpha(signature_alpha)
        c.setStrokeAlpha(signature_alpha)
    except Exception:
        logger.warning("Transparency not supported. Continuing without alpha.")

    sig = ImageReader(signature_file)

    c.drawImage(
        sig,
        position_x,
        position_y,
        signature_width,
        signature_height,
        mask='auto'
    )

    c.save()


def sign_pdf_inplace(file_path):
    logger.info(f"Processing PDF: {file_path}")

    temp_output = file_path + ".tmp"

    try:
        reader = PdfReader(file_path)
        writer = PdfWriter()

        total_pages = len(reader.pages)
        logger.info(f"  -> Total pages: {total_pages}")

        for idx, page in enumerate(reader.pages, start=1):
            pw = float(page.mediabox.width)
            ph = float(page.mediabox.height)

            logger.debug(f"  -> Stamping page {idx}/{total_pages}")

            create_signature_stamp(pw, ph, temp_stamp)

            stamp_reader = PdfReader(temp_stamp)
            stamp_page = stamp_reader.pages[0]

            page.merge_page(stamp_page)
            writer.add_page(page)

        # Write result to temp file
        with open(temp_output, "wb") as f:
            writer.write(f)

        # Replace original file
        os.replace(temp_output, file_path)

        logger.info(f"[✓] Signed: {file_path}")

    except Exception as e:
        logger.error(f"[!] Error signing {file_path}: {e}")

        if os.path.exists(temp_output):
            os.remove(temp_output)


def process_folder(root_folder):
    logger.info(f"Scanning folder: {root_folder}")

    total_pdfs = 0

    for folder, subdirs, files in os.walk(root_folder):
        pdfs = [f for f in files if f.lower().endswith(".pdf")]
        pdfs_sorted = sorted(pdfs, key=extract_decimal)

        if pdfs_sorted:
            logger.info(f"Found {len(pdfs_sorted)} PDF(s) in {folder}")

        for filename in pdfs_sorted:
            if filename == temp_stamp or filename.endswith(".tmp"):
                continue

            full_path = os.path.join(folder, filename)
            total_pdfs += 1

            print(f"==> Processing: {full_path}")
            sign_pdf_inplace(full_path)

    if total_pdfs == 0:
        logger.warning("No PDF files found.")
    else:
        logger.info(f"Total PDFs processed: {total_pdfs}")


# ============================================================
# MAIN
# ============================================================

def main():
    logger.info("PDF signing tool started.")
    logger.info(f"Using seal file: {signature_file}")
    logger.info(f"PDF scan folder: {base_folder}")

    try:
        process_folder(base_folder)
    finally:
        if os.path.exists(temp_stamp):
            os.remove(temp_stamp)
            logger.debug("Temporary file cleaned.")

    print("\nAll PDFs have been signed successfully.")
    logger.info("All PDFs signed successfully.")

    input("\nProcessing complete. Press Enter to exit...")


if __name__ == "__main__":
    main()
