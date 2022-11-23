from sys import stdout
from ensemble_functions import Annotate_word, Run_external_taggers
from process_features import Calculate_normalized_length, Add_code_context
import logging, os, subprocess, shutil
root_logger = logging.getLogger(__name__)
from flask import Flask, flash, redirect, url_for, request, render_template, send_from_directory, session, render_template_string
from flask_cors import cross_origin
from werkzeug.utils import secure_filename
from time import sleep
from uuid import uuid4

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

#cors = CORS(app)
#app.config['CORS_HEADERS'] = 'Access-Control-Allow-Origin'

#compressed_folder_extension = ""

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
    compressed_folder_extension = ""

    if '.' in filename:
        for extension in ALLOWED_FOLDER_EXTENSIONS.keys():
            if filename.endswith('.' + extension):
                #global compressed_folder_extension
                compressed_folder_extension = extension
                result = True
                break

    return (result, compressed_folder_extension)

@app.route("/")
def landing():
    return render_template("index.html")

@app.route("/upload_file_srcml", methods=['GET', 'POST'])
@cross_origin()
def upload_file_srcml():
    if request.method == 'POST':
        print("Executing POST")
        # check if the post request has the file part
        if 'file' not in request.files:
            print("File missing")
            flash('No file part')
            return "ERROR"
        file = request.files['file']
        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file and allowed_file(file.filename):
            print("File accepted")
            # code branch when selecting a file
            filename = secure_filename(file.filename)
            # print(filename)

            unique_folder_identifier = str(uuid4())
            unique_upload_folder = app.config['UPLOAD_FOLDER'] + "-" + unique_folder_identifier
            unique_results_folder = app.config['RESULTS_FOLDER'] + "-" + unique_folder_identifier

            if not os.path.isdir(unique_upload_folder):
                os.mkdir(unique_upload_folder)

            file.save(os.path.join(unique_upload_folder, filename))

            if not os.path.isdir(unique_results_folder):
                os.mkdir(unique_results_folder)

            result_file = os.path.join(
                unique_results_folder, filename) + ".xml"
            subprocess.run(
                ["srcml", os.path.join(unique_upload_folder, filename), "-o", result_file])
            #file.close()
            os.remove(os.path.join(unique_upload_folder, filename))
            os.rmdir(unique_upload_folder)

            #response = send_from_directory(app.config['RESULTS_FOLDER'], filename + ".xml", as_attachment=True)
            #print(response)
            #os.remove(os.path.join(app.config['RESULTS_FOLDER'], filename + ".xml"))
            #return response
            #return 'SUCCESS'

            output_file = open(os.path.join(unique_results_folder, filename + ".xml"), 'r')
            output = output_file.read()
            output_file.close()
            os.remove(os.path.join(unique_results_folder, filename + ".xml"))
            os.rmdir(unique_results_folder)
            return output
            

    return render_template('upload_file.html', file_types_phrase=allowed_file_formats_phrase(list(ALLOWED_FILE_EXTENSIONS)), file_types_html=allowed_file_formats_html(list(ALLOWED_FILE_EXTENSIONS)), file_types_js=allowed_file_formats_js(list(ALLOWED_FILE_EXTENSIONS)))

@app.route("/upload_file_annotate", methods=['GET', 'POST'])
@cross_origin()
def upload_file_annotate():
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

            unique_folder_identifier = str(uuid4())
            unique_upload_folder = app.config['UPLOAD_FOLDER'] + "-" + unique_folder_identifier
            unique_results_folder = app.config['RESULTS_FOLDER'] + "-" + unique_folder_identifier

            # print(filename)

            if not os.path.isdir(unique_upload_folder):
                os.mkdir(unique_upload_folder)

            file.save(os.path.join(unique_upload_folder, filename))

            if not os.path.isdir(unique_results_folder):
                os.mkdir(unique_results_folder)

            result_file = os.path.join(
                unique_results_folder, filename) + ".xml"
            subprocess.run(
                ["srcml", os.path.join(unique_upload_folder, filename), "-o", result_file])
            #file.close()
            os.remove(os.path.join(unique_upload_folder, filename))
            os.rmdir(unique_upload_folder)

            output = subprocess.run(["./../build/bin/grabidentifiers", result_file], text=True, capture_output=True).stdout

            os.remove(result_file)
            os.rmdir(unique_results_folder)
            return output
            

    return render_template('upload_file_annotate.html', file_types_phrase=allowed_file_formats_phrase(list(ALLOWED_FILE_EXTENSIONS)), file_types_html=allowed_file_formats_html(list(ALLOWED_FILE_EXTENSIONS)), file_types_js=allowed_file_formats_js(list(ALLOWED_FILE_EXTENSIONS)))

