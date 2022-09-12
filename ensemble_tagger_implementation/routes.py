from ensemble_functions import Annotate_word, Run_external_taggers
from process_features import Calculate_normalized_length, Add_code_context
import logging, os, subprocess, shutil
root_logger = logging.getLogger(__name__)
from flask import Flask, flash, redirect, url_for, request, render_template, send_from_directory, session
from werkzeug.utils import secure_filename

UPLOAD_FOLDER = 'uploads'
RESULTS_FOLDER = 'results'
EXTRACT_FOLDER = 'extract'
ALLOWED_FILE_EXTENSIONS = {'java', 'c', 'h', 'cpp'}
ALLOWED_FOLDER_EXTENSIONS = {'zip':'zip', 'tar.gz':'gztar'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['RESULTS_FOLDER'] = RESULTS_FOLDER
app.config['EXTRACT_FOLDER'] = EXTRACT_FOLDER
app.secret_key = "abc"

compressed_folder_extension = ""

def allowed_file(filename: str):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_FILE_EXTENSIONS


def allowed_file_formats_phrase(format_list):
    return ", ".join(format_list[0:-1]) + ", or " + format_list[-1]


def allowed_file_formats_html(format_list):
    return ",".join(["." + format for format in format_list])


def allowed_file_formats_js(format_list):
    return "[" + ",".join(["\"" + "." + format + "\"" for format in format_list]) + "]"


def allowed_compressed_folder(filename: str):
    result = False

    if '.' in filename:
        for extension in ALLOWED_FOLDER_EXTENSIONS.keys():
            if filename.endswith('.' + extension):
                global compressed_folder_extension
                compressed_folder_extension = extension
                result = True
                break

    return result

@app.route("/")
def landing():
    return render_template("index.html")

@app.route("/upload_file", methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            # code branch when selecting a file
            filename = secure_filename(file.filename)
            # print(filename)

            if not os.path.isdir(app.config['UPLOAD_FOLDER']):
                os.mkdir(app.config['UPLOAD_FOLDER'])

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            if not os.path.isdir(app.config['RESULTS_FOLDER']):
                os.mkdir(app.config['RESULTS_FOLDER'])

            result_file = os.path.join(
                app.config['RESULTS_FOLDER'], filename) + ".xml"
            subprocess.run(
                ["srcml", os.path.join(app.config['UPLOAD_FOLDER'], filename), "-o", result_file])
            #file.close()
            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            response = send_from_directory(app.config['RESULTS_FOLDER'], filename + ".xml", as_attachment=True)
            os.remove(os.path.join(app.config['RESULTS_FOLDER'], filename + ".xml"))
            return response

    return render_template('upload_file.html', file_types_phrase=allowed_file_formats_phrase(list(ALLOWED_FILE_EXTENSIONS)), file_types_html=allowed_file_formats_html(list(ALLOWED_FILE_EXTENSIONS)), file_types_js=allowed_file_formats_js(list(ALLOWED_FILE_EXTENSIONS)))


@app.route("/upload_folder", methods=['GET', 'POST'])
def upload_folder():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_compressed_folder(file.filename):
            # step 1: extract contents of compressed folder into the upload folder using shutil
            filename = secure_filename(file.filename)
            # print(filename)

            if not os.path.isdir(app.config['UPLOAD_FOLDER']):
                os.mkdir(app.config['UPLOAD_FOLDER'])

            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            if not os.path.isdir(app.config['EXTRACT_FOLDER']):
                os.mkdir(app.config['EXTRACT_FOLDER'])

            shutil.unpack_archive(os.path.join(
                app.config['UPLOAD_FOLDER'], filename), app.config['EXTRACT_FOLDER'])

            os.remove(os.path.join(app.config['UPLOAD_FOLDER'], filename))

            # step 2: scan for a directory name (must be 1 directory)
            directory_list = list(os.scandir(app.config['EXTRACT_FOLDER']))
            if len(directory_list) > 0:
                RESULT_FILE_NAME = "result"

                session.pop('_flashes', None)
                print("Name: " + directory_list[0].name)
                print("Path: " + directory_list[0].path)
                # step 3: use srcml with dir parameter and output to result folder
                subprocess.run(
                ["srcml", "--to-dir", app.config['RESULTS_FOLDER'], app.config['EXTRACT_FOLDER']])

                # step 4: delete folder contents in the extract folder
                shutil.rmtree(app.config['EXTRACT_FOLDER'])

                # step 5: make a new zipped archive of the contents
                shutil.make_archive(os.path.join(app.config['RESULTS_FOLDER'],RESULT_FILE_NAME),ALLOWED_FOLDER_EXTENSIONS[compressed_folder_extension],app.config['RESULTS_FOLDER'],app.config['EXTRACT_FOLDER'])

                # step 6: Send compressed folder and delete remaining contents
                response = send_from_directory(app.config['RESULTS_FOLDER'], RESULT_FILE_NAME + "." + compressed_folder_extension, as_attachment=True)
                os.remove(os.path.join(app.config['RESULTS_FOLDER'], RESULT_FILE_NAME + "." + compressed_folder_extension))
                shutil.rmtree(os.path.join(app.config['RESULTS_FOLDER'], app.config['EXTRACT_FOLDER']))
                return response
            else:
                flash("ERROR: Compressed folder is empty")
                return redirect(request.url)

            

    return render_template('upload_folder.html', file_types_phrase=allowed_file_formats_phrase(list(ALLOWED_FOLDER_EXTENSIONS.keys())), file_types_html=allowed_file_formats_html(list(ALLOWED_FOLDER_EXTENSIONS.keys())), file_types_js=allowed_file_formats_js(list(ALLOWED_FOLDER_EXTENSIONS.keys())))

@app.route('/<identifier_type>/<identifier_name>/<identifier_context>')
def listen(identifier_type, identifier_name, identifier_context):
    root_logger.info("INPUT: {ident_type} {ident_name} {ident_context}".format(ident_type=identifier_type, ident_name=identifier_name, ident_context=identifier_context))
    ensemble_input = Run_external_taggers(identifier_type + ' ' + identifier_name, identifier_context)
    ensemble_input = Calculate_normalized_length(ensemble_input)
    ensemble_input = Add_code_context(ensemble_input,identifier_context)
    
    output = []
    for key, value in ensemble_input.items():
        result = Annotate_word(value[0], value[1], value[2], value[3], value[4].value)
        #output.append("{identifier},{word},{swum},{posse},{stanford},{prediction}"
        #.format(identifier=(identifier_name),word=(key),swum=value[0], posse=value[1], stanford=value[2], prediction=result))
        output.append("{word}|{prediction}".format(word=(key[:-1]),prediction=result))
    output_str = ','.join(output)
    return str(output_str)


class MSG_COLORS:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

if __name__ == '__main__':
    if 'PERL5LIB' not in os.environ or os.environ.get('PERL5LIB') == '':
        print(f"{MSG_COLORS.FAIL}**** Warning: PERL5LIB not set; accuracy of the tagger may be compromised.****{MSG_COLORS.ENDC}")
    if 'PYTHONPATH' not in os.environ or os.environ.get('PYTHONPATH') == '':
        print(f"{MSG_COLORS.FAIL}**** Warning: PYTHONPATH not set; if something isn't working, try setting PYTHONPATH****{MSG_COLORS.ENDC}")
    app.run(host='0.0.0.0')
