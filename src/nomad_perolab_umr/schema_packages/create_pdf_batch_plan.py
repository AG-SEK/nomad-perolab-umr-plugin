from fpdf import FPDF


def get_entry_id_from_reference(reference):
    '''
    Function to extract the entry:id from a nomad reference
    '''
    # Splitte den String bei 'archive/' und bei '/' und nimm den ersten Teil
    entry_id = reference.split("archive/")[1].split("#/")[0]

    return entry_id


def get_varying_process(data):
    '''
    Function to extract the processes which are varied
    '''
    
    varied_processes = []

    for process in data['standard_processes_for_variation']:
        if "process_is_varied" in process:
            if process['process_is_varied'] == True:
                varied_processes.append(process)
        
    return varied_processes

# def get_layers(data):

#     layers = []

#     # Hier uss ich mit einem Verweis arbeiten geht nicht mehr über
#     for p in data['standard_processes_for_variation']:
#         entry_id = get_entry_id_from_reference(p['process_reference'])
#         process = get_archive_by_entry_id(entry_id, base_url=local_base_url, auth_header=auth_header)
#         #process = get_archive_by_entry_id(entry_id)


#         if "layer" in process:
#             layers.append(process['layer'])
                          
#     return layers


def convert_datetime(iso_date):
    '''
    Function to convert iso datetime string into a differnt better readable format
    '''
    from datetime import datetime

    # Conversion into datetime object
    dt = datetime.fromisoformat(iso_date)

    # Formatting
    formatted_date = dt.strftime('%A, %d.%m.%Y')

    return formatted_date


def html_to_pdf(html):
    '''
    Function to convert html text to a normal string text (by replacing or deleting the html tags)
    '''
    import re

    # Replace <li> tags with bullet points
    html = re.sub(r'<li>(.*?)</li>', r'- \1', html)
    
    # Replace <p> tags with line breaks
    html = re.sub(r'<p>', '', html)
    html = re.sub(r'</p>', '\n', html)

    # Remove all other HTML tags
    html = re.sub(r'<.*?>', '', html)

    # Remove leading and trailing whitespace
    text = html.strip()

    return text

def find_maximum_number_of_substrates(groups):
    '''
    Function to find the maxmimum number of substrates for one group - to calculate the column height
    '''

    # Initialize the maximum number of substrates with a very low value
    max_substrates = 0

    # Iterate through all groups in the list
    for group in groups:
        # Get the number of substrates for the current group
        number_of_substrates = group["number_of_substrates"]
        
        # Compare with the current maximum number
        max_substrates = max(max_substrates, number_of_substrates)

    # Return the maximum number of substrates found
    return max_substrates