#@app.route("/tagger_output")
#def tagger_output():
#    return output


@app.route("/upload_folder_srcml_download", methods=['GET', 'POST'])
@cross_origin()
def upload_folder_srcml_download():
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
        allowed_compressed_folder_result = allowed_compressed_folder(file.filename)
        if file and allowed_compressed_folder_result[0]:
            compressed_folder_extension = allowed_compressed_folder_result[1]
            # step 1: extract contents of compressed folder into the upload folder using shutil
            filename = secure_filename(file.filename)
            # print(filename)
            unique_folder_identifier = str(uuid4())
            unique_upload_folder = app.config['UPLOAD_FOLDER'] + "-" + unique_folder_identifier
            unique_results_folder = app.config['RESULTS_FOLDER'] + "-" + unique_folder_identifier
            unique_extract_folder = app.config['EXTRACT_FOLDER'] + "-" + unique_folder_identifier

            if not os.path.isdir(unique_upload_folder):
                os.mkdir(unique_upload_folder)

            file.save(os.path.join(unique_upload_folder, filename))

            if not os.path.isdir(unique_extract_folder):
                os.mkdir(unique_extract_folder)

            shutil.unpack_archive(os.path.join(
                unique_upload_folder, filename), unique_extract_folder)

            os.remove(os.path.join(unique_upload_folder, filename))
            os.rmdir(unique_upload_folder)

            # step 2: scan for a directory name (must be 1 directory)
            directory_list = list(os.scandir(unique_extract_folder))
            if len(directory_list) > 0:
                RESULT_FILE_NAME = "result"

                session.pop('_flashes', None)
                print("Name: " + directory_list[0].name)
                print("Path: " + directory_list[0].path)
                # step 3: use srcml with dir parameter and output to result folder
                subprocess.run(
                ["srcml", "--to-dir", unique_results_folder, unique_extract_folder])

                # step 4: delete folder contents in the extract folder
                shutil.rmtree(unique_extract_folder)

                # step 5: make a new zipped archive of the contents
                shutil.make_archive(os.path.join(unique_results_folder,RESULT_FILE_NAME),ALLOWED_FOLDER_EXTENSIONS[compressed_folder_extension],unique_results_folder,unique_extract_folder)

                # step 6: Send compressed folder and delete remaining contents
                response = send_from_directory(unique_results_folder, RESULT_FILE_NAME + "." + compressed_folder_extension, as_attachment=True)
                os.remove(os.path.join(unique_results_folder, RESULT_FILE_NAME + "." + compressed_folder_extension))
                shutil.rmtree(os.path.join(unique_results_folder, unique_extract_folder))
                os.rmdir(unique_results_folder)
                return response
            else:
                flash("ERROR: Compressed folder is empty")
                shutil.rmtree(unique_extract_folder)
                return "EMPTY_FOLDER_ERROR"

            

    return render_template('upload_folder.html', file_types_phrase=allowed_file_formats_phrase(list(ALLOWED_FOLDER_EXTENSIONS.keys())), file_types_html=allowed_file_formats_html(list(ALLOWED_FOLDER_EXTENSIONS.keys())), file_types_js=allowed_file_formats_js(list(ALLOWED_FOLDER_EXTENSIONS.keys())))

