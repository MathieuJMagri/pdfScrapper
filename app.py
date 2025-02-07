# coding=utf-8
import os
import random
from pyairtable import Api
from pdfquery import PDFQuery
from dotenv import load_dotenv
load_dotenv()

import os
from flask import Flask, render_template, request, redirect, url_for, flash
import pdfquery

# Configure the Flask app
app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Replace with a secure key in production
UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

# Ensure the upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    extracted_info = None
    if request.method == 'POST':
        # Check if the POST request has the file part
        if 'pdf_file' not in request.files:
            flash("Aucun fichier n'a été envoyé.")
            return redirect(request.url)
        file = request.files['pdf_file']
        # If no file is selected
        if file.filename == '':
            flash('Aucun fichier sélectionné.')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            try:
                x0 = 18.000
                x1 = 593.00

                ##################################1. Gender Extraction #####################################################################
                genderLabel = pdf.pq('LTTextLineHorizontal:contains("Genre de la personne")')
                left_corner = float(genderLabel.attr('x0'))
                bottom_corner = float(genderLabel.attr('y0'))
                genderTextArray = pdf.pq('LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (x0, bottom_corner-30, x1, bottom_corner)).text()

                #Remove checked box and space and convert to string
                gender = ''.join(genderTextArray[2:])

                #########################################################################################################################

                ##################################2. Age Extraction #####################################################################

                ageLabel = pdf.pq('LTTextLineHorizontal:contains("Âge (par tranches)")')
                left_corner = float(ageLabel.attr('x0'))
                bottom_corner = float(ageLabel.attr('y0'))
                ageTextArray = pdf.pq('LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (x0, bottom_corner-30, x1, bottom_corner)).text()

                #Remove checked box and space and convert to string
                age = ''.join(ageTextArray[2:])

                #########################################################################################################################

                ##################################3. Financial Situation Extraction #####################################################

                financeLabel = pdf.pq('LTTextLineHorizontal:contains("Situation")')
                left_corner = float(financeLabel.attr('x0'))
                bottom_corner = float(financeLabel.attr('y0'))
                financeTextArray = pdf.pq('LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (x0, bottom_corner-30, x1, bottom_corner)).text()

                #Remove checked box and space and convert to string
                financialSituation = ''.join(financeTextArray[2:])

                ########################################################################################################################

                ##################################4. Reason for Consultation ###########################################################

                consultationLabel = pdf.pq('LTTextLineHorizontal:contains("Motifs")')
                left_corner = float(consultationLabel.attr('x0'))
                bottom_corner = float(consultationLabel.attr('y0'))
                consultationTextArray = pdf.pq('LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (x0, bottom_corner-30, x1, bottom_corner)).text()

                #Remove checked box and space and convert to string
                reasonForConsultation = ''.join(consultationTextArray[2:])

                ########################################################################################################################

                ##################################5. Service Asked #####################################################################

                serviceLabel = pdf.pq('LTTextLineHorizontal:contains("Demande")')
                left_corner = float(serviceLabel.attr('x0'))
                bottom_corner = float(serviceLabel.attr('y0'))
                serviceTextArray = pdf.pq('LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (x0, bottom_corner-30, x1, bottom_corner)).text()

                #Remove checked box and space and convert to string
                serviceForConsultation = ''.join(serviceTextArray[2:])

                ######################################################################################################################

                ##################################6. Antecedents #####################################################################

                antecedentLabel = pdf.pq('LTTextLineHorizontal:contains("Antécédents de suivis en santé mentale")')
                left_corner = float(antecedentLabel.attr('x0'))
                bottom_corner = float(antecedentLabel.attr('y0'))
                antecedentTextArray = pdf.pq('LTTextLineHorizontal:in_bbox("%s, %s, %s, %s")' % (x0, bottom_corner-30, x1, bottom_corner)).text()


                #Remove checked box and space and convert to string
                antecedent = ''.join(antecedentTextArray[2:])

                ######################################################################################################################
                ######################################################################################################################
                ######################################################################################################################


                #We now have all of our information, it's time to make API calls to Airtable 
                #We will fill our table from the pdf data acquired from the uploaded pdf
                #We will use Airtables APIs

                AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
                AIRTABLE_ENDPOINT = os.environ.get("AIRTABLE_ENDPOINT")
                AIRTABLE_TABLE_ID = os.environ.get("AIRTABLE_TABLE_ID")
                AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")

                api = Api(AIRTABLE_API_KEY)
                table = api.table(AIRTABLE_BASE_ID, AIRTABLE_TABLE_ID)

                #Create ID
                #ID number starts at 1 and continues
                currentAvailableID = random.randint(1, 1000000)

                table.create({
                    'Numéro de référence': currentAvailableID, 
                    'Genre de la personne': gender, 
                    'Âge':age, 
                    'Région Mondiale': "Non-Disponible", 
                    'Situation Financière':financialSituation, 
                    'Motifs de consultation':reasonForConsultation,
                    'Demande de Service':serviceForConsultation,
                    'Antécédents de suivis en santé mentale':antecedent})

                ######################################################################################################################
                ######################################################################################################################
                ######################################################################################################################



                
            except Exception as e:
                flash(f"Erreur lors du traitement du PDF : {e}")
            # Optionally, remove the file after processing
            os.remove(filepath)
        else:
            flash('Format invalide. Le fichier doit être un pdf.')
    return render_template('index.html', extracted_info=extracted_info)

if __name__ == '__main__':
    app.run(debug=True)
