
{
    'name': "Request Book feature",
    'summary': """
        """,
    'description': """
        Add request button if there are no stock for that product
    """,

    'author': 'Metamorphosis',
    'co-author': 'Rakin',
    'website': 'https://metamorphosis.com',
    'license': 'AGPL-3',
    # Categories can be used to filter modules in modules listing
    # for the full list
    'category': 'eCommerce',
    'version': '16.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'mail',
        'website',
        'website_sale',
        'website_payment',
        'product',
        'web',
        'payment',
        'meta_book_info',
        'meta_sms_mod',
        ],
    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'views/website.xml',
        'views/product_requests.xml',
        'views/product_template.xml',
        'views/sms.xml',
        'views/email_template.xml'
    ],
    
    'assets': {
        'web.assets_frontend': [
            '/meta_request_button/static/src/js/sweetalert.min.js',
            '/meta_request_button/static/src/js/website_product_request.js',
        ],
    },
    
    "installable": True,
    'auto_install': False,
    'application': True,
}
