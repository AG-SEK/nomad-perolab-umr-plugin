import plotly.io as pio
import plotly.graph_objects as go
import pandas as pd
import h5py
import numpy as np
import scipy.constants as const
from scipy.interpolate import interp1d
from scipy.stats import linregress
from scipy.optimize import curve_fit
from scipy.ndimage import gaussian_filter



# normalize a cube if this is not already done
def normalize_cube_images(normalization_file_path, cube_file_path):
    with h5py.File(normalization_file_path, 'r') as normalization_file, \
         h5py.File(cube_file_path, 'r') as cube_file:
        
        # Extract images and wavelengths from the cube
        images = cube_file['Cube']['Images'][:]
        wavelengths = cube_file['Cube']['Wavelength'][:]
        
        # Extract normalization data from the normalization file
        normalization_data = normalization_file['Graph']['0']['Data'][:, 1]  # Assuming second column has normalization values
        normalization_wavelengths = normalization_file['Graph']['0']['Data'][:, 0]
        
        # Normalize each image by its corresponding wavelength's normalization value
        normalized_images = images.copy()
        for i, wavelength in enumerate(wavelengths):
            # Find the closest wavelength in normalization data and use it for normalization
            closest_idx = np.abs(normalization_wavelengths - wavelength).argmin()
            normalization_value = normalization_data[closest_idx]
            normalized_images[i] /= normalization_value

    return wavelengths, normalized_images

def save_normalized_cube_with_processing(output_file_path, original_cube_file_path, wavelengths, normalized_images, normalization_file_path):
    with h5py.File(original_cube_file_path, 'r') as original_cube_file, \
         h5py.File(output_file_path, 'w') as new_cube_file:
        
        # Copy structure and metadata from the original HDF5 file
        def copy_structure_with_metadata(original_group, new_group):
            for key, item in original_group.items():
                if isinstance(item, h5py.Group):
                    # Recursively create sub-groups
                    new_subgroup = new_group.create_group(key)
                    copy_structure_with_metadata(item, new_subgroup)
                elif isinstance(item, h5py.Dataset):
                    # Copy datasets along with their data and attributes
                    new_dataset = new_group.create_dataset(key, data=item[()], dtype=item.dtype)
                    for attr_key, attr_value in item.attrs.items():
                        new_dataset.attrs[attr_key] = attr_value  # Copy dataset attributes

            # Copy group-level attributes
            for attr_key, attr_value in original_group.attrs.items():
                new_group.attrs[attr_key] = attr_value

        # Copy the full structure from the original file
        copy_structure_with_metadata(original_cube_file, new_cube_file)
        
        # Replace the Images dataset with the normalized images
        del new_cube_file['Cube']['Images']  # Remove the original Images dataset
        new_cube_file['Cube'].create_dataset('Images', data=normalized_images, dtype=normalized_images.dtype)
        
        # Replace the Wavelengths dataset with the updated wavelengths
        del new_cube_file['Cube']['Wavelength']  # Remove the original Wavelengths dataset
        new_cube_file['Cube'].create_dataset('Wavelength', data=wavelengths, dtype=wavelengths.dtype)
        
        # Modify the Processings group
        processings_group = new_cube_file['Cube']['Info']['Processings']
        normalization_index = str(len(processings_group.keys())).zfill(3)  # Add a new group with an incremented index
        new_processing_group = processings_group.create_group(normalization_index)
        new_processing_group.attrs['Name'] = 'Normalization'
        new_processing_group.attrs['Method'] = 'Devide'
        new_processing_group.attrs['Source Data'] = original_cube_file_path.split('/')[-1]
        new_processing_group.attrs['Spectrum'] = normalization_file_path.split('/')[-1]

    return 0



def get_hypPL_spectrum(file_path):
    df = pd.DataFrame()
    with h5py.File(file_path, 'r') as file:
        df['wavelength'] = file['Cube']['Wavelength'][:]
        df['energy'] = const.h*const.c/(df['wavelength']*1e-9) # in J
        exposure_times= file['Cube']['TimeExposure'][:]
        df['intensity'] = np.nanmean(file['Cube']['Images'][:], axis=(1,2))/exposure_times*1.36
    return df



