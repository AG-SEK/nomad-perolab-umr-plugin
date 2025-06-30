# In this Script we collect functions which are used to create matrices out of several plots.


from PIL import Image
import math

def make_plot_matrix(list_of_image_paths, filename, n_col=None, n_row=None, image_size=None, background='transparent'):
    """
    Creates an image matrix from a list of image paths and saves the resulting image.

    This function takes a list of image paths and arranges the images into a matrix.
    The size of the matrix (number of rows and columns) can be optionally specified.
    If not specified, a square matrix will be created. The resulting image matrix
    is saved to the specified file and returned.

    Parameters:
        - list_of_image_paths (list): List of paths to the images.
        - filename (str): The name of the file where the resulting image matrix will be saved.
        - n_col (int, optional): Number of columns in the matrix. If not specified, will be determined automatically.
        - n_row (int, optional): Number of rows in the matrix. If not specified, will be determined automatically.
        - image_size (list, optional): Size of each image in the matrix [width, height]. Default is None (auto-determine based on images).
        - background (str, optional): Background color of the matrix. Can be 'white' or 'transparent'. Default is 'transparent'.

    Returns:
        Image: The resulting image matrix.
    """
    
    # Determine n_col and n_row automatically if not given
    if not n_col and not n_row:
        pixel = math.ceil(math.sqrt(len(list_of_image_paths))) # Take square root of number of elements and round (Quadratic matrix)
        n_col = pixel
        n_row = pixel

    # Determine image_size automatically if not given
    if not image_size:
        # Load the first image to get its size
        first_image = Image.open(list_of_image_paths[0])
        image_size = first_image.size

    # Create new transparent or white picture for matrix in correct dimensions
    if background == 'transparent':
        matrix_image = Image.new('RGBA', (n_col * image_size[0], n_row * image_size[1]), color=(255, 255, 255, 0))
    elif background == 'white':
        matrix_image = Image.new('RGB', (n_col * image_size[0], n_row * image_size[1]), color=(255, 255, 255))

    # Add pictures to matrix
    for i, image_path in enumerate(list_of_image_paths):
        # Calculate Position of image
        row = i // n_col
        col = i % n_col
        # Add plot to matrix_image
        img = Image.open(image_path)
        img = img.resize(image_size, Image.LANCZOS)
        matrix_image.paste(img, (col * image_size[0], row * image_size[1]))

    # Save the matrix image
    matrix_image.save(filename)

    return matrix_image
