{
    "name": "Forthcoming Books",
    "summary": """Forthcoming Books""",
    "description": """Forthcoming Books""",

    "category": "Tools/Tools",
    "version": "16.0.0.1",
    "sequence": -10,

    "author": "Metamorphosis Limited",
    "co-author": "Jony Ghosh",
    "license": "AGPL-3",
    "website": "https://metamorphosis.com.bd/",

    "depends": ['base', 'web', 'website_sale', 'website', 'meta_book_info', 'meta_request_button'],
    "data": [
        "views/forthcoming_template.xml",
        "views/product_template_view.xml",
    ],
    'assets': {
        'web.assets_frontend': [
            '/meta_forthcoming_books/static/src/css/design.css',
            '/meta_forthcoming_books/static/src/js/related_prods.js',
        ],
    },
    "application": True,
    "installable": True,
    "auto_install": False,
}