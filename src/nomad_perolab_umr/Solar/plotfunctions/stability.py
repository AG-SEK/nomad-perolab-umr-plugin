import plotly.graph_objects as go  # for go.Scatter Plot
import plotly.io as pio

from .update_layout import update_layout_umr

################## STABILITY PARAMETERS PLOTS ##################

# List of all available parameters
JVparameters_list = ["open_circuit_voltage",
                  "short_circuit_current_density",
                  "fill_factor",
                  "efficiency",
                  "potential_at_maximum_power_point",
                  "current_density_at_maximum_power_point",
                  "power_at_maximum_power_point",
                  "series_resistance_ohm",
                  "shunt_resistance_ohm"]

# Dictionary with plot names for different parameters
JVparameters_name_dict = dict(
    open_circuit_voltage = "Voc",
    short_circuit_current_density = "Jsc",
    fill_factor = "Fill Factor",
    efficiency = "Efficiency",
    potential_at_maximum_power_point = "Vmpp",
    current_density_at_maximum_power_point = "Jmpp",
    power_at_maximum_power_point = "Pmpp",
    series_resistance_ohm = "Rseries",
    shunt_resistance_ohm = "Rshunt"
)

# Dictionary with y-axis labels for different parameters
JVparameters_yaxis_title_dict = dict(
    open_circuit_voltage = "Voc [V]",
    short_circuit_current_density = "Jsc [mA/cm²]",
    fill_factor = "Fill Factor",
    efficiency = "Efficiency [%]",
    potential_at_maximum_power_point = "Vmpp [V]",
    current_density_at_maximum_power_point = "Jmpp [mA/cm²]",
    power_at_maximum_power_point = "Pmpp [mW/cm²]",
    series_resistance_ohm = "Rseries [Ohm]",
    shunt_resistance_ohm = "Rshunt [Ohm]"
)


# Function for creating a Plotly Graph object for a specific variable over time
def plot_stability_parameter(stability_data, parameter, grid=False, toggle_grid_button=False, fig=None):
    """
    Plots stability parameter variations over time using Plotly.

    Parameters:
    - stability_data (dict): Dictionary containing time and JV stability parameter values.
    - parameter (str): Name of the stability parameter to be plotted.
        "open_circuit_voltage",
        "short_circuit_current_density",
        "fill_factor",
        "efficiency",
        "potential_at_maximum_power_point",
        "current_density_at_maximum_power_point",
        "power_at_maximum_power_point",
        "series_resistance_ohm",
        "shunt_resistance_ohm"]
    - grid (bool, optional): Flag to control the visibility of the grid in the plot. Default is False.
    - toggle_grid_button (bool, optional): Flag to control the visibility of the Toggle Grid Button in the plot. Default is False.
    - fig (plotly.graph_objects.Figure, optional): Existing Plotly figure to which the stability parameter curve will be added. If None, a new figure will be created.

    Returns:
    - fig (plotly.graph_objects.Figure): Plotly figure object.

    Example:
    ```python
    # Sample data
     stability_data =
        {"time": [400, 500, 600, 700], "open_circuit_voltage": [0.2, 0.5, 0.8, 0.6]}, "short_circuit_current_density": ...
    fig = plot_stability_parameter(stability_data, "open_circuit_voltage)    
    """
    
    # Create a Plotly figure
    if not fig:
        fig = go.Figure()

    # Create trace
    fig.add_scatter(x=stability_data['time'], y=stability_data[parameter], name=JVparameters_name_dict[parameter])
    
    # Definition of standard axis layout
    fig.update_layout(
        xaxis_title='Time [hours]',
        yaxis_title= JVparameters_yaxis_title_dict[parameter],
        # Show/hide grid based on the 'grid' parameter
        xaxis_showgrid=grid,
        xaxis_minor_showgrid=grid, 
        yaxis_showgrid=grid,
        yaxis_minor_showgrid=grid, 
        # show only positive range
        xaxis_rangemode='nonnegative', 
        yaxis_rangemode='nonnegative',
    )

    # Creates grid button
    if toggle_grid_button:
        fig.update_layout(updatemenus = pio.templates['UMR'].layout.updatemenus) # toggle button for grid
    
   # Correct layout
    update_layout_umr(fig)

    return fig




    ################## STABILITY TRACKING PLOTS ##################

def plot_stability(tracking_data, step=100, grid=False, toggle_grid_button=False, fig_power=None, fig_voltage_current=None):
    """
    Plots Power Density and Voltage/Current-Density curves (2 Figures) for Stability Tracking using Plotly.

    Parameters:
    - mppt_archive (dict): Dictionary containing MPPT data with the following keys:
        - 'time': List of time values for the plot.
        - 'power_density': List of power density values for the Power Density plot.
        - 'voltage': List of voltage values for the Voltage-Current Density plot.
        - 'current_density': List of current density values for the Voltage-Current Density plot.
    - step (int, optional): Step size for data reduction. Only every 'step' data point will be plotted. Default is 100.
    - grid (bool, optional): Flag to control the visibility of the grid in the plots. Default is False.
    - toggle_grid_button (bool, optional): Flag to control the visibility of the Toggle Grid Button in the plots. Default is False.
    - fig_power (plotly.graph_objects.Figure, optional): Existing Plotly figure for the Power Density plot. If None, a new figure will be created.
    - fig_voltage_current (plotly.graph_objects.Figure, optional): Existing Plotly figure for the Voltage/Current-Density plot. If None, a new figure will be created.

    Returns:
    - fig_power (plotly.graph_objects.Figure): Plotly figure object for the Power Density plot.
    - fig_voltage_current (plotly.graph_objects.Figure): Plotly figure object for the Voltage/ Current-Density plot.

    Example:
    ```python
    # Sample MPPT data
    tracking_data = {
        "time": [0, 1, 2, 3],
        "power_density": [10, 15, 20, 18],
        "voltage": [2, 3, 4, 5],
        "current_density": [5, 8, 10, 9],
    }
    fig_power, fig_voltage_current = plot_stability(tracking_data)  # Plot Stability curves
    ```
    """

## Reduce data based on the specified step size
    # Typically the tracking_data is big (>100.000 data points), thus processing might take long
    # Only every 'step' data point will be plotted.
    reduced_data = dict(
            time = tracking_data['time'][::step],
            voltage =  tracking_data['voltage'][::step],
            current_density = tracking_data['current_density'][::step],
            power_density = tracking_data['power_density'][::step],
    )


## Power Density Plot
 
   # Create a Plotly figure
    if not fig_power:
        fig_power = go.Figure()

    # Create trace
    fig_power.add_scatter(x=reduced_data['time'], y=reduced_data['power_density'], name='Power Density')
    
    # Definition of standard axis layout
    fig_power.update_layout(
        xaxis_title='Time [hours]',
        yaxis_title='Power Density [mw/cm²]',
        # Show/hide grid based on the 'grid' parameter
        xaxis_showgrid=grid,
        xaxis_minor_showgrid=grid, 
        yaxis_showgrid=grid,
        yaxis_minor_showgrid=grid, 
    )

    # Add text annotation for step size above the plot
    fig_power.add_annotation(
        x=0.5,
        y=1.1,
        xref='paper',
        yref='paper',
        text=f"every {step}th data point",
        showarrow=False,
        #font=dict(size=10),
    )

    # creates grid button
    if toggle_grid_button:
        fig_power.update_layout(updatemenus = pio.templates['UMR'].layout.updatemenus) # toggle button for grid
    
    # Correct layout
    update_layout_umr(fig_power)
    fig_power.show()

## Voltage and Current Density Plot

   # Create a Plotly figure
    if not fig_voltage_current:
        fig_voltage_current = go.Figure()

    # Create trace
    trace_voltage = fig_voltage_current.add_scatter(x=reduced_data['time'], y=reduced_data['voltage'], name='Voltage')
    trace_current_density = fig_voltage_current.add_scatter(x=reduced_data['time'], y=reduced_data['current_density'], name='Current Densityt', yaxis='y2')

    # Definition of standard axis layout
    colors = pio.templates['UMR'].layout.colorway  # use colors from umr-Ttemplate

    fig_voltage_current.update_layout(
        xaxis_title='Time [s]',
        yaxis=dict(
            title="Voltage [V]",
            color=colors[0],
            linecolor=colors[0],
            mirror=False,
        ),
        yaxis2=dict(
            title="Current Density [mA/cm²]",
            color=colors[1],
            linecolor=colors[1],
            overlaying="y",
            side="right",
            mirror=False,
        ), 
        # Show/hide grid based on the 'grid' parameter
        xaxis_showgrid=grid,
        xaxis_minor_showgrid=grid, 
        yaxis_showgrid=grid,
        yaxis_minor_showgrid=grid, 
    )

    # Add text annotation for step size above the plot
    fig_power.add_annotation(
        x=0.5,
        y=1.1,
        xref='paper',
        yref='paper',
        text=f"every {step}th data point",
        showarrow=False,
        #font=dict(size=10),
    )

    # creates grid button
    if toggle_grid_button:
        fig_voltage_current.update_layout(updatemenus = pio.templates['UMR'].layout.updatemenus) # toggle button for grid
    
    # Correct layout
    update_layout_umr(fig_voltage_current)

    fig_voltage_current.show()
    
    # Return the Plotly figure objects for further customization
    return fig_power, fig_voltage_current     