@app.route("/upload_folder_annotate", methods=['GET', 'POST'])
@cross_origin()
def upload_folder_annotate():
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
        allowed_compressed_folder_result = allowed_compressed_folder(file.filename)
        if file and allowed_compressed_folder_result[0]:
            compressed_folder_extension = allowed_compressed_folder_result[1]
            # step 1: extract contents of compressed folder into the upload folder using shutil
            filename = secure_filename(file.filename)
            # print(filename)
            unique_folder_identifier = str(uuid4())
            unique_upload_folder = app.config['UPLOAD_FOLDER'] + "-" + unique_folder_identifier
            #unique_results_folder = app.config['RESULTS_FOLDER'] + "-" + unique_folder_identifier
            unique_extract_folder = app.config['EXTRACT_FOLDER'] + "-" + unique_folder_identifier

            if not os.path.isdir(unique_upload_folder):
                os.mkdir(unique_upload_folder)

            file.save(os.path.join(unique_upload_folder, filename))

            if not os.path.isdir(unique_extract_folder):
                os.mkdir(unique_extract_folder)

            shutil.unpack_archive(os.path.join(
                unique_upload_folder, filename), unique_extract_folder)

            os.remove(os.path.join(unique_upload_folder, filename))
            os.rmdir(unique_upload_folder)

            # step 2: scan for a directory name (must be 1 directory)
            directory_list = list(os.scandir(unique_extract_folder))
            if len(directory_list) > 0:
                RESULT_FILE_NAME = "result" + "-" + unique_folder_identifier + ".xml"

                session.pop('_flashes', None)
                print("Name: " + directory_list[0].name)
                print("Path: " + directory_list[0].path)
                # step 3: use srcml with dir parameter and output to result folder
                subprocess.run(
                ["srcml", unique_extract_folder, "-o", RESULT_FILE_NAME])

                # step 4: delete folder contents in the extract folder
                shutil.rmtree(unique_extract_folder)

                # step 5: make a new zipped archive of the contents
                output = subprocess.run(["./../build/bin/grabidentifiers", RESULT_FILE_NAME], text=True, capture_output=True).stdout
                os.remove(RESULT_FILE_NAME)

                # step 6: Send compressed folder and delete remaining contents
                #response = send_from_directory(unique_results_folder, RESULT_FILE_NAME + "." + compressed_folder_extension, as_attachment=True)
                #os.remove(os.path.join(unique_results_folder, RESULT_FILE_NAME + "." + compressed_folder_extension))
                #shutil.rmtree(os.path.join(unique_results_folder, unique_extract_folder))
                #os.rmdir(unique_results_folder)
                return output
            else:
                flash("ERROR: Compressed folder is empty")
                shutil.rmtree(unique_extract_folder)
                return "EMPTY_FOLDER_ERROR"

    return render_template('upload_folder.html', file_types_phrase=allowed_file_formats_phrase(list(ALLOWED_FOLDER_EXTENSIONS.keys())), file_types_html=allowed_file_formats_html(list(ALLOWED_FOLDER_EXTENSIONS.keys())), file_types_js=allowed_file_formats_js(list(ALLOWED_FOLDER_EXTENSIONS.keys())))

