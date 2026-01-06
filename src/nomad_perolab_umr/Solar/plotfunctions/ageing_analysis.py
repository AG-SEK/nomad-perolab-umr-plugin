#!/usr/bin/env python

# In[3]:


import io
import os
import re
import sys
from collections import Counter
from pprint import pprint

import pandas as pd
import plotly.graph_objects as go

#import .. plottemplate # UMR Template is automatically set as default
#from .. import *
from ..otherfunctions import generate_gradient
from ..plottemplate.umr_plot_template import color_gradients, colors, markers

#module_path = 'K:\solar\9_Topics\Python Analysis Scripts' 
module_path = '/Volumes/Solar/9_Topics/Python Analysis Scripts' # macOS

if module_path not in sys.path:
    sys.path.append(module_path)


# In[4]:


# In[23]:


class DataPlotter:
    def __init__(self, groups):
        self.devices = {}
        self.groups = groups 
        self.units = {'Power (mW/cm²)': 'Power [mW/cm²]', 
                      'Voc (V) RV': 'Open Circuit Voltage [V]',
                      'Jsc (mA/cm2) RV': 'Short Circuit Current Density [mA/cm²]',
                      'Efficiency (%) RV': 'Power Conversion Efficiency [%]',
                      'Fill Factor (%) RV': 'Fill Factor (%)'}

    
    # read_file takes a file_path and returns the device name and the data as a pandas dataframe
    def read_file(self, file_path):
        with open(file_path, encoding='ISO-8859-1') as file:
            file_content = file.read()

        device_name_match = re.search(r'Device\t([^\n\r]+)', file_content)
        device_name = device_name_match.group(1) if device_name_match else "Unknown Device"

        data_part = file_content.split('## Data ##')[1].strip()
        data_df = pd.read_csv(io.StringIO(data_part), sep='\t')

        return device_name, data_df

    
    # add_file takes the file path and the device type, calls function read_file and adds the data to the dictionary devices
    def add_file(self, file_path, device_type):
        device_name, data_df = self.read_file(file_path)
        
        if device_name not in self.devices:
            self.devices[device_name] = {'data': [], 'type': device_type}
        

        filtered_columns = [col for col in data_df.columns if 'Jsc' in col or 'current' in col or 'P_' in col or 'Power' in col or 'Efficiency' in col]
        if device_name.split('-')[1] == '6':
            correction_factor = 1/1.392
        else:
            correction_factor = 0.25/0.3087

            
        for c in filtered_columns:
            data_df[c] = data_df[c]*correction_factor    

         
        self.devices[device_name]['data'].append(data_df) # each entry will have two data sets, as we have two files for each device 


    def plot_individual(self, path):
        
        pprint(self.devices)
                
        for device_name, device_info in self.devices.items(): # loop through all devices 
            
            for data_df in device_info['data']: # for each device look at the data
                
                fig = go.Figure()
                
                # plot power over time 
                if 'Power (mW/cm²)' in data_df.columns: 

                    fig.add_scatter(x = data_df['Time (Hours)'].values, 
                                    y = data_df['Power (mW/cm²)'].values, 
                                    name = 'Power (mW/cm²)')
                    
                    fig.update_layout(xaxis_title = 'Time [h]',
                                      yaxis_title = "Power [mW/cm²]", 
                                      showlegend = False)

                    fig.write_image(path+"Power_"+device_name+'.png')
                
                # plot voc, jsc and ff over time 
                elif 'Voc (V) RV' and 'Jsc (mA/cm2) RV' and 'Fill Factor (%) RV' in data_df.columns:
                    
                    # Add Voc trace
                    fig.add_trace(
                        go.Scatter(x=data_df['Time (Hours)'], 
                                   y=data_df['Voc (V) RV'],
                                   name='Voc',)
                    )
                    

                    # Add Jsc trace
                    fig.add_trace(
                        go.Scatter(x = data_df['Time (Hours)'], 
                                   y = data_df['Jsc (mA/cm2) RV'],
                                   name = 'Jsc',
                                   yaxis = "y2",)
                    )

                    # add FF trace
                    fig.add_trace(
                        go.Scatter(x = data_df['Time (Hours)'], 
                                   y = data_df['Fill Factor (%) RV'],
                                   name = 'Fill Factor',
                                   yaxis = "y3",)
                    )


                    # Set y-axes titles, add three y-axis each in the same color as the trace 
                    fig.update_layout(
                        xaxis=dict(
                            domain=[0.3, 0.7]
                        ),
                        yaxis=dict(
                            title="Open Circuit Voltage [V]",
                            titlefont=dict(
                                color=list(colors.values())[0]
                            ),
                            tickfont=dict(
                                color=list(colors.values())[0]
                            )
                        ),
                        yaxis2=dict(
                            title="Short Circuit Current Density [mA/cm²]",
                            titlefont=dict(
                                color=list(colors.values())[1]
                            ),
                            tickfont=dict(
                                color=list(colors.values())[1]
                            ),
                            anchor="x",
                            overlaying="y",
                            side="right",
                            ticks='',             # No ticks
                            showticklabels=True   # But show labels
                        ),
                        yaxis3=dict(
                            title="Fill Factor [%]",
                            titlefont=dict(
                                color=list(colors.values())[2]
                            ),
                            tickfont=dict(
                                color=list(colors.values())[2]
                            ),
                            anchor="free",
                            overlaying="y",
                            side="right",
                            position=0.8,
                            ticks='',             # No ticks
                            showticklabels=True   # But show labels
                        )
                    )
                    
                    
                    fig.update_layout(
                        xaxis_title = "Time [h]",
                        width=1600,
                        legend=dict(x=0.7)
                    )
                    
                    
                    fig.write_image(path+"JscVocFF_"+device_name+'.png')


    def plot_combined(self, variable, i=0):

        
        fig = go.Figure()

        # create a list of length len(groups) that can be used to iterate over the indeces
        gradients = {}
        
        # create a gradient for each group, each gradient contains as many colors as there are devices in the group 
        # Extract device types from the devices dictionary
        device_types = [device_info['type'] for device_info in self.devices.values()]

        # Use Counter to count occurrences of each device type
        type_counts = list(Counter(device_types).items())
        print(type_counts)
        
        for (k, group) in zip(range(len(self.groups)),self.groups):
            gradients[group] = {"gradient": generate_gradient( list(color_gradients.values())[k], type_counts[k][1]), 
                                "index": 0, 
                                "marker": (markers[1::3])[k],
                                "slicer": k*50}

        
        added_to_legend = set()

        for device_name, device_info in self.devices.items():
            if device_info['type'] in self.groups:
                for data_df in device_info['data']:
                    if variable in data_df.columns:
                        # Efficient downsampling
                        if i > 0:
                            downsampled_df = data_df[::i]
                        else:
                            downsampled_df = data_df

                        # Get the color and update the index
                        color = gradients[device_info['type']]["gradient"][gradients[device_info['type']]["index"]]
                        gradients[device_info['type']]["index"] += 1

                        # Check if this group is already added to the legend
                        show_legend = False
                        if device_info['type'] not in added_to_legend:
                            show_legend = True
                            added_to_legend.add(device_info['type'])

                        # Add trace to the figure
                        fig.add_trace(go.Scatter(
                            x=downsampled_df['Time (Hours)'],
                            y=downsampled_df[variable],
                            mode = 'lines',
                            line=dict(color=color),
                            name=device_info['type'] if show_legend else "",  # Show the group name only once
                            legendgroup=device_info['type'],
                            showlegend=show_legend,  # Control legend display
                            hovertemplate=(f"Device: {device_name}<br>Type: {device_info['type']}<br>"
                                           f"Time [h]: %{{x}}<br>{variable}: %{{y}}<extra></extra>")
                        ))
                        
                        
                        # Add trace to the figure
                        fig.add_trace(go.Scatter(
                            x=data_df['Time (Hours)'][gradients[device_info['type']]["slicer"]::100],
                            y=data_df[variable][gradients[device_info['type']]["slicer"]::100],
                            mode = 'markers',
                            marker = dict(symbol = gradients[device_info['type']]["marker"], color = color),
                            showlegend = False
                        ))
                        
        # Update layout for aesthetics
        fig.update_layout(
            xaxis_title='Time [h]',
            yaxis_title=self.units[variable],
            #legend_title_text='Device Type',
            hovermode='closest'
        )

        # To simulate separate legends or groupings, you might add annotations or custom hover text.
        # However, this example keeps the legend unified for simplicity and clarity.

        fig.show()

    def plot_combined_power(self, i=0):
        self.plot_combined('Power (mW/cm²)', i)

    
    def plot_combined_Voc(self, i=0):
        self.plot_combined('Voc (V) RV', i)


    def plot_combined_Jsc(self, i=0):
        self.plot_combined('Jsc (mA/cm2) RV', i)
        
        
    def plot_combined_PCE(self, i=0):
        self.plot_combined('Efficiency (%) RV', i)
        
    def plot_combined_FillFactor(self,  i=0):
        self.plot_combined('Fill Factor (%) RV', i)
    
    
    def compare_efficiencies(self):
        for device_name, device_info in self.devices.items(): # loop through all devices 
            
            fig = go.Figure()

            for data_df in device_info['data']: # for each device look at the data

                    
                    # plot power over time 
                    if 'Voc (V) RV' and 'Jsc (mA/cm2) RV' and 'Fill Factor (%) RV' in data_df.columns:
                        
                        
                         # Add FW efficiency 
                        fig.add_trace(
                            go.Scatter(x=data_df['Time (Hours)'], 
                                       y=data_df['Efficiency (%) FW'],
                                       name='Forward Scan',
                                       mode = 'lines', 
                                       line=dict(color=list(colors.values())[0]),
                                       showlegend = False 
                                       )
                        )
                        
                        fig.add_trace(
                            go.Scatter(x=data_df['Time (Hours)'][::50], 
                                       y=data_df['Efficiency (%) FW'][::50],
                                       name='Forward Scan',
                                       mode = 'markers',
                                       marker=dict(color=list(colors.values())[0], symbol = markers[0]), 
                                       showlegend = False 
                                      )
                        )
                        
                        fig.add_trace(
                            go.Scatter(x=data_df['Time (Hours)'][:1], 
                                       y=data_df['Efficiency (%) FW'][:1],
                                       mode = 'lines+markers',
                                       marker=dict(color=list(colors.values())[0], symbol = markers[0]),
                                       line=dict(color=list(colors.values())[0]), 
                                       name = "Forward Scan"
                                      )
                        )




                        # Add reverse efficiency
                        fig.add_trace(
                            go.Scatter(x=data_df['Time (Hours)'], 
                                       y=data_df['Efficiency (%) RV'],
                                       mode = 'lines', 
                                       line=dict(color=list(colors.values())[1]),
                                       showlegend = False
                                       )
                        )
                        
                        fig.add_trace(
                            go.Scatter(x=data_df['Time (Hours)'][::100], 
                                       y=data_df['Efficiency (%) RV'][::100],
                                       mode = 'markers',
                                       marker=dict(color=list(colors.values())[1], symbol = markers[1]),
                                       showlegend = False
                                      )
                        )
                        
                        fig.add_trace(
                            go.Scatter(x=data_df['Time (Hours)'][:1], 
                                       y=data_df['Efficiency (%) RV'][:1],
                                       mode = 'lines+markers',
                                       marker=dict(color=list(colors.values())[1], symbol = markers[1]),
                                       line=dict(color=list(colors.values())[1]), 
                                       name = "Reverse Scan"
                                      )
                        )
                        
                        
                        
                        # update axis 
                        fig.update_layout(
                            xaxis_title = "Time [h]",
                            yaxis_title = 'Power Conversion Efficiency [%]',
                            #legend=dict(x=0.7)
                        )
                    
                    if 'Power (mW/cm²)' in data_df.columns: 
                        # Add PCE from MPP data
                        
                        fig.add_trace(
                            go.Scatter(x=data_df['Time (Hours)'][::500], 
                                       y=data_df['Power (mW/cm²)'][::500],
                                       mode = 'lines', 
                                       line=dict(color=list(colors.values())[2]),
                                       showlegend = False
                                       )
                        )
                        
                        fig.add_trace(
                            go.Scatter(x=data_df['Time (Hours)'][::40000], 
                                       y=data_df['Power (mW/cm²)'][::40000],
                                       mode = 'markers',
                                       marker=dict(color=list(colors.values())[2], symbol = markers[2]),
                                       showlegend = False
                                      )
                        )
                        
                        fig.add_trace(
                            go.Scatter(x=data_df['Time (Hours)'][:1], 
                                       y=data_df['Power (mW/cm²)'][:1],
                                       mode = 'lines+markers',
                                       marker=dict(color=list(colors.values())[2], symbol = markers[2]),
                                       line=dict(color=list(colors.values())[2]), 
                                       name = "MPP Tracking"
                                      )
                        )

            fig.show()







        


# In[25]:


def find_files(base_path, exclude = []):
    """
    Searches for text files containing "Parameters" and "Tracking" in their names
    within a specific directory structure. Assumes each subdirectory of the given
    base_path contains another directory, which then contains multiple text files.
    
    Args:
    - base_path (str): The path to the top-level directory.
    
    Returns:
    - dict: A dictionary with device names as keys and lists of file paths as values.
    """
    device_files = {}
    
    # Traverse through the directory structure
    for root, dirs, files in os.walk(base_path):
        for file in files:
            if "Parameters" in file or "Tracking" in file:
                # Extract device name from filename
                device_name = file.split('_')[-1].split('.')[0]
                
                # Build the full path to the file
                file_path = os.path.join(root, file)
                
                # Add the file path to the dictionary under the device name
                if device_name not in exclude:
                    if device_name in device_files:
                        device_files[device_name].append(file_path)
                    else:
                        device_files[device_name] = [file_path]
    
    print("The following devices were found: ")
    for device in device_files: 
        print(device)
        
    
    return device_files




# In[24]:





# In[29]:





# In[ ]:




