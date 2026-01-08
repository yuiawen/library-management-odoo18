{
    'name': 'Library Management',
    'version': '18.0.1.0.0',
    'category': 'Productivity',
    'summary': 'Manage library books, members and borrowing records',
    'description': """
        Library Management System
        =========================
        * Manage books catalog
        * Track book borrowing
        * Member management
        * Automated return notifications
    """,
    'author': 'Your Company',
    'website': 'https://www.yourcompany.com',
    'license': 'LGPL-3',
    'depends': ['base', 'mail'],
    'data': [
        'security/library_security.xml',
        'security/ir.model.access.csv',
        'data/library_data.xml',

        # Borrowing dulu, supaya action_library_borrowing sudah ada
        'views/library_borrowing_views.xml',

        # Baru views yang memanggil action tersebut
        'views/library_book_views.xml',
        'views/library_member_views.xml',

        # Menu yang pakai action_library_borrowing
        'views/library_menu.xml',

        'reports/library_borrowing_report.xml',
    ],

    'demo': [
        'demo/library_demo.xml',
    ],
    'installable': True,
    'application': True,
    'auto_install': False,
}