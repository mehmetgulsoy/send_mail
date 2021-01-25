import os
from flask import Flask, request, jsonify
from werkzeug.utils import secure_filename
from werkzeug.http import HTTP_STATUS_CODES
import smtplib
from string import Template
from email.message import EmailMessage
from flask_cors import CORS


ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg',
                      'jpeg', 'gif', 'doc', 'docx', 'xls', 'xlsx', 'pdf"'}

app = Flask(__name__)
CORS(app)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def read_template(filename):
    """
    Returns a Template object comprising the contents of the 
    file specified by filename.
    """

    with open(filename, 'r', encoding='utf-8') as template_file:
        template_file_content = template_file.read()
    return Template(template_file_content)


def error_response(status_code, message=None):
    payload = {'error': HTTP_STATUS_CODES.get(status_code, 'Unknown error')}
    if message:
        payload['message'] = message
    response = jsonify(payload)
    response.status_code = status_code
    return response


def bad_request(message):
    return error_response(400, message)


@app.route('/test_yandex_send', methods=['GET', 'POST'])
def send():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return bad_request('No file part')
        file = request.files['file']
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            return bad_request('No selected file')
        if not allowed_file(file.filename):
            return bad_request(f'Not allowed extensions! Allowed: {" ,".join(ALLOWED_EXTENSIONS)}')
        if file and allowed_file(file.filename):
            names, emails = ('mehmet',), ('m.mehmetgulsoy@gmail.com',)
            message_template = read_template('message.txt')

            # set up the SMTP server
            s = smtplib.SMTP_SSL(host='smtp.yandex.com.tr', port=465)
            s.login('abc@yandex.com.tr', 'XXXXX')

            # For each contact, send the email:
            for name, email in zip(names, emails):
                # create a message
                msg = EmailMessage()

                # add in the actual person name to the message template
                message = message_template.substitute(PERSON_NAME=name.title())

                # setup the parameters of the message
                msg['From'] = 'mehmet.gulsoy@kitayazilim.com'
                msg['To'] = email
                msg['Subject'] = "This is TEST"

                msg.set_content(message)
                maintype, subtype = file.mimetype.split('/', 1)
                msg.add_attachment(file.stream.read(),
                                   maintype=maintype,
                                   subtype=subtype,
                                   filename=file.filename)

                # send the message via the server set up earlier.
                s.send_message(msg)
                del msg

            # Terminate the SMTP session and close the connection
            s.quit()
        return 'E-mail send', 200
    return f'''
    <!doctype html>
    <title>Upload new File</title>
    <h1>Upload new File</h1>
    <form method=post enctype=multipart/form-data>
      <input type=file name=file   accept=".{" ,.".join(ALLOWED_EXTENSIONS)}">
      <input type=submit value=Upload>
    </form>
    '''


company = {
    'ronesansteknik': {
        'mail': 'info@ronesansteknik.com.tr',
        'pass': 'ronesansteknik123456'
    },
    'optimalmakina': {
        'mail': 'info@optimalmakina.com.tr'
    },

}


def get_company(comp):
    return company.get(comp, None)


@app.route('/api_send_mail_yandex', methods=['POST'])
def public_yandex_send():
    company = get_company(request.form.get('company'))
    if not company:
        return bad_request('Firma bilgisi gerekli')

    if 'message' not in request.form:
        return bad_request('Mesajınızı giriniz')

    if 'subject' not in request.form:
        return bad_request('Konu giriniz')

    msg = EmailMessage()
    msg['From'] = company.get('mail')
    msg['To'] = request.form.get('to', company.get('mail'))
    msg['Subject'] = request.form.get('subject')
    msg.set_content(request.form.get('message'))

    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '':
            if not allowed_file(file.filename):
                return bad_request(f'Not allowed extensions! Allowed: {" ,".join(ALLOWED_EXTENSIONS)}')

            maintype, subtype = file.mimetype.split('/', 1)
            msg.add_attachment(file.stream.read(),
                               maintype=maintype,
                               subtype=subtype,
                               filename=file.filename)

    s = smtplib.SMTP_SSL(host='smtp.yandex.com.tr', port=465)
    s.login(company.get('mail'), company.get('pass'))
    s.send_message(msg)
    del msg
    s.quit()
    return 'E-mail send', 200


@app.route('/api_send_mail', methods=['POST'])
def public_send():
    company = get_company(request.form.get('company'))
    if not company:
        return bad_request('Firma bilgisi gerekli')

    if 'message' not in request.form:
        return bad_request('Mesajınızı giriniz')

    if 'subject' not in request.form:
        return bad_request('Konu giriniz')

    msg = EmailMessage()
    msg['From'] = company.get('mail')
    msg['To'] = request.form.get('to', company.get('mail'))
    msg['Subject'] = request.form.get('subject')
    msg.set_content(request.form.get('message'))

    if 'file' in request.files:
        file = request.files['file']
        if file and file.filename != '':
            if not allowed_file(file.filename):
                return bad_request(f'Not allowed extensions! Allowed: {" ,".join(ALLOWED_EXTENSIONS)}')

            maintype, subtype = file.mimetype.split('/', 1)
            msg.add_attachment(file.stream.read(),
                               maintype=maintype,
                               subtype=subtype,
                               filename=file.filename)

    #s = smtplib.SMTP_SSL(host='smtp.yandex.com.tr', port=465)
    s = smtplib.SMTP(host='localhost', port=25)
    s.send_message(msg)
    del msg
    s.quit()
    return 'E-mail send', 200


if __name__ == "__main__":
    app.run(host='0.0.0.0', port='8085')


# https://docs.python.org/3/library/email.examples.html
