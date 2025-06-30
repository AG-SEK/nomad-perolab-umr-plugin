import plotly.graph_objects as go
import plotly.io as pio

################## LAYOUT TEMPLATE ##################

# Create a custom template
umr = go.layout.Template()

############# DEFINITION OF PROPERTIES (ALPHABETICALLY SORTED) #############

### AXES
axis_layout = dict(

    # GRID
    showgrid=False,
    gridcolor='lightgrey',
    griddash='solid',         # 'dash'
    gridwidth=1,
    
    # FRAME
    linecolor='black',
    linewidth=3,
    mirror='ticks',           # True, False, 'ticks', 'all', 'allticks'
    showline=True,
    
    # TICKS
    tickmode='auto',
    nticks=20, #20
    tickcolor='black',
    ticklabelstep=2,          # label at every second tick
    ticklen=14,                # length of ticks
    ticks='inside',
    tickwidth=1.5,
    title_standoff=20,
    #tickfont_size=27,
    
    # Minor Ticks
    minor=dict(
        #dtick = None,
        ticks = 'inside',
        ticklen = 8,
        tickcolor = 'black',
        nticks = 2,
        tickmode='auto', # must be linear for log plot to work (changed by Lea 04.04.24)
        showgrid = False, 
    ),
       
    # Zeroline Settings
    zeroline=True,
    zerolinecolor='black',
    zerolinewidth=2.5,
    
    # Miscellaneous
    title_font_size=40, #28      # axis title
    automargin=True,          # Avoid that labels overlap with number
    #fixedrange=False,         # allow moving axis or fix range
    #rangemode= 'nonnegative', # rangemode: 'normal', 'tozero', 'nonnegative'
)
umr.layout.xaxis = axis_layout  # Add axis_layout to template
umr.layout.yaxis = axis_layout


### BACKGROUND COLOR
umr.layout.plot_bgcolor='white'
   
     
### COLORS (of traces in order of appearance)
# umr.layout.colorway = [
#     '#1f82c0',                  # Blue
#     '#f29400',                  # Orange
#     'rgb(25, 150, 125)',        # Turquoise
#     '#d62728',                  # Red
#     '#8c564b',                  # Brown
#     '#e377c2',                  # Pink
#     '#bcbd22',                  # Yellow
#     'rgb(149, 163, 186)',       # Light blue (university logo)
#     '#98df8a',                  # Light Green
#     'rgb(50, 50, 150)',         # Dark blue 
#     'rgb(0, 128, 0)',           # Dark green
#     '#aec7e8',                  # Light Blue
#     '#000000'                   # Black
# ]

colors = {
    'blue': '#1f82c0',              # Blue
    'orange': '#f29400',            # Orange
    'turquoise': '#19967D',         # Turquoise
    'red': '#d62728',               # Red
    'brown': '#8c564b',             # Brown
    'pink': '#e377c2',              # Pink
    'yellow': '#bcbd22',            # Yellow
    'lightblue': '#95A3BA',      # Light blue (university logo)
    'lightgreen': '#98df8a',        # Light Green
    'darkblue': '#323296',          # Dark blue 
    'darkgreen': '#008000',         # Dark green
    'light blue': '#aec7e8',        # Light Blue
    'black': '#000000'              # Black
}

### COLORS (of traces in order of appearance)

umr.layout.colorway = [item for item in colors.values()]


color_gradients = {
    'blue': ['#7bc6ff', '#021a55'],
    'orange': ['#ffe666', '#F07400'],
    'grey': ['#bbafaf', '#3d3d3d'],
    'green': ['#98df8a', '#008000'],
    'pink': ['#E378C3', '#a5035a'],
    'red': ['#fb5d39', '#ad0000'],
    'brown': ['#b0857c', '#593c36'],
    'turquoise': ['#1cffe2', '#198577' ]

    
}

linepattern = [
    'solid',
    'dashdot',
    'dot',
    'dash',
    'longdash',
    'longdashdot'
]
#) or a dash length list in px (eg "5px,10px,2px,2px").


### DIMENSIONS (width and height)
umr.layout.width = 850          # values should be chosen such that in 16:9 presentation one can have plot on right side, comment on left
umr.layout.height = 700
umr.layout.autosize = False 
umr.layout.margin=dict(
        l=0,  # Adjust left margin for y-axis label
        r=10,  # Adjust right margin
        t=100,  # Larger, becsaue of possible titel and buttons
        b=0   # Adjust bottom margin for x-axis label
    )


### FONT (default for everything)
umr.layout.font = dict(
    family='Arial',
    size=40, #  30
    color='black',
)


### LEGEND
umr.layout.showlegend=True       # show legend, also if only one trace
umr.layout.legend = dict(
    xanchor='right',             # aligns legend to top right                  
    yanchor='top',   
    x=0.99,                        
    y=0.99,                  
    bgcolor='rgba(0, 0, 0, 0)',  # transparent background
    font_size=30, # 25
)


### SCATTER PLOT (marker definition)
# List of marker symbols of traces in order of appearance ('-open' means not filled)
markers = [
    'circle',
    'circle-open',
    'square',
    'square-open',
    'diamond',
    'diamond-open',
    'cross',
    'cross-open',
    'star',
    'star-open',
    'x',
    'x-open',
    'triangle-up',
    'triangle-up-open',
    'triangle-down',
    'triangle-down-open',
    'pentagon',
    'pentagon-open',
    'hexagon',
    'hexagon-open',
    'triangle-left',
    'triangle-left-open',
    'triangle-right',
    'triangle-right-open',
    'triangle-ne',
    ]

umr.data.scatter = [dict(                  # sets layout for scatter plots only  
    marker=dict(symbol=sym,                # marker symbol 
                size=14),                  # marker size                      
    mode = 'lines+markers')                # shows markes and lines
    for sym in markers
]


### UPDATEMENUS (TOGGLE GRID BUTTON)
umr.layout.updatemenus=[dict(              # creates toggle button to turn on/off the grid
     buttons=[dict(
        label="Toggle Grid",
        method="relayout",
        args=[{"xaxis.showgrid": False, "yaxis.showgrid": False, "xaxis.minor.showgrid": False, "yaxis.minor.showgrid": False}],  # Turn off grid
        args2=[{"xaxis.showgrid": True, "yaxis.showgrid": True, "xaxis.minor.showgrid": True, "yaxis.minor.showgrid": True}],   # Turn on grid
        visible=True,
            )],
    direction="left",
    type="buttons",
    x=1,
    y=1.1,
    font_size=16,
    showactive = True
)] 
# If the Button should be used this has to be declared in the plot_layout with  
'''
updatemenus = pio.templates['UMR'].layout.updatemenus, # toggle button for grid
'''


# Add optional shape-drawing buttons to modebar
umr.layout.modebar.add=[
    'drawline',
    'drawopenpath',
    'drawclosedpath',
    'drawcircle',
    'drawrect',
    'eraseshape'
    ]

# Modebar properties
#umr.layout.modebar.bgcolor='#7bc6ff' # light blue
#umr.layout.modebar.orientation='v' # vertical modebar
#umr.layout.modebar.displayModeBar=False # Hide modebar


# Show full trace name (when hovering)
umr.layout.hoverlabel = dict(
    namelength=-1
    )


############# ADD TEMPLATE AND SET IT AS DEFAULT #############

pio.templates["UMR"] = umr
pio.templates.default = "UMR"   # Set the custom template as default

