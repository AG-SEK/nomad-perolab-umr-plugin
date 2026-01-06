import plotly.graph_objects as go
import plotly.io as pio

from .update_layout import update_layout_umr

################## CONNECTION TEST PLOT ##################

def plot_connection_test(connectionTest_data, grid=False, toggle_grid_button=False, fig=None):
    """
    Plots connection test data using Plotly.

    Parameters:
    - connectionTest_data (dict): Dictionary containing connection test data with 'time', 'voltage', and 'current_density'.
    - grid (bool, optional): Toggle to show/hide grid lines. Defaults to False.
    - toggle_grid_button (bool, optional): Toggle to add a button for dynamically showing/hiding grid lines. Defaults to False.
    - fig (plotly.graph_objects.Figure, optional): If provided, the plot will be added to this existing Figure. Defaults to None.

    Returns:
    - plotly.graph_objects.Figure: The Plotly figure object for further customization.

    Usage:
    fig = plot_connectionTest(connectionTest_data)
    """


   # Create a Plotly figure
    if not fig:
        fig = go.Figure()

    # Create trace
    fig.add_scatter(x=connectionTest_data['time'], y=connectionTest_data['voltage'], name='Voltage')
    fig.add_scatter(x=connectionTest_data['time'], y=connectionTest_data['current_density'], name='Current Density', yaxis='y2')

    # Definition of standard axis layout
    colors = pio.templates['UMR'].layout.colorway  # use colors from umr-Ttemplate

    fig.update_layout(
        xaxis_title='Time [s]',
        yaxis=dict(
            title="Voltage [V]",
            color=colors[0],
            linecolor=colors[0],
            mirror=False,
            range=[-1.5,1.5],
        ),
        yaxis2=dict(
            title="Current Density [mA/cm²]",
            color=colors[1],
            linecolor=colors[1],
            overlaying="y",
            side="right",
            mirror=False,
            range=[-40,40],
        ), 
        # Show/hide grid based on the 'grid' parameter
        xaxis_showgrid=grid,
        xaxis_minor_showgrid=grid, 
        yaxis_showgrid=grid,
        yaxis_minor_showgrid=grid, 
    )

    # creates grid button
    if toggle_grid_button:
        fig.update_layout(updatemenus = pio.templates['UMR'].layout.updatemenus) # toggle button for grid
    
    # Correct layout
    update_layout_umr(fig)

    fig.show()

    # Return the Plotly figure objects for further customization
    return fig     

