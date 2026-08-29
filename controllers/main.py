from odoo import http
from odoo.http import request
import base64
import logging
import re

_logger = logging.getLogger(__name__)

# Master document field list  (form_key, model_field, filename_field, label, required)
DOC_FIELDS = [
    ('photo',                  'photo',                  'photo_filename',                   'Photo',                              True),
    ('aadhaar_doc',            'aadhaar_doc',            'aadhaar_doc_filename',             'Aadhaar Document',                   False),
    ('signed_nda',             'signed_nda',             'signed_nda_filename',              'Signed NDA',                         True),
    ('signed_offer_letter',    'signed_offer_letter',    'signed_offer_letter_filename',     'Signed Offer Letter',                True),
    ('pan_card',               'pan_card',               'pan_card_filename',                'PAN Card',                           True),
    ('sslc_certificate',       'sslc_certificate',       'sslc_certificate_filename',        'SSLC Certificate',                   False),
    ('plus_two_certificate',   'plus_two_certificate',   'plus_two_certificate_filename',    'Plus Two Certificate',               False),
    ('degree_certificate',     'degree_certificate',     'degree_certificate_filename',      'Degree Certificate',                 False),
    ('other_edu_certificates', 'other_edu_certificates', 'other_edu_certificates_filename',  'Other Edu Certificates (PG/Diploma)', False),
    ('exp_relieving_letter',   'exp_relieving_letter',   'exp_relieving_letter_filename',    'Experience / Relieving Letter',      False),
    ('bank_statements',        'bank_statements',        'bank_statements_filename',         'Bank Statements (Last 6 Months)',    False),
    ('payslips',               'payslips',               'payslips_filename',                'Payslips (Last 3 Months)',           False),
    ('resume',                 'resume',                 'resume_filename',                  'Resume (with 2 Reference Contacts)', False),
]


def _save_uploads(vals):
    for fk, vk, fnk, _l, _r in DOC_FIELDS:
        f = request.httprequest.files.get(fk)
        if f and f.filename:
            vals[vk] = base64.b64encode(f.read())
            vals[fnk] = f.filename


def _doc_status(app):
    return [{
        'field':    vk,
        'label':    label,
        'required': req,
        'uploaded': bool(getattr(app, vk, False)),
        'filename': getattr(app, fnk, '') or '',
    } for _fk, vk, fnk, label, req in DOC_FIELDS]


class StaffJoiningPortalController(http.Controller):

    # ── /join  New application ─────────────────────────────────────────────
    @http.route('/join', type='http', auth='public', website=True, methods=['GET'])
    def joining_form(self, **kw):
        return request.render('staff_joining_19.portal_joining_form', {
            'success': False, 'error': None, 'form_data': {},
            'job_positions': request.env['hr.job'].sudo().search([], order='name asc'),
        })

    @http.route('/join/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def joining_submit(self, **post):
        fd = {k: v for k, v in post.items() if not k.startswith('csrf')}
        jobs = request.env['hr.job'].sudo().search([], order='name asc')

        def err(msg):
            return request.render('staff_joining_19.portal_joining_form', {
                'success': False, 'error': msg, 'form_data': fd, 'job_positions': jobs,
            })

        for f, l in [('full_name','Full Name'),('email','Email ID'),
                     ('phone','Phone Number'),('address','Address'),('aadhaar_number','Aadhaar Number')]:
            if not post.get(f,'').strip():
                return err(f'{l} is required.')

        aadhaar = post.get('aadhaar_number','').replace(' ','')
        if not re.match(r'^\d{12}$', aadhaar):
            return err('Aadhaar number must be exactly 12 digits.')

        phone = post.get('phone','').strip()
        if not re.match(r'^[6-9]\d{9}$', phone):
            return err('Phone must be a valid 10-digit Indian mobile number.')

        vals = {
            'full_name': post.get('full_name','').strip(),
            'email': post.get('email','').strip(),
            'phone': phone,
            'address': post.get('address','').strip(),
            'location': post.get('location','').strip(),
            'aadhaar_number': aadhaar,
            'bank_account_name': post.get('bank_account_name','').strip(),
            'bank_account_number': post.get('bank_account_number','').strip(),
            'bank_name': post.get('bank_name','').strip(),
            'bank_ifsc': post.get('bank_ifsc','').strip(),
            'bank_branch': post.get('bank_branch','').strip(),
        }
        jp = post.get('job_position_id','').strip()
        if jp and jp.isdigit():
            vals['job_position_id'] = int(jp)

        _save_uploads(vals)

        try:
            app = request.env['staff.joining.application'].sudo().create(vals)
            return request.render('staff_joining_19.portal_joining_form', {
                'success': True, 'application_ref': app.name,
                'form_data': {}, 'error': None, 'job_positions': jobs,
            })
        except Exception:
            _logger.exception('Error creating joining application')
            return err('An error occurred. Please try again.')

    # ── /join/update  Phone lookup ─────────────────────────────────────────
    @http.route('/join/update', type='http', auth='public', website=True, methods=['GET'])
    def update_lookup(self, **kw):
        return request.render('staff_joining_19.portal_update_lookup', {'error': None})

    @http.route('/join/update/find', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def update_find(self, **post):
        phone = post.get('phone','').strip()
        if not phone:
            return request.render('staff_joining_19.portal_update_lookup',
                                  {'error': 'Please enter your registered phone number.'})

        app = request.env['staff.joining.application'].sudo().search(
            [('phone','=',phone), ('state','not in',['approved','rejected'])],
            limit=1, order='create_date desc')

        if not app:
            return request.render('staff_joining_19.portal_update_lookup',
                {'error': 'No active application found for this phone number. '
                          'Approved or rejected applications cannot be updated.'})

        return request.render('staff_joining_19.portal_update_form', {
            'app': app, 'doc_status': _doc_status(app), 'success': False, 'error': None,
        })

    @http.route('/join/update/submit', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def update_submit(self, **post):
        phone    = post.get('phone','').strip()
        app_name = post.get('app_name','').strip()

        app = request.env['staff.joining.application'].sudo().search(
            [('phone','=',phone),('name','=',app_name),('state','not in',['approved','rejected'])],
            limit=1)

        if not app:
            return request.render('staff_joining_19.portal_update_lookup',
                                  {'error': 'Session expired. Please search again.'})

        vals = {}
        for field in ['full_name','email','location','address',
                      'bank_account_name','bank_account_number',
                      'bank_name','bank_ifsc','bank_branch']:
            v = post.get(field,'').strip()
            if v:
                vals[field] = v
        _save_uploads(vals)

        if not vals:
            return request.render('staff_joining_19.portal_update_form', {
                'app': app, 'doc_status': _doc_status(app), 'success': False,
                'error': 'No files selected. Please choose at least one document.',
            })

        try:
            app.sudo().write(vals)
            return request.render('staff_joining_19.portal_update_form', {
                'app': app, 'doc_status': _doc_status(app), 'success': True, 'error': None,
            })
        except Exception:
            _logger.exception('Error updating documents')
            return request.render('staff_joining_19.portal_update_form', {
                'app': app, 'doc_status': _doc_status(app), 'success': False,
                'error': 'An error occurred. Please try again.',
            })
