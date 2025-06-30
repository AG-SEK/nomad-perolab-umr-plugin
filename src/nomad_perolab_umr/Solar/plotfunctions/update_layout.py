#### HELPER FUNCTION TO ADJUST THE SIZE OF THE GRAPH ####

def update_layout_umr(fig):
    """
    Because some programs (e.g. VS Code, JupyterNotebook) have their on default values which overwrite our default template values it is neccessary
    to adjust some parameters again not only in the template, but with the update_layout function.
    The parameters are so far:
        - width, height
    """
    fig.update_layout(
        width=800,
        height=700,
    )