@app.route("/upload_folder_annotate_download", methods=['GET', 'POST'])
@cross_origin()
def upload_folder_annotate_download():
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
        allowed_compressed_folder_result = allowed_compressed_folder(file.filename)
        if file and allowed_compressed_folder_result[0]:
            compressed_folder_extension = allowed_compressed_folder_result[1]
            # step 1: extract contents of compressed folder into the upload folder using shutil
            filename = secure_filename(file.filename)
            # print(filename)
            unique_folder_identifier = str(uuid4())
            unique_upload_folder = app.config['UPLOAD_FOLDER'] + "-" + unique_folder_identifier
            unique_results_folder = app.config['RESULTS_FOLDER'] + "-" + unique_folder_identifier
            unique_extract_folder = app.config['EXTRACT_FOLDER'] + "-" + unique_folder_identifier

            if not os.path.isdir(unique_upload_folder):
                os.mkdir(unique_upload_folder)

            file.save(os.path.join(unique_upload_folder, filename))

            if not os.path.isdir(unique_extract_folder):
                os.mkdir(unique_extract_folder)

            shutil.unpack_archive(os.path.join(
                unique_upload_folder, filename), unique_extract_folder)

            os.remove(os.path.join(unique_upload_folder, filename))
            os.rmdir(unique_upload_folder)

            # step 2: scan for a directory name (must be 1 directory)
            directory_list = list(os.scandir(unique_extract_folder))
            if len(directory_list) > 0:
                RESULT_FILE_NAME = "result" + "-" + unique_folder_identifier + ".xml"

                session.pop('_flashes', None)
                print("Name: " + directory_list[0].name)
                print("Path: " + directory_list[0].path)
                # step 3: use srcml with output parameter and output to result file
                subprocess.run(
                ["srcml", unique_extract_folder, "-o", RESULT_FILE_NAME])

                # step 4: delete folder contents in the extract folder
                shutil.rmtree(unique_extract_folder)

                # step 5: annotate file and remove srcml
                output = subprocess.run(["./../build/bin/grabidentifiers", RESULT_FILE_NAME], text=True, capture_output=True).stdout
                
                # annotate srcml file
                result_file_writer = open(RESULT_FILE_NAME, "w")
                result_file_writer.write("<" + output.split("<", 1)[1])

                ANNOTATED_FOLDER_NAME = "annotated" + "-" + unique_folder_identifier

                # remove srcml tags and restore to directory structure
                subprocess.run(["srcml", RESULT_FILE_NAME, "--to-dir", ANNOTATED_FOLDER_NAME])
                os.remove(RESULT_FILE_NAME)

                # re-add srcml while keeping directory structure, delete annotated folder
                subprocess.run(["srcml", ANNOTATED_FOLDER_NAME, "--to-dir", unique_results_folder])
                shutil.rmtree(ANNOTATED_FOLDER_NAME)

                #create compressed folder
                shutil.make_archive(os.path.join(unique_results_folder,ANNOTATED_FOLDER_NAME,unique_extract_folder),ALLOWED_FOLDER_EXTENSIONS[compressed_folder_extension],os.path.join(unique_results_folder,ANNOTATED_FOLDER_NAME),unique_extract_folder)


                # step 6: Send compressed folder and delete remaining contents
                #print("Zip path: " + str(os.path.isfile(os.path.join(unique_results_folder,ANNOTATED_FOLDER_NAME,unique_extract_folder + "." + compressed_folder_extension))))
                response = send_from_directory(os.path.join(unique_results_folder,ANNOTATED_FOLDER_NAME), unique_extract_folder + "." + compressed_folder_extension, as_attachment=True)
                shutil.rmtree(unique_results_folder)
                #os.remove(os.path.join(unique_results_folder, RESULT_FILE_NAME + "." + compressed_folder_extension))
                #shutil.rmtree(os.path.join(unique_results_folder, unique_extract_folder))
                #os.rmdir(unique_results_folder)
                return response
            else:
                flash("ERROR: Compressed folder is empty")
                shutil.rmtree(unique_extract_folder)
                return "EMPTY_FOLDER_ERROR"

    return render_template('upload_folder.html', file_types_phrase=allowed_file_formats_phrase(list(ALLOWED_FOLDER_EXTENSIONS.keys())), file_types_html=allowed_file_formats_html(list(ALLOWED_FOLDER_EXTENSIONS.keys())), file_types_js=allowed_file_formats_js(list(ALLOWED_FOLDER_EXTENSIONS.keys())))

