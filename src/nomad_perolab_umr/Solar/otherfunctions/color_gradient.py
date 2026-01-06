#!/usr/bin/env python

# Lea Obermueller, 06.03.2024


################## LOAD STANDARD PLOT FUNCTIONS ##################

#from Solar.plottemplate.umr_plot_template import color_gradients as color_grad


def generate_gradient(colors, num_colors):
    """
    Generates a smooth gradient between two given hexadecimal colors.

    This function interpolates linearly between the RGB values of the start and end colors
    and returns a list of hex color strings forming a gradient from the first to the second color.

    Parameters
    ----------
    colors : list[str]
        A list containing exactly two hex color codes representing the start and end colors 
        of the gradient. Example: ['#1f82c0', '#021A55'].
    
    num_colors : int
        The number of intermediate colors to generate (including start and end colors).

    Returns
    -------
    list[str]
        A list of `num_colors` color values as hexadecimal strings (e.g., '#1F82C0') forming the gradient.
    """
    
    if len(colors) != 2:
        raise ValueError("Color list must contain exactly two hex color codes.")

    color_start = colors[0]
    color_end = colors[1]

    # Convert the start and end colors from hex to RGB
    start_r = int(color_start[1:3], 16)
    start_g = int(color_start[3:5], 16)
    start_b = int(color_start[5:7], 16)

    end_r = int(color_end[1:3], 16)
    end_g = int(color_end[3:5], 16)
    end_b = int(color_end[5:7], 16)

    # Generate the gradient colors
    gradient_colors = []
    for i in range(num_colors):
        # Calculate the intermediate color
        r = int(start_r + (i * (end_r - start_r) / (num_colors - 1)))
        g = int(start_g + (i * (end_g - start_g) / (num_colors - 1)))
        b = int(start_b + (i * (end_b - start_b) / (num_colors - 1)))

        # Convert the color back to hex format and add it to the list
        gradient_colors.append(f"#{r:02X}{g:02X}{b:02X}")

    return gradient_colors