# PDF Erstellung
class BatchPlanPDF(FPDF):
    #def header(self):
    #    self.set_font('Arial', 'B', 10)
    #    self.cell(0, 10, f'Batch Plan', 0, 1, 'C')
    #    self.ln()


    def main_title(self, title):
        # Bold main title
        self.set_font('Arial', 'B', 20)
        self.cell(0, 10, title, ln=True)


    def chapter_title(self, title):
        # Bold chapter title
        self.set_font('Arial', 'B', 16)
        self.cell(0, 10, title, ln=True)


    def general_body(self, key, value):
        # Bold Key
        self.set_x(20)
        self.set_font('Arial', 'B', 12)        
        self.cell(60, 10, f"{key}:", 0, 0)  
        # Normal value
        self.set_font('Arial', '', 12)        # Normale Schriftart für den Wert
        self.multi_cell(0, 10, f"{value}")     # 0 ist die Breite (geht bis zum Rand), 10 ist die Höhe der Zeile

    def group_body(self, group):
        # Bold Group Number
        self.set_x(20)
        self.set_font('Arial', 'B', 12)     
        self.cell(30, 10, f"Group {group['group_number']}:", ) 
        # Normal Group Name
        self.set_font('Arial', '', 12)        
        self.cell(0, 10, f"{group['group_description']}", ln=True) 

    def layer_body(self, all_layers):
        self.set_font('Arial', 'B', 12)
        self.cell(60, 10, "Name", border=1) 
        self.cell(60, 10, "Material", border=1) 
        self.cell(60, 10, "Layer Type", border=1) 
        self.cell(60, 10, "Deposition Method", border=1, ln=True) 

        self.set_font('Arial', '', 12)
        for layers in reversed(all_layers):
            for layer in layers:
                self.cell(60, 10, f"{layer['layer_name']}", border=1) 
                self.cell(60, 10, f"{layer['layer_material_name']}", border=1) 
                self.cell(60, 10, f"{layer['layer_type']}", border=1) 
                self.cell(60, 10, f"{layer['deposition_method']}", border=1, ln=True) 
    


    def variation_body(self, varied_process):
        
        # Print name of varied process
        # Subheading
        self.set_x(20)
        self.set_font('Arial', 'B', 12)    
        self.cell(200, 10, f"{varied_process['name']}:", ln=True)

        self.set_font('Arial', '', 12)        

        # Print information about parameter variation (if possible)
        if "parameter_variation" in varied_process:
            # Subheading
            self.set_font('Arial', 'U', 12)      
            self.set_x(30)
            self.cell(200, 10, "Parameter Variation:", ln=True)
            # Body
            self.set_font('Arial', '', 12)  
            self.set_x(40)
            self.cell(200, 10, f"Parameter: {varied_process['parameter_variation']['parameter_path']}", ln=True)
            self.set_x(40)
            self.cell(200, 10, f"Values: {varied_process['parameter_variation']['parameter_values']}", ln=True)
            self.set_x(40)
            self.cell(200, 10, f"Unit: {varied_process['parameter_variation']['parameter_unit']}", ln=True)

        # List Varied processes
        # Subheading
        self.set_font('Arial', 'U', 12)        
        self.set_x(30)
        self.cell(200, 10, "Varied Processes:", ln=True)
        # Body
        self.set_font('Arial', '', 12)  
        for i, process in enumerate(varied_process['varied_processes']):
            self.set_x(40)
            self.cell(200, 10, f"Process {i}: {process['name']}", ln=True)


    def table(self, data):
        column_width_1 = 70
        column_width_2 = 15
        font_size = 8
        self.set_fill_color(200, 220, 255)  # light blue as fill color

        # Row 1: Groups
        line_height = 10
        self.set_font('Arial', 'B', font_size)
        # First column
        self.cell(column_width_1, line_height, 'Process Name', 1)
        # Rest of columns
        for group in data['groups_for_selection_of_processes']:
            self.cell(column_width_2, line_height, f"Group {group['group_number']}", 1, 0, 'C')  # Header für Gruppen
        self.ln()

        # Row 2   
        line_height = 4
        groups = data['groups_for_selection_of_processes']
        maximum_number_substrates = find_maximum_number_of_substrates(groups)
        current_y = self.get_y()
        # First column
        self.cell(column_width_1, maximum_number_substrates*line_height, "Substrates", 1, 0, 'C')
        # Rest of columns
        for i, group in enumerate(groups):
            # Set coordinates
            self.set_y(current_y)
            self.set_x(self.get_x() + column_width_1- column_width_2 + (i+1)*column_width_2)
            # Prepare Text
            text = ""
            substrates = group['substrate_engraved_numbers']
            substrates.extend([""] * (maximum_number_substrates - len(substrates)))
            for substrate in substrates:
                text += f"{substrate} \n"  

            self.multi_cell(column_width_2, line_height, text, 1, 'C')
        self.ln()

        # Row 3 - .... Processes
        varied_processes = get_varying_process(data)
        names_of_varied_processes = [process["name"] for process in varied_processes]

        self.set_y(self.get_y()-line_height)
        line_height = 10

        for process in data['standard_processes_for_variation']:
            process_name = process['name']
            # Check if process is varied
            if process_name in names_of_varied_processes:
                self.set_fill_color(255, 150, 150)  # Ein Rot         # Setze die Füllfarbe (RGB)
                self.cell(column_width_1, line_height, process_name, border=1, fill=True)
            else:
                self.set_fill_color(200, 220, 255)  # Ein leichtes Blau         # Setze die Füllfarbe (RGB)
                self.cell(column_width_1, line_height, process_name, border=1, fill=False)
            # Mark used processes with "X"
            for group in groups:
                for selected_process in group['select_processes']:
                    process_found = False
                    if process_name in selected_process['display_name']:
                        self.cell(column_width_2, line_height, 'X', align='C', fill=True, border=1)
                        process_found=True
                        break
                if not process_found:
                    self.cell(column_width_2, line_height, '', border=1)
            self.ln()

                    

def create_pdf(data):
    pdf = BatchPlanPDF(orientation='L', unit='mm', format='A4')  # Querformat A4
    pdf.add_page()

    # Title 
    pdf.main_title(f"Batch Plan - {data['batch_id']}")

    # General Information
    pdf.chapter_title('General Information')
    pdf.general_body("Batch Description", data['batch_description'])
    #pdf.general_body('Batch Number', data['batch_number'])
    pdf.general_body('Date', convert_datetime(data['datetime']))
    pdf.general_body("Responsible Person", data['responsible_person'])
    pdf.ln()
    pdf.general_body("Description", html_to_pdf(data['description']))
    pdf.ln()

    # Layers
    pdf.chapter_title('Stack')
   # all_layers = get_layers(data)
  #  pdf.layer_body(all_layers)
    pdf.ln()
    

    # Parameter Variation
    pdf.chapter_title('Parameter variation')
    varied_processes = get_varying_process(data)
    for process in varied_processes:
        pdf.variation_body(process)
    pdf.ln()

    # Groups
    pdf.chapter_title('Groups')
    for group in data['groups_for_selection_of_processes']:
        pdf.group_body(group)
    pdf.ln()

    

    # Matrix
    pdf.add_page()
    pdf.chapter_title('Process Matrix')
    pdf.table(data)


    # PDF speichern
    pdf.output('batch_plan_report_TEST.pdf')
