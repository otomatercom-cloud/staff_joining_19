from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
import re


class StaffJoiningApplication(models.Model):
    _name = 'staff.joining.application'
    _description = 'Staff Joining Application'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'create_date desc'
    _rec_name = 'full_name'

    # ── Reference ──────────────────────────────────────────────────────────
    name = fields.Char(string='Application Reference', readonly=True, default='New', copy=False)

    # ── Personal ───────────────────────────────────────────────────────────
    full_name    = fields.Char(string='Full Name',     required=True, tracking=True)
    email        = fields.Char(string='Email ID',      required=True, tracking=True)
    phone        = fields.Char(string='Phone Number',  required=True, tracking=True)
    address      = fields.Text(string='Address',       required=True)
    location     = fields.Char(string='Location / City')
    job_position_id = fields.Many2one('hr.job', string='Designation', tracking=True)
    photo        = fields.Binary(string='Photo', attachment=True)
    photo_filename = fields.Char(string='Photo Filename')

    # ── Identity ───────────────────────────────────────────────────────────
    aadhaar_number   = fields.Char(string='Aadhaar Number', required=True, tracking=True)
    aadhaar_doc      = fields.Binary(string='Aadhaar Document', attachment=True)
    aadhaar_doc_filename = fields.Char(string='Aadhaar Filename')

    # ── Joining Documents (Required) ───────────────────────────────────────
    signed_nda              = fields.Binary(string='Signed NDA', attachment=True)
    signed_nda_filename     = fields.Char(string='Signed NDA Filename')
    signed_offer_letter     = fields.Binary(string='Signed Offer Letter', attachment=True)
    signed_offer_letter_filename = fields.Char(string='Signed Offer Letter Filename')
    pan_card                = fields.Binary(string='PAN Card', attachment=True)
    pan_card_filename       = fields.Char(string='PAN Card Filename')

    # ── Educational Certificates ───────────────────────────────────────────
    sslc_certificate        = fields.Binary(string='SSLC Certificate', attachment=True)
    sslc_certificate_filename = fields.Char(string='SSLC Certificate Filename')
    plus_two_certificate    = fields.Binary(string='Plus Two Certificate', attachment=True)
    plus_two_certificate_filename = fields.Char(string='Plus Two Certificate Filename')
    degree_certificate      = fields.Binary(string='Degree Certificate', attachment=True)
    degree_certificate_filename = fields.Char(string='Degree Certificate Filename')
    other_edu_certificates  = fields.Binary(string='Other Edu Certificates (PG/Diploma)', attachment=True)
    other_edu_certificates_filename = fields.Char(string='Other Edu Certificates Filename')

    # ── Experience & Financial ─────────────────────────────────────────────
    exp_relieving_letter    = fields.Binary(string='Experience / Relieving Letter', attachment=True)
    exp_relieving_letter_filename = fields.Char(string='Exp/Relieving Letter Filename')
    bank_statements         = fields.Binary(string='Bank Statements (Last 6 Months)', attachment=True)
    bank_statements_filename = fields.Char(string='Bank Statements Filename')
    payslips                = fields.Binary(string='Payslips (Last 3 Months)', attachment=True)
    payslips_filename       = fields.Char(string='Payslips Filename')
    resume                  = fields.Binary(string='Resume with 2 Reference Contacts', attachment=True)
    resume_filename         = fields.Char(string='Resume Filename')

    # ── Bank Details ───────────────────────────────────────────────────────
    bank_account_name   = fields.Char(string='Account Holder Name')
    bank_account_number = fields.Char(string='Account Number')
    bank_name           = fields.Char(string='Bank Name')
    bank_ifsc           = fields.Char(string='IFSC Code')
    bank_branch         = fields.Char(string='Branch')

    # ── Workflow ───────────────────────────────────────────────────────────
    state = fields.Selection([
        ('draft',        'Submitted'),
        ('under_review', 'Under Review'),
        ('approved',     'Approved'),
        ('rejected',     'Rejected'),
    ], string='Status', default='draft', tracking=True)

    employee_id      = fields.Many2one('hr.employee', string='Created Employee', readonly=True)
    user_id          = fields.Many2one('res.users', string='Internal User', readonly=True)
    rejection_reason = fields.Text(string='Rejection Reason')
    reviewed_by      = fields.Many2one('res.users', string='Reviewed By', readonly=True)
    approved_date    = fields.Datetime(string='Approved On', readonly=True)

    # ── Constraints ────────────────────────────────────────────────────────
    @api.constrains('email')
    def _check_email(self):
        for rec in self:
            if rec.email and not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', rec.email):
                raise ValidationError(_('Please enter a valid Email ID.'))

    @api.constrains('phone')
    def _check_phone(self):
        for rec in self:
            if rec.phone and not re.match(r'^[6-9]\d{9}$', rec.phone.strip()):
                raise ValidationError(_('Phone must be a valid 10-digit Indian mobile number.'))

    @api.constrains('aadhaar_number')
    def _check_aadhaar(self):
        for rec in self:
            if rec.aadhaar_number and not re.match(r'^\d{12}$', rec.aadhaar_number.replace(' ', '')):
                raise ValidationError(_('Aadhaar number must be exactly 12 digits.'))

    # ── ORM ────────────────────────────────────────────────────────────────
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('staff.joining.application') or 'New'
        return super().create(vals_list)

    # ── Actions ────────────────────────────────────────────────────────────
    def action_set_under_review(self):
        self.ensure_one()
        self.write({'state': 'under_review'})

    def action_reject(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': _('Rejection Reason'),
            'res_model': 'staff.joining.reject.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_application_id': self.id},
        }

    def action_approve(self):
        self.ensure_one()
        if self.state != 'under_review':
            raise UserError(_('Application must be Under Review before approval.'))
        return {
            'type': 'ir.actions.act_window',
            'name': _('Create Employee Login'),
            'res_model': 'staff.joining.approve.wizard',
            'view_mode': 'form',
            'target': 'new',
            'context': {'default_application_id': self.id},
        }

    def _do_approve(self, login, password):
        self.ensure_one()
        existing = self.env['res.users'].sudo().search([('login', '=', login)], limit=1)
        if existing:
            raise UserError(_('Login "%s" is already taken.') % login)

        group_internal = self.env.ref('base.group_user')
        user = self.env['res.users'].sudo().create({
            'name': self.full_name, 'login': login, 'password': password,
            'email': self.email, 'group_ids': [(6, 0, [group_internal.id])],
        })

        employee_vals = {
            'name': self.full_name, 'work_email': self.email,
            'mobile_phone': self.phone, 'user_id': user.id,
        }
        if self.photo:          employee_vals['image_1920'] = self.photo
        if self.location:       employee_vals['work_location_name'] = self.location
        if self.job_position_id: employee_vals['job_id'] = self.job_position_id.id

        employee = self.env['hr.employee'].sudo().create(employee_vals)

        if self.bank_account_number and self.bank_name:
            self.env['res.partner.bank'].sudo().create({
                'acc_number': self.bank_account_number,
                'bank_id': self._get_or_create_bank(self.bank_name, self.bank_ifsc),
                'partner_id': user.partner_id.id,
            })

        self.write({
            'state': 'approved', 'employee_id': employee.id,
            'user_id': user.id, 'reviewed_by': self.env.user.id,
            'approved_date': fields.Datetime.now(),
        })
        return True

    def _get_or_create_bank(self, bank_name, ifsc=None):
        bank = self.env['res.bank'].sudo().search([('name', 'ilike', bank_name)], limit=1)
        if not bank:
            bank = self.env['res.bank'].sudo().create({'name': bank_name, 'bic': ifsc or ''})
        return bank.id

    def action_open_employee(self):
        self.ensure_one()
        if not self.employee_id:
            return {}
        return {
            'type': 'ir.actions.act_window', 'name': _('Employee'),
            'res_model': 'hr.employee', 'view_mode': 'form', 'res_id': self.employee_id.id,
        }
