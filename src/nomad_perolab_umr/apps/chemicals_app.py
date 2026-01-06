
from nomad.config.models.ui import App, Column, Filters, Menu, MenuItemTerms

# schema definitions
schemas = [
    '*#nomad_perolab_umr.schema_packages.umr_synthesis_classes.UMR_Chemical',
    '*#nomad_perolab_umr.schema_packages.umr_synthesis_classes.UMR_ChemicalLot',
]

chemicals_app = App(
    label='Chemicals App',
    path="chemicals",
    breadcrumb= "Search Chemicals",
    category = "UMR Apps",
    description = "Use this app to search chemicals",
    readme = "longer description",
    #search_quantities=SearchQuantities(include=schemas),
    # Include filtering customized quantities from own schema
    filters=Filters(include=schemas),
    columns=[
        Column(
            quantity="name",
            selected=True,
            title="Chemical Name",
            align="center",
            # unit
            # format = Format(...)
        ),
        Column(
            quantity="data.link_to_product#nomad_perolab_umr.schema_packages.umr_synthesis_classes.UMR_Chemical",
            selected=True,
            title="Link",
            align="left",
        )
    ],
        
    menu=Menu(
        title='Chemicals Database',
        items=[
            MenuItemTerms(
                quantity="entry_type",
                show_input=False,
                title='Search Chemical or Chemical Lot'),
            MenuItemTerms(
                quantity="data.category#nomad_perolab_umr.schema_packages.umr_synthesis_classes.UMR_Chemical",
                show_input=False,
                title='Category'),          
            MenuItemTerms(
                quantity='data.state_of_matter#nomad_perolab_umr.schema_packages.umr_synthesis_classes.UMR_Chemical',
                show_input=False,
                title='State of Matter'),
            MenuItemTerms(
                quantity='data.supplier#nomad_perolab_umr.schema_packages.umr_synthesis_classes.UMR_Chemical',
                show_input=True,
                title='Supplier Abbreviation'),                  
            ]
        ),

    # Dictionary of search filters that are always enabled for queries made
    filters_locked={
        "entry_type": ['UMR_Chemical', 'UMR_ChemicalLot']
    }
)
    