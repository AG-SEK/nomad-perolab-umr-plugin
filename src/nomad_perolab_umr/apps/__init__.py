from nomad.config.models.plugins import AppEntryPoint

from nomad_perolab_umr.apps.chemicals_app import chemicals_app
from nomad_perolab_umr.apps.voila_app import voila_app

chemicals_app_entry_point  = AppEntryPoint(
    name = 'Chemicals App',
    description = 'App to search chemicals.',
    app = chemicals_app
)
    
voila_app_entry_point = AppEntryPoint(
    name='voila',
    description='Find and launch your Voila Tools.',
    app = voila_app
)
    
