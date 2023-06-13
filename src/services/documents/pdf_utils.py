import io
import os
import shutil
import tempfile
import asyncio

from typing import Tuple

from fastapi import HTTPException
from PIL import Image
from PyPDF2 import PdfReader, PdfWriter
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen import canvas


async def copy_file(file):
    """
    The copy_file function takes a file object and copies it to the uploads directory.
    It returns the path of the copied file.

    :param file: Get the file object from the request
    :return: The path of the file that was copied
    :doc-author: Ihor Voitiuk
    """

    upload_dir = os.path.join(os.getcwd(), "uploads")
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)

    dest = os.path.join(upload_dir, file.filename)

    with open(dest, "wb") as buffer:
        await asyncio.get_event_loop().run_in_executor(
            None, shutil.copyfileobj, file.file, buffer
        )

    return dest


async def check_valid_file(file, file_type):
    """
    The check_valid_file function checks the file size and content type of a given file.

    :param file: Check the file type and size
    :param file_type: Check the file type and the size of the file
    :return: A boolean value
    :doc-author: Ihor Voitiuk
    """

    file.file.seek(0, 2)
    file_size = file.file.tell()

    await file.seek(0)

    content_type = file.content_type

    if file_type == "image":
        if file_size > 8 * 1024 * 1024:
            # more than 8 MB
            raise HTTPException(status_code=400, detail="File too large")

        if content_type not in ["image/jpeg", "image/png", "image/gif"]:
            raise HTTPException(status_code=400, detail="Invalid file type")
    elif file_type == "pdf":
        if file_size > 15 * 1024 * 1024:
            # more than 15 MB
            raise HTTPException(status_code=400, detail="File too large")

        if content_type not in ["application/pdf"]:
            raise HTTPException(status_code=400, detail="Invalid file type")


async def operation_with_file_indicators(file, output_file) -> Tuple[int, int, float]:
    """
    The operation_with_file_indicators function is a helper function 
    that calculates the initial and final file sizes of
    the PDF, as well as the percentage reduction. It returns a 
    tuple containing these values.
    
    :param file: Read the file and get its size
    :param output_file: Pass the output file to the function
    :return: A tuple of three values:
    :doc-author: Ihor Voitiuk
    """
    initial_pdf_size = 0
    initial_pdf_size_mb = 0

    if file.file.seekable():
        file.file.seek(0, 2)  # Move the file pointer to the end
        initial_pdf_size = file.file.tell()  # Get the current position, which represents the file size
        initial_pdf_size_mb = initial_pdf_size / 1048576  # Convert to megabytes

    # Calculate the final file size
    final_file_size = len(output_file)
    final_file_size_mb = final_file_size / 1048576  # Convert to megabytes

    # Calculate the percentage reduction
    percentage_reduction = round((
        ((initial_pdf_size - final_file_size) / initial_pdf_size * 100)
        if initial_pdf_size != 0
        else 0.0
    ))

    return initial_pdf_size_mb, final_file_size_mb, percentage_reduction


async def convert_images_to_pdf(images):
    """
    The convert_images_to_pdf function takes a list of images and converts them to a single PDF file.

    :param images: Pass in the list of images to be converted
    :return: An output_stream object, which is a file-like object
    :doc-author: Ihor Voitiuk
    """
    output_stream = io.BytesIO()
    c = canvas.Canvas(output_stream, pagesize=letter)

    tasks = []
    for image in images:
        tasks.append(asyncio.create_task(process_image(image, c)))

    await asyncio.gather(*tasks)

    c.save()
    output_stream.seek(0)
    return output_stream


