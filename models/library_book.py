from odoo import models, fields, api
from odoo.exceptions import ValidationError


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char('Title', required=True, tracking=True)
    isbn = fields.Char('ISBN', copy=False, tracking=True)
    author = fields.Char('Author', required=True, tracking=True)
    publisher = fields.Char('Publisher')
    publication_date = fields.Date('Publication Date')
    category = fields.Selection([
        ('fiction', 'Fiction'),
        ('non_fiction', 'Non-Fiction'),
        ('science', 'Science'),
        ('technology', 'Technology'),
        ('history', 'History'),
        ('other', 'Other')
    ], string='Category', default='other', required=True)
    
    pages = fields.Integer('Number of Pages')
    copies_available = fields.Integer('Available Copies', compute='_compute_copies_available', store=True)
    total_copies = fields.Integer('Total Copies', default=1, required=True)
    
    state = fields.Selection([
        ('available', 'Available'),
        ('borrowed', 'All Borrowed'),
        ('maintenance', 'Under Maintenance')
    ], string='Status', default='available', tracking=True)
    
    description = fields.Text('Description')
    cover_image = fields.Binary('Cover Image')
    
    borrowing_ids = fields.One2many('library.borrowing', 'book_id', string='Borrowing Records')
    active_borrowings = fields.Integer('Active Borrowings', compute='_compute_active_borrowings')

    @api.depends('borrowing_ids.state')
    def _compute_active_borrowings(self):
        for record in self:
            record.active_borrowings = len(record.borrowing_ids.filtered(lambda b: b.state == 'borrowed'))

    @api.depends('total_copies', 'active_borrowings')
    def _compute_copies_available(self):
        for record in self:
            record.copies_available = record.total_copies - record.active_borrowings
            if record.copies_available <= 0 and record.state != 'maintenance':
                record.state = 'borrowed'
            elif record.copies_available > 0 and record.state == 'borrowed':
                record.state = 'available'

    @api.constrains('total_copies')
    def _check_total_copies(self):
        for record in self:
            if record.total_copies < 1:
                raise ValidationError('Total copies must be at least 1')

    @api.constrains('isbn')
    def _check_isbn(self):
        for record in self:
            if record.isbn:
                existing = self.search([('isbn', '=', record.isbn), ('id', '!=', record.id)])
                if existing:
                    raise ValidationError('ISBN must be unique!')

    def action_set_maintenance(self):
        self.write({'state': 'maintenance'})

    def action_set_available(self):
        self.write({'state': 'available'})