from nomad.config.models.plugins import ExampleUploadEntryPoint

example_upload_entry_point = ExampleUploadEntryPoint(
    title='New Example Upload',
    category='Examples',
    description='Description of this example upload.',
    path='example_uploads/getting_started',
)

voila_scripts_entry_point = ExampleUploadEntryPoint(
    title='PV Voila Scripts',
    category='Examples',
    description='Voila scripts to work with your PV data',
    path='example_uploads/voila_scripts/',
)
