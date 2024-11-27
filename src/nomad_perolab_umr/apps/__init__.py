from nomad.config.models.plugins import AppEntryPoint
from nomad.config.models.ui import App, Column, Columns, FilterMenu, FilterMenus, Filters, FilterMenuActions, FilterMenuActionCheckbox

schema = 'nomad_perolab_umr.schema_packages.umr_synthesis_classes.UMR_Chemical'

chemicals_app_entry_point  = MyAppEntryPoint(
    name = 'MyApp',
    description = 'My custom app.',
    app = App(
        label='Chemicals App',
        path=chemicals,
        breadcrumb= "Search Chemicals",
        category = "UMR Apps",
        description = "Use this app to search chemicals",
        readme = "longer description",
        # Include filtering custoized quantities from own schema
        filters=Filters(include=[f'*#{schema}']),
        columns=[Columns(
            quantity="name",
            selected=True,
            title="Chemical Name",
            align="center",
            # unit
            # format = Format(...)
        )
        , Columns(
            quantity=f"data.link_to_product#{schema}",
            selected=True,
            title="Link",
            align="left",
        )],
        # Dictionary of search filters that are always enabled for queries made
        filters_locked={
            "section_defs.definition_qualified_name:all": [schema]
        },
         # Controls the filter menus shown on the left
        filter_menus=FilterMenus(
            options={
                'material': FilterMenu(label="Material"),
                'state':FilterMenu(
                    label="State of Matter",
                    level=1,
                    actions=FilterMenuActions(
                        options={
                            'liquid': FilterMenuActionCheckbox(type="checkbox", label="LIQ", quantity=f"data.state_of_matter#{schema}"),
                            'solid': FilterMenuActionCheckbox(type="checkbox", quantity=f"data.state_of_matter#{schema}")}
                        )
                )
            }
        )
    )

    
app_entry_point = AppEntryPoint(
    name='NewApp',
    description='New app entry point configuration.',
    app=App(
        label='NewApp',
        path='app',
        category='simulation',
        columns=Columns(
            selected=['entry_id'],
            options={
                'entry_id': Column(),
            },
        ),
        filter_menus=FilterMenus(
            options={
                'material': FilterMenu(label='Material'),
            }
        ),
    ),
)
