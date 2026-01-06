import plotly.graph_objects as go  # for go.Scatter Plot
import plotly.io as pio

from .update_layout import update_layout_umr

################## MPP TRACKING PLOTS ##################

def plot_mppt(mppt_archive, grid=False, toggle_grid_button=False, fig_power=None, fig_voltage_current=None):
    """
    Plots Power Density and Voltage/Current-Density curves (2 Figures) for Maximum Power Point Tracking (MPPT) analysis using Plotly.

    Parameters:
    - mppt_archive (dict): Dictionary containing MPPT data with the following keys:
        - 'time': List of time values for the MPPT analysis.
        - 'power_density': List of power density values for the Power Density plot.
        - 'voltage': List of voltage values for the Voltage-Current Density plot.
        - 'current_density': List of current density values for the Voltage-Current Density plot.
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
    mppt_data = {
        "time": [0, 1, 2, 3],
        "power_density": [10, 15, 20, 18],
        "voltage": [2, 3, 4, 5],
        "current_density": [5, 8, 10, 9],
    }
    fig_power, fig_voltage_current = plot_mppt(mppt_data)  # Plot MPPT curves
    ```
    """

## Power Density Plot
 
   # Create a Plotly figure
    if not fig_power:
        fig_power = go.Figure()

    # Create trace
    fig_power.add_scatter(x=mppt_archive['time'], y=mppt_archive['power_density'], name='Power Density')
    
    # Definition of standard axis layout
    fig_power.update_layout(
        xaxis_title='Time [s]',
        yaxis_title='Power Density [mw/cm²]',
        # Show/hide grid based on the 'grid' parameter
        xaxis_showgrid=grid,
        xaxis_minor_showgrid=grid, 
        yaxis_showgrid=grid,
        yaxis_minor_showgrid=grid, 
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
    fig_voltage_current.add_scatter(x=mppt_archive['time'], y=mppt_archive['voltage'], name='Voltage')
    fig_voltage_current.add_scatter(x=mppt_archive['time'], y=mppt_archive['current_density'], name='Current Density', yaxis='y2')

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

    # creates grid button
    if toggle_grid_button:
        fig_voltage_current.update_layout(updatemenus = pio.templates['UMR'].layout.updatemenus) # toggle button for grid
    
    # Correct layout
    update_layout_umr(fig_voltage_current)

    fig_voltage_current.show()
    
    # Return the Plotly figure objects for further customization
    return fig_power, fig_voltage_current     