# Replace NaNs with the mean of each 2D slice along the first axis
def fill_nan_with_slice_mean(data):
    filled_data = data.copy()  # Avoid modifying the original data
    for i in range(filled_data.shape[0]):  # Iterate over slices
        slice_mean = np.nanmean(filled_data[i])  # Compute mean ignoring NaNs
        nan_mask = np.isnan(filled_data[i])  # Find NaNs in the slice
        filled_data[i][nan_mask] = slice_mean  # Replace NaNs with the slice mean
    return filled_data



def get_hypPL_cube(file_path, sigma=(0,0,0)):
    data = {}
    with h5py.File(file_path, 'r') as file:
        data['wavelength'] = file['Cube']['Wavelength'][:] # in nm
        data['energy'] = const.h*const.c/(data['wavelength']*1e-9) # in J
        exposure_time= file['Cube']['TimeExposure'][0] # assume all images are recorded with same exposure time
        intensity = file['Cube']['Images'][:]
        cleaned_intensity = fill_nan_with_slice_mean(intensity) # fill nan values with proper value
        cleaned_intensity[cleaned_intensity < 0] = 1e11 # fill values below zero with positive value
        data['intensity'] = gaussian_filter(cleaned_intensity, sigma)/exposure_time*1.36
    return data




def get_hypPL_map(file_path, sigma=(0,0)):
    data = {}
    with h5py.File(file_path, 'r') as file:
        #exposure_time= file['Cube']['TimeExposure'][0] # assume all images are recorded with same exposure time
        #data['intensity'] = gaussian_filter(file['Cube']['Images'][:], sigma)/exposure_time*1.36
        data['intensity'] = file['Cube']['Images'][:]
    return data




def get_hypPL_video_spectrum(file_path):
    df = pd.DataFrame()
    with h5py.File(file_path, 'r') as file:
        byte_timestamps = file['Cube']['Timestamp'][:]
        decoded_timestamps = [bt.decode('utf-8') for bt in byte_timestamps]
        df['timestamps'] = pd.to_datetime(decoded_timestamps)
        df['time [s]']  = (df['timestamps'] - df['timestamps'].min()).dt.total_seconds()
        exposure_times = file['Cube']['TimeExposure'][:] 
        df['intensity'] = np.nanmean(file['Cube']['Images'][:], axis=(1,2))/exposure_times
    return df

def get_hypPL_video_cubes(file_path):
    df = pd.DataFrame()
    with h5py.File(file_path, 'r') as file:
        byte_timestamps = file['Cube']['Timestamp'][:]
        decoded_timestamps = [bt.decode('utf-8') for bt in byte_timestamps]
        df['timestamps'] = pd.to_datetime(decoded_timestamps)
        df['time [s]']  = (df['timestamps'] - df['timestamps'].min()).dt.total_seconds()
        exposure_time = file['Cube']['TimeExposure'][:][0]
        df['intensity'] = file['Cube']['Images'][:]/exposure_time
    return df