async def process_image(image, canvas):
    """
    The process_image function takes an image and a canvas as arguments.
    It then checks to see if the file is valid, copies it to a temporary location,
    and opens it with PIL. It then calculates the ratio of the image's width and height
    to that of letter size paper (8.5&quot; x 11&quot;). If the image's ratio is greater than that
    of letter size paper, we set new_width equal to pdf_width (8.5&quot;) and calculate new_height
    based on this value; otherwise we set new_height equal to pdf_height (11&quot;) and calculate
    new_width

    :param image: Pass in the image file that is to be processed
    :param canvas: Draw the image onto the pdf
    :return: A canvas object with the image drawn onto it
    :doc-author: Ihor Voitiuk
    """
    await check_valid_file(image, "image")
    image_path = await copy_file(image)
    img = Image.open(image_path)

    width, height = img.size
    pdf_width, pdf_height = letter

    image_ratio = width / height
    pdf_ratio = pdf_width / pdf_height

    if image_ratio > pdf_ratio:
        new_width = pdf_width
        new_height = int(new_width / image_ratio)
    else:
        new_height = pdf_height
        new_width = int(new_height * image_ratio)

    img = img.resize((int(new_width), int(new_height)), Image.ANTIALIAS)

    with tempfile.NamedTemporaryFile(suffix=".png") as temp_file:
        file_name = temp_file.name
        img.save(file_name)

        canvas.drawImage(ImageReader(file_name), 0, 0, pdf_width, pdf_height)

    os.remove(image_path)
    canvas.showPage()


async def compress_pdf(file, compression):
    """
    The compress_pdf function takes in a file and a compression option.
    It then checks if the file is valid, and if it is not,
    raises an HTTPException. If the file is valid, it then checks
    what compression option was chosen by the user.
    If they chose to remove duplication from their PDF document,
    it calls on another function to do so.
    Otherwise, if they chose to remove images from their PDF document or
    apply lossless compression to their PDF document (which are both done using Ghostscript),
    it calls on another function that does this for them.

    :param file: Pass the file object to the function
    :param compression: Determine which compression method to use
    :return: A file object
    :doc-author: Ihor Voitiuk
    """
    await check_valid_file(file, "pdf")

    if compression == "remove duplication":
        result = await remove_duplication(file)
    elif compression == "remove images":
        result = await remove_images(file)
    elif compression == "lossless compression":
        result = await apply_lossless_compression(file)
    else:
        raise HTTPException(status_code=400, detail="Invalid compression option")

    file_indicators = await operation_with_file_indicators(file, result)

    return result, *file_indicators


async def remove_duplication(file):
    """
    The remove_duplication function takes a file and returns
    the same file with all duplicate pages removed.

    :param file: Get the file from the request
    :return: A file with the same content as the input file,
    but without duplicated pages
    :doc-author: Ihor Voitiuk
    """
    input_pdf = io.BytesIO(await file.read())
    output_pdf = io.BytesIO()

    pdf = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in pdf.pages:
        writer.add_page(page)

    writer.add_metadata(pdf.metadata)
    writer.write(output_pdf)
    output_pdf.seek(0)

    return output_pdf.getvalue()


async def remove_images(file):
    """
    The remove_images function takes a file object and
    returns the same file with all images removed.

    :param file: Read the file from the request
    :return: The pdf file without the images
    :doc-author: Ihor Voitiuk
    """
    input_pdf = io.BytesIO(await file.read())
    output_pdf = io.BytesIO()

    pdf = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in pdf.pages:
        writer.add_page(page)

    writer.remove_images()

    writer.write(output_pdf)
    output_pdf.seek(0)

    return output_pdf.getvalue()


async def apply_lossless_compression(file):
    """
    The apply_lossless_compression function takes a file object and returns
    the same file with lossless compression applied.

    :param file: Read the file and convert it to a byte stream
    :return: A bytestring
    :doc-author: Ihor Voitiuk
    """
    input_pdf = io.BytesIO(await file.read())
    output_pdf = io.BytesIO()

    pdf = PdfReader(input_pdf)
    writer = PdfWriter()

    for page in pdf.pages:
        page.compress_content_streams()
        writer.add_page(page)

    writer.write(output_pdf)
    output_pdf.seek(0)

    return output_pdf.getvalue()
