from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class StaffJoiningApproveWizard(models.TransientModel):
    _name = 'staff.joining.approve.wizard'
    _description = 'Staff Joining Approval Wizard - Create Login'

    application_id = fields.Many2one(
        'staff.joining.application',
        string='Application',
        required=True,
        readonly=True,
    )
    applicant_name = fields.Char(
        related='application_id.full_name',
        string='Applicant',
        readonly=True,
    )
    applicant_email = fields.Char(
        related='application_id.email',
        string='Email',
        readonly=True,
    )
    login = fields.Char(
        string='Login ID',
        required=True,
        help='The username the employee will use to log in.',
    )
    password = fields.Char(
        string='Password',
        required=True,
    )
    confirm_password = fields.Char(
        string='Confirm Password',
        required=True,
    )

    @api.onchange('application_id')
    def _onchange_application(self):
        if self.application_id and self.application_id.email:
            self.login = self.application_id.email

    @api.constrains('password', 'confirm_password')
    def _check_passwords(self):
        for rec in self:
            if rec.password != rec.confirm_password:
                raise ValidationError(_('Password and Confirm Password do not match.'))
            if len(rec.password) < 6:
                raise ValidationError(_('Password must be at least 6 characters long.'))

    def action_confirm_approve(self):
        self.ensure_one()
        if self.password != self.confirm_password:
            raise ValidationError(_('Passwords do not match.'))
        self.application_id._do_approve(self.login, self.password)
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'title': _('Approved!'),
                'message': _('Employee and login created successfully for %s.') % self.application_id.full_name,
                'type': 'success',
                'sticky': False,
                'next': {'type': 'ir.actions.client', 'tag': 'reload'},
            },
        }


class StaffJoiningRejectWizard(models.TransientModel):
    _name = 'staff.joining.reject.wizard'
    _description = 'Staff Joining Rejection Wizard'

    application_id = fields.Many2one(
        'staff.joining.application',
        string='Application',
        required=True,
        readonly=True,
    )
    rejection_reason = fields.Text(
        string='Rejection Reason',
        required=True,
    )

    def action_confirm_reject(self):
        self.ensure_one()
        self.application_id.write({
            'state': 'rejected',
            'rejection_reason': self.rejection_reason,
            'reviewed_by': self.env.user.id,
        })
        return {'type': 'ir.actions.act_window_close'}