def get_ESP32_data(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    # Prepare lists to hold the parsed data
    cell_voltage = []
    cell_current = []
    resistor_voltage = []
    constant_voltage = []
    sweep_voltage = []
    time = []

    # Iterate over each line in the file and extract the data
    for line in lines:
        measurements = line.split('\t')
        
        # Extracting and cleaning each measurement
        for measurement in measurements:
            if 'CellVoltage V:' in measurement:
                cell_voltage.append(float(measurement.split(': ')[1]))
            elif 'CellCurrent mA:' in measurement:
                cell_current.append(float(measurement.split(': ')[1]))
            elif 'Resistor_Voltage:' in measurement:
                resistor_voltage.append(float(measurement.split(': ')[1]))
            elif 'Constant_Voltage:' in measurement:
                constant_voltage.append(float(measurement.split(': ')[1]))
            elif 'Sweep_Voltage:' in measurement:
                sweep_voltage.append(float(measurement.split(': ')[1]))
            elif 'Time:' in measurement:
                time.append(measurement.split('Time: ')[1].strip())

    # Create a DataFrame from the parsed data
    data = {
        'CellVoltage V': cell_voltage,
        'CellCurrent mA': cell_current,
        'Resistor_Voltage': resistor_voltage,
        'Constant_Voltage': constant_voltage,
        'Sweep_Voltage': sweep_voltage,
        'Timestamp': time
    }
    df = pd.DataFrame(data)
    df['Timestamp'] = pd.to_datetime(df['Timestamp'])
    df['time [s]'] = (df['Timestamp'] - df['Timestamp'].min()).dt.total_seconds()

    return df





def plot_1curve(data, keys=['wavelength', 'intensity', 'PL intensity', 'PL intensity [photons/(s*nm*m²)]'], x_title='Wavelength [nm]', fig=None):
    if not fig:
      fig = go.Figure()
    
    x = data[keys[0]]
    y = data[keys[1]]

    fig.add_scatter(
        x=x,  # x-values
        y=y,  # y-values
        name=keys[2],
        #marker=dict(size=4),
        )

    fig.update_layout(
        #legend_font_size=24,
        #legend_x= 0.05,
        #legend_xanchor ='left',
        xaxis_title=x_title,
        yaxis=dict(
           title_text=keys[3],
           # automargin = True
           )
        )
    return fig





def plot_2curves(data1, keys1, data2, keys2, x_title, line_mode='markers', fig=None):
    '''keys is list with key_x, key_y, name, y_title'''
    if not fig:
      fig = go.Figure()

    line_color = pio.templates['UMR'].layout.colorway
    fig.add_scatter(
            x=data1[keys1[0]],  # x-values
            y=data1[keys1[1]],  # y-values
            name=keys1[2],
            #marker=dict(size=4, color=line_color[0]),
            marker=dict(color=line_color[0]),
            mode=line_mode
    )
    fig.add_scatter(
            x=data2[keys2[0]],  # x-values
            y=data2[keys2[1]], # y-values
            name=keys2[2],
            #marker=dict(size=4, color=line_color[1]),
            marker=dict(color=line_color[1]),
            yaxis='y2',
            mode=line_mode
    )
    
    fig.update_layout(
       #legend_font_size=20,
       #legend_y=1, 
       #legend_x=0.0,
       #legend_xanchor='left',
       legend_visible=True,
       xaxis_title=x_title,
       yaxis=dict(
          title=keys1[3],
          color=line_color[0],
          mirror=False,
          zeroline=False,
          ),
       yaxis2=dict(
          color=line_color[1],
          title=keys2[3],
          overlaying='y',
          side='right',
          mirror=False,
          zeroline=False
          )
    )
    #fig.update_layout(width=1200, height=700)
    return fig  



def gaussian(x, a, b, c):
   return a * np.exp(-((x - b)**2) / (2 * c**2))

def plot_gaussian(data, name, return_peak_wl=None, fig=None):
   if not fig:
      fig = go.Figure()
   
   fig = plot_1curve(data, keys=['wavelength', 'intensity', name, 'PL intensity [photons/(s*nm*m²)]'], fig=fig)

   # Fit the Gaussian model
   x = data['wavelength']
   y = data['intensity']
   peak_guess = np.argmax(y)
   w = int(len(data['wavelength'])/10)
   x = x[peak_guess-w:peak_guess+w].reset_index(drop=True)
   y = y[peak_guess-w:peak_guess+w].reset_index(drop=True)
   
   popt, _ = curve_fit(gaussian, x, y, p0=[y.max(), x[np.argmax(y)], 20])
   peak_position = popt[1]
   
   #fig.add_trace(go.Scatter(x=x, y=gaussian(x, *popt), mode='lines', name='Gaussian Fit'))
   #fig.add_vline(x=peak_position, line_dash='dash')
   fig.add_shape(
    type="line",
    x0=peak_position, x1=peak_position,  # x-coordinate for the vertical line
    y0=0, y1=popt[0],  # y-coordinate range
    line=dict(color="black", width=3, dash="dash"),  # Line style
)
   if return_peak_wl:
       return fig, peak_position
   else:
       return fig




# Custom colorscale for the heatmap
custom_colorscale = [
    [0, "black"],      # start with black
    [0.35, "red"],     # transition to red
    [0.6, "orange"],   # then to orange
    [0.8, "yellow"],   # more emphasis on yellow
    [1, "white"]       # end with white
]

def plot_h5_heatmap(data, tickformat='.0f', digits=4, percentile_low=0.5, percentile_high=99.5, zmin=False, zmax=False, Temp=False):
    # Flatten the data for percentile calculation
    data_flat = data.flatten()
    mean_val = np.nanmean(data_flat)  

    # Calculate the 5th and 95th percentiles of the data
    if not zmin:
        zmin = np.nanpercentile(data_flat, percentile_low)
    if not zmax:
        zmax = np.nanpercentile(data_flat, percentile_high)
    

    # Heatmap colorbar configuration
    colorbar_config = dict(
        x=0.78, y=0.5, len=0.9, thickness=40,
        tickformat=tickformat, tickvals=[zmin, mean_val, zmax],
        ticks='inside', ticklen=10, tickwidth=5, tickcolor='white',
        outlinecolor='white', outlinewidth=3,
        tickfont=dict(color='white', size=48)
    )

    # Calculate the width of the colorbar background based on the number of digits
    colorbar_bg_width = 0.16 + 0.013 * (digits - 2)

    # get correct labelling when numbers too long
    if 'e' in tickformat:
        mantissa, exponent = f"{mean_val:{tickformat}}".split('e')
        mantissa = float(mantissa)
        exponent = int(exponent)
        colorbar_config.update({
            'title_text': f"10<sup>{exponent}</sup>",
            'title_font': dict(color='white', size=48),
            'ticktext': [f"{val/10**exponent:{tickformat.split('e')[0]}f}" for val in [zmin, mean_val, zmax]]
        })
        
    # Initialize the heatmap figure
    fig = go.Figure(data=go.Heatmap(
        z=data, zmin=zmin, zmax=zmax, colorbar=colorbar_config, colorscale=custom_colorscale
    ))

    # Scale bar settings
    scale_length_micrometers = 200  # Length of the scale bar in micrometers
    microns_per_pixel = 16.4 / 21.22  # Conversion factor from micrometers to pixel units
    pixel_length = scale_length_micrometers * microns_per_pixel  # Pixel length of the scale bar
    scale_bar_position_x = 60  # X position where the scale bar starts
    scale_bar_position_y = 60  # Y position where the scale bar is located
    scale_bar_height = 5  # Height of the scale bar

    # Settings for additional dynamic annotation
    annotation_position_x = 350  # X position for the new annotation
    annotation_position_y = 75  # Y position for the new annotation

    # Define shapes for scale bar and additional backgrounds
    shapes = [
        # Extended colorbar background
        dict(type="rect", xref="paper", yref="paper", x0=0.78, y0=0.025, x1=0.78 + colorbar_bg_width, y1=0.975,
             line=dict(color='rgba(0,0,0,0.3)'), fillcolor='rgba(0,0,0,0.5)'),
        # Black background for the scale bar
        dict(type="rect", x0=scale_bar_position_x - 30, y0=scale_bar_position_y - 20,
             x1=scale_bar_position_x + pixel_length + 30, y1=scale_bar_position_y + 70,
             line=dict(color="rgba(0,0,0,0.3)"), fillcolor="rgba(0,0,0,0.5)"),
        # White scale bar
        dict(type="rect", x0=scale_bar_position_x, y0=scale_bar_position_y - scale_bar_height / 2,
             x1=scale_bar_position_x + pixel_length, y1=scale_bar_position_y + scale_bar_height / 2,
             line=dict(color="White", width=2), fillcolor="White"),
        # Ticks on the scale bar
        dict(type="line", x0=scale_bar_position_x, y0=scale_bar_position_y - scale_bar_height / 2,
             x1=scale_bar_position_x, y1=scale_bar_position_y + 20, line=dict(color="White", width=5)),
        dict(type="line", x0=scale_bar_position_x + pixel_length, y0=scale_bar_position_y - scale_bar_height / 2,
             x1=scale_bar_position_x + pixel_length, y1=scale_bar_position_y + 20, line=dict(color="White", width=5)),
    ]

    # Define annotations, including placeholders for dynamic updates
    annotations = [
        # Scale bar annotation
        dict(x=scale_bar_position_x + pixel_length / 2, y=scale_bar_position_y + 45,
             text="200 μm", showarrow=False, font=dict(color="White", size=50)),
    ]

    if Temp:
        # Background for the new dynamic annotation
        shapes.append(
            dict(type="rect", x0=annotation_position_x - 10, y0=annotation_position_y - 35,
                x1=annotation_position_x + 350, y1=annotation_position_y + 35,
                line=dict(color="rgba(0,0,0,0.3)"), fillcolor="rgba(0,0,0,0.3)"))
        # Placeholder for dynamic time and temperature data
        annotations.append(
            dict(x=annotation_position_x, y=annotation_position_y,
                text="t={}s, T={}K".format("0", "0"),
                showarrow=False, font=dict(color="White", size=50),
                xanchor="left")
        )

    # Update layout with shapes and annotations
    fig.update_layout(shapes=shapes, annotations=annotations,
                      xaxis=dict(tickmode='array', tickvals=[]),
                      yaxis=dict(tickmode='array', tickvals=[]),
                      autosize=False, width=1024, height=1024,
                      margin=dict(l=2, r=2, b=2, t=2))

    return fig





# in this function the temperature is calculated from -1/slope, QFLS is intercept*T
def get_QFLSy_value(I_PL, E, A=1):
    nm_to_J=const.h*const.c/E**2 * 1e9 # this is used to transform photon flux /s*m²*nm into photon flux /s*m²*J
    return const.k*(np.log(nm_to_J*I_PL) + np.log(4*np.pi**2*const.hbar**3*const.c**2/(A*E**2)))/const.e




def get_QFLS(intensity, energy, A_data = 1, A_type='fix', fit_range=(4,16), fig=None):
    # for A either take just fix A=1 or IPCE (if complete cell) or UV-Vis (if transmission accessible)
    if A_type == 'fix' or A_type =='HypPL':
        absorptance = A_data
    if A_type == 'eqe':
        # Interpolate EQE to match the energy axis of the 3D dataset
        abs_x=const.h*const.c/(A_data['wavelength']*1e-9)
        abs_y=A_data['eqe']
        interp_func = interp1d(abs_x, abs_y, kind='linear', fill_value="extrapolate")
        absorptance = interp_func(energy)        

    QFLSy_values = get_QFLSy_value(intensity, energy, A=absorptance)

    x = energy/const.e
    y = QFLSy_values

    # Perform linear regression
    x1=x[fit_range[0]:fit_range[1]]
    y1=y[fit_range[0]:fit_range[1]]
    slope, intercept, r_value, p_value, std_err = linregress(x1, y1)
    T= -1/slope
    QFLS = intercept*T

    #print(f"slope: {slope}, Intercept: {intercept}, Temp T [K]: {T}, QFLS: {QFLS}")
    #print(f"R-squared: {r_value**2}")

    fig = plot_1curve({'x':x, 'y':y}, ['x', 'y', 'PL data', r'k*ln(PL*4𝜋²ħ³𝑐²/𝐴*𝐸²) [eV/K]'], 'Energy [eV]', fig=fig)
    #fig.add_scatter(x=x1, y=slope*x1+intercept, name=f'T = {T:.0f}, QFLS = {QFLS:.3f}', mode='lines')
    fig.add_scatter(x=x1, y=slope*x1+intercept, name=f'fit T = {T:.0f} K, QFLS = {QFLS:.3f} eV', mode='lines',  line=dict(width=8))
        
    return fig, T, QFLS




def get_QFLS_map(intensity, energy, A_data=1, A_type='fix', fit_range=(4,26), sigma=(0, 0, 0), fig=None):
    # for A either take just fix A=1 or IPCE (if complete cell) or UV-Vis (if transmission accessible)
    if A_type == 'fix':
        absorptance = A_data
    if A_type == 'eqe':
        # Interpolate EQE to match the energy axis of the 3D dataset
        abs_x=const.h*const.c/(A_data['wavelength']*1e-9)
        abs_y=A_data['eqe']
        interp_func = interp1d(abs_x, abs_y, kind='linear', fill_value="extrapolate")
        absorptance = interp_func(energy)[:, np.newaxis, np.newaxis]
    if A_type == 'HypPL':
        if len(A_data['intensity']) == len(energy):
            absorptance = A_data['intensity']
        # in best case HypPL absorptance data is available with the same energy axis
        if len(A_data['intensity']) != len(energy):
            print('HypPL has not same size as PL_cube')
            #following would be correct but is too slow, 
            '''
            # Interpolate HypPL to match the energy axis of the 3D dataset
            abs_x=const.h*const.c/(A_data['wavelength']*1e-9)
            abs_y=A_data['intensity']
            # Interpolate Each Slice Along the energy Axis
            interpolated_data = np.zeros((len(energy), abs_y.shape[1], abs_y.shape[2]))
            for i in range(abs_y.shape[1]):  # Loop over first axis
                for j in range(abs_y.shape[2]):  # Loop over second axis
                    interp_func = interp1d(abs_x, abs_y[:, i, j], kind='linear', fill_value="extrapolate")
                    interpolated_data[:, i, j] = interp_func(energy)
            absorptance = interpolated_data
            '''
            '''
            #we better use one A map and scale it with the interpolated spectrum
            abs_x=const.h*const.c/(A_spec['wavelength']*1e-9)
            abs_y=A_spec['absorptance']
            interp_func = interp1d(abs_x, abs_y, kind='linear', fill_value="extrapolate")
            abs_spec_interp = interp_func(energy)

            idx = np.argmax(A_data['wavelength'] >769) # enter desired wavelength here
            A_map = A_data['intensity'][idx]
            absorptance = [A_map*a for a in abs_spec_interp]
            '''

    energy_spec = energy[:, np.newaxis, np.newaxis] # Reshape for broadcasting        

    QFLSy_cube = gaussian_filter(get_QFLSy_value(intensity, energy_spec, absorptance), sigma)

    E_dim, x_dim, y_dim = (fit_range[1]-fit_range[0]), QFLSy_cube.shape[1], QFLSy_cube.shape[2]  # Dimensions of the dataset (E, x, y)
    E_values = energy[fit_range[0]:fit_range[1]] / const.e #E axis values for linear regression
    reshaped_data = QFLSy_cube[fit_range[0]:fit_range[1]].reshape(E_dim, -1) # Reshape data to make the regression vectorized, flatten the (x, y) dimensions so data is of shape (E, x*y)

    slopes, intercepts = np.polyfit(E_values, reshaped_data, 1) # Apply linear regression (degree 1) across the E axis for each flattened pixel

    # Reshape slopes and intercepts back to (x_dim, y_dim)
    slope_array = slopes.reshape(x_dim, y_dim)
    intercept_array = intercepts.reshape(x_dim, y_dim)
    T_map = -1/slope_array
    QFLS_map = intercept_array*T_map

    #print(f"slope: {slope}, Intercept: {intercept}, Temp T [K]: {T}, QFLS: {QFLS}")
    #print(f"R-squared: {r_value**2}")   
    return QFLS_map





def get_EA_map(QFLS_cube, T, fit_range=(0,4)):       
    T_dim, x_dim, y_dim = (fit_range[1]-fit_range[0]), QFLS_cube[0].shape[0], QFLS_cube[0].shape[1]  # Dimensions of the dataset (x, y)
    T_values = T[fit_range[0]:fit_range[1]]
    reshaped_data = np.array(QFLS_cube[fit_range[0]:fit_range[1]]).reshape(T_dim, -1) # Reshape data to make the regression vectorized, flatten the (x, y) dimensions so data is of shape (E, x*y)

    slopes, intercepts = np.polyfit(T_values, reshaped_data, 1) # Apply linear regression (degree 1) across the E axis for each flattened pixel

    # Reshape slopes and intercepts back to (x_dim, y_dim)
    #slope_array = slopes.reshape(x_dim, y_dim)
    intercept_array = intercepts.reshape(x_dim, y_dim)
    EA_map = intercept_array

    print(f"Intercept: {np.nanmean(intercept_array):2f}")
    #print(f"R-squared: {r_value**2}")   
    return EA_map




def get_n_map(d, threshold=0.25, T=302, sigma=(0,0,0)):   
    x1_list = d['I_suns'][d['I_suns']>threshold]
    y1_list = np.array([qfls_map for qfls_map, sun in zip(d['QFLS_maps'], d['I_suns']) if sun > threshold])
    # Step 1: Get the sorted indices of x1
    sorted_indices = np.argsort(x1_list)
    # Step 2: Sort x1 and y1 using the sorted indices
    x1 = np.array(x1_list)[sorted_indices]  # Sort x1
    y1_sorted = y1_list[sorted_indices, :, :]  # Sort y1 along the first axis
    y1=gaussian_filter(y1_sorted, sigma)

    I_dim, x_dim, y_dim = len(x1), y1[0].shape[0], y1[0].shape[1]  # Dimensions of the dataset (x, y) 
    reshaped_data = np.array(y1).reshape(I_dim, -1) # Reshape data to make the regression vectorized, flatten the (x, y) dimensions so data is of shape (E, x*y)

    slopes, intercepts = np.polyfit(np.log(x1), reshaped_data, 1) # Apply linear regression (degree 1) across the E axis for each flattened pixel

    # Reshape slopes and intercepts back to (x_dim, y_dim)
    slope_array = slopes.reshape(x_dim, y_dim)
    #intercept_array = intercepts.reshape(x_dim, y_dim)
    n_map = slope_array*const.e/const.k/T

    #slope, intercept = np.polyfit(np.log(x1), np.nanmean(y1, axis=(1,2)), 1)
    #n_mean = (slope*const.e/const.k/T)
    #print(n_mean)
 
    return n_map