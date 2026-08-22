{
    'name': 'Staff Joining Portal',
    'version': '19.0.1.0.0',
    'summary': 'Staff Joining Application Portal with Approval Workflow',
    'description': """
        Staff Joining Portal Module for Odoo 19
        ========================================
        - Public portal form for staff joining applications
        - Fields: Full Name, Email, Phone, Address, Location, Photo, Aadhaar, Bank Details
        - Backend approval workflow for Admin/HR
        - Auto employee and internal user creation on approval
    """,
    'category': 'Human Resources',
    'author': 'Custom',
    'depends': ['base', 'hr', 'portal', 'mail', 'web', 'website'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/sequence.xml',
        'views/joining_application_views.xml',
        'views/portal_templates.xml',
        'views/menu_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'staff_joining_19/static/src/css/portal.css',
            'staff_joining_19/static/src/js/portal.js',
        ],
    },
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}