@app.route("/upload_folder_srcml", methods=['GET', 'POST'])
@cross_origin()
def upload_folder_srcml():
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
        allowed_compressed_folder_result = allowed_compressed_folder(file.filename)
        if file and allowed_compressed_folder_result[0]:
            compressed_folder_extension = allowed_compressed_folder_result[1]
            # step 1: extract contents of compressed folder into the upload folder using shutil
            filename = secure_filename(file.filename)
            # print(filename)
            unique_folder_identifier = str(uuid4())
            unique_upload_folder = app.config['UPLOAD_FOLDER'] + "-" + unique_folder_identifier
            #unique_results_folder = app.config['RESULTS_FOLDER'] + "-" + unique_folder_identifier
            unique_extract_folder = app.config['EXTRACT_FOLDER'] + "-" + unique_folder_identifier

            if not os.path.isdir(unique_upload_folder):
                os.mkdir(unique_upload_folder)

            file.save(os.path.join(unique_upload_folder, filename))

            if not os.path.isdir(unique_extract_folder):
                os.mkdir(unique_extract_folder)

            shutil.unpack_archive(os.path.join(
                unique_upload_folder, filename), unique_extract_folder)

            os.remove(os.path.join(unique_upload_folder, filename))
            os.rmdir(unique_upload_folder)

            # step 2: scan for a directory name (must be 1 directory)
            directory_list = list(os.scandir(unique_extract_folder))
            if len(directory_list) > 0:
                #RESULT_FILE_NAME = "result" + "-" + unique_folder_identifier + ".xml"

                session.pop('_flashes', None)
                print("Name: " + directory_list[0].name)
                print("Path: " + directory_list[0].path)
                # step 3: use srcml with dir parameter and output to result folder
                output = subprocess.run(
                ["srcml", unique_extract_folder], text=True, capture_output=True).stdout

                # step 4: delete folder contents in the extract folder
                shutil.rmtree(unique_extract_folder)

                # step 5: make a new zipped archive of the contents
                #output = subprocess.run(["./../build/bin/grabidentifiers", RESULT_FILE_NAME], text=True, capture_output=True).stdout
                #os.remove(RESULT_FILE_NAME)

                # step 6: Send compressed folder and delete remaining contents
                #response = send_from_directory(unique_results_folder, RESULT_FILE_NAME + "." + compressed_folder_extension, as_attachment=True)
                #os.remove(os.path.join(unique_results_folder, RESULT_FILE_NAME + "." + compressed_folder_extension))
                #shutil.rmtree(os.path.join(unique_results_folder, unique_extract_folder))
                #os.rmdir(unique_results_folder)
                return output
            else:
                flash("ERROR: Compressed folder is empty")
                shutil.rmtree(unique_extract_folder)
                return "EMPTY_FOLDER_ERROR"

            

    return render_template('upload_folder.html', file_types_phrase=allowed_file_formats_phrase(list(ALLOWED_FOLDER_EXTENSIONS.keys())), file_types_html=allowed_file_formats_html(list(ALLOWED_FOLDER_EXTENSIONS.keys())), file_types_js=allowed_file_formats_js(list(ALLOWED_FOLDER_EXTENSIONS.keys())))

#@app.route("/upload_folder", methods=['POST'])
#@cross_origin()
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
        allowed_compressed_folder_result = allowed_compressed_folder(file.filename)
        if file and allowed_compressed_folder_result[0]:
            compressed_folder_extension = allowed_compressed_folder_result[1]
            # step 1: extract contents of compressed folder into the upload folder using shutil
            filename = secure_filename(file.filename)
            # print(filename)
            unique_folder_identifier = str(uuid4())
            unique_upload_folder = app.config['UPLOAD_FOLDER'] + "-" + unique_folder_identifier
            #unique_results_folder = app.config['RESULTS_FOLDER'] + "-" + unique_folder_identifier
            unique_extract_folder = app.config['EXTRACT_FOLDER'] + "-" + unique_folder_identifier

            if not os.path.isdir(unique_upload_folder):
                os.mkdir(unique_upload_folder)

            file.save(os.path.join(unique_upload_folder, filename))


            # step 6: Send compressed folder and delete remaining contents
            #response = send_from_directory(unique_results_folder, RESULT_FILE_NAME + "." + compressed_folder_extension, as_attachment=True)
            #os.remove(os.path.join(unique_results_folder, RESULT_FILE_NAME + "." + compressed_folder_extension))
            #shutil.rmtree(os.path.join(unique_results_folder, unique_extract_folder))
            #os.rmdir(unique_results_folder)
            return unique_folder_identifier

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
