import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import fitz  # PyMuPDF
import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin

class ImageProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Image Processor Application")
        self.create_widgets()

    def create_widgets(self):
        # PDF Image Extraction
        pdf_frame = tk.LabelFrame(self.root, text="PDF Image Extraction")
        pdf_frame.pack(padx=10, pady=5, fill="x")
        
        pdf_btn = tk.Button(pdf_frame, text="Upload PDF", command=self.extract_images_from_pdf)
        pdf_btn.pack(pady=5)

        # Image Converter
        converter_frame = tk.LabelFrame(self.root, text="Image Converter")
        converter_frame.pack(padx=10, pady=5, fill="x")

        convert_btn = tk.Button(converter_frame, text="Convert Images to JPG", command=self.convert_images_to_jpg)
        convert_btn.pack(pady=5)

        # Image Scraper
        scraper_frame = tk.LabelFrame(self.root, text="Image Scraper")
        scraper_frame.pack(padx=10, pady=5, fill="x")

        self.url_entry = tk.Entry(scraper_frame, width=40)
        self.url_entry.pack(side="left", padx=5, pady=5)
        
        scrape_btn = tk.Button(scraper_frame, text="Scrape Images", command=self.scrape_images_from_website)
        scrape_btn.pack(side="left", padx=5, pady=5)

        # Image Resizer
        resizer_frame = tk.LabelFrame(self.root, text="Image Resizer")
        resizer_frame.pack(padx=10, pady=5, fill="x")

        resize_btn = tk.Button(resizer_frame, text="Resize Images to 1024x768", command=self.resize_images)
        resize_btn.pack(pady=5)

    def extract_images_from_pdf(self):
        pdf_path = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF files", "*.pdf")])
        if not pdf_path:
            return

        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        output_folder = os.path.join(os.path.dirname(pdf_path), pdf_name)
        os.makedirs(output_folder, exist_ok=True)

        with fitz.open(pdf_path) as pdf:
            for i, page in enumerate(pdf):
                images = page.get_images(full=True)
                for img_index, img in enumerate(images):
                    xref = img[0]
                    base_image = pdf.extract_image(xref)
                    img_data = base_image["image"]

                    img_path = os.path.join(output_folder, f"{pdf_name}_page_{i + 1}_img_{img_index + 1}.jpg")
                    with open(img_path, "wb") as img_file:
                        img_file.write(img_data)

        messagebox.showinfo("PDF Image Extraction", f"Images extracted to {output_folder}")

    def convert_images_to_jpg(self):
        image_paths = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image files", "*.png;*.jpeg;*.bmp;*.tiff;*.gif;*.webp")])
        if not image_paths:
            return

        output_folder = os.path.join(os.path.dirname(image_paths[0]), "converted")
        os.makedirs(output_folder, exist_ok=True)

        for img_path in image_paths:
            img_name = os.path.splitext(os.path.basename(img_path))[0]
            try:
                with Image.open(img_path) as img:
                    rgb_img = img.convert("RGB")
                    output_path = os.path.join(output_folder, f"{img_name}.jpg")
                    rgb_img.save(output_path, "JPEG")
            except Exception as e:
                messagebox.showerror("Image Conversion Error", f"Could not convert {img_path}\n{e}")
                continue

        messagebox.showinfo("Image Converter", f"Images converted to JPG in {output_folder}")

    def scrape_images_from_website(self):
        url = self.url_entry.get()
        if not url:
            messagebox.showerror("Image Scraper", "Please enter a website URL.")
            return

        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = os.path.join(os.getcwd(), f"scraped_{date_str}")
        os.makedirs(output_folder, exist_ok=True)

        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            img_tags = soup.find_all("img")

            for i, img_tag in enumerate(img_tags, start=1):
                img_url = img_tag.get("src")
                img_url = urljoin(url, img_url)

                try:
                    img_data = requests.get(img_url).content
                    img_path = os.path.join(output_folder, f"image_{i}.jpg")
                    with open(img_path, "wb") as img_file:
                        img_file.write(img_data)
                except Exception as e:
                    print(f"Error downloading {img_url}: {e}")
                    continue

            messagebox.showinfo("Image Scraper", f"Images scraped to {output_folder}")

        except requests.RequestException as e:
            messagebox.showerror("Image Scraper Error", f"Could not scrape images from {url}\n{e}")

    def resize_images(self):
        image_paths = filedialog.askopenfilenames(title="Select Images", filetypes=[("Image files", "*.png;*.jpeg;*.jpg;*.bmp;*.tiff;*.gif;*.webp")])
        if not image_paths:
            return

        date_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_folder = os.path.join(os.path.dirname(image_paths[0]), f"resize_{date_str}")
        os.makedirs(output_folder, exist_ok=True)

        target_size = (1024, 768)
        
        for img_path in image_paths:
            img_name = os.path.splitext(os.path.basename(img_path))[0]
            try:
                with Image.open(img_path) as img:
                    img_ratio = img.width / img.height
                    target_ratio = target_size[0] / target_size[1]

                    if img_ratio > target_ratio:
                        # Crop width
                        new_height = target_size[1]
                        new_width = int(target_size[1] * img_ratio)
                        img = img.resize((new_width, new_height), Image.LANCZOS)
                        left = (new_width - target_size[0]) / 2
                        img = img.crop((left, 0, left + target_size[0], target_size[1]))
                    else:
                        # Crop height
                        new_width = target_size[0]
                        new_height = int(target_size[0] / img_ratio)
                        img = img.resize((new_width, new_height), Image.LANCZOS)
                        top = (new_height - target_size[1]) / 2
                        img = img.crop((0, top, target_size[0], top + target_size[1]))

                    output_path = os.path.join(output_folder, f"{img_name}_resized.jpg")
                    img.save(output_path, "JPEG")
            except Exception as e:
                messagebox.showerror("Image Resizer Error", f"Could not resize {img_path}\n{e}")
                continue

        messagebox.showinfo("Image Resizer", f"Images resized to 1024x768 and saved in {output_folder}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ImageProcessorApp(root)
    root.mainloop()
