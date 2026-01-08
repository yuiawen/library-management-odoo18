from odoo import models, fields, api
from odoo.exceptions import ValidationError
import re


class LibraryMember(models.Model):
    _name = 'library.member'
    _description = 'Library Member'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'name'

    name = fields.Char('Member Name', required=True, tracking=True)
    member_number = fields.Char('Member Number', required=True, copy=False, readonly=True, default='New')
    email = fields.Char('Email', required=True)
    phone = fields.Char('Phone')
    address = fields.Text('Address')
    
    join_date = fields.Date('Join Date', default=fields.Date.today, required=True)
    membership_type = fields.Selection([
        ('standard', 'Standard'),
        ('premium', 'Premium'),
        ('student', 'Student')
    ], string='Membership Type', default='standard', required=True)
    
    active = fields.Boolean('Active', default=True)
    
    borrowing_ids = fields.One2many('library.borrowing', 'member_id', string='Borrowing Records')
    borrowed_books_count = fields.Integer('Borrowed Books', compute='_compute_borrowed_books_count')
    total_borrowings = fields.Integer('Total Borrowings', compute='_compute_total_borrowings')

    max_books = fields.Integer('Max Books Allowed', compute='_compute_max_books')

    @api.depends('membership_type')
    def _compute_max_books(self):
        limits = {'standard': 3, 'premium': 10, 'student': 5}
        for record in self:
            record.max_books = limits.get(record.membership_type, 3)

    @api.depends('borrowing_ids.state')
    def _compute_borrowed_books_count(self):
        for record in self:
            record.borrowed_books_count = len(record.borrowing_ids.filtered(lambda b: b.state == 'borrowed'))

    @api.depends('borrowing_ids')
    def _compute_total_borrowings(self):
        for record in self:
            record.total_borrowings = len(record.borrowing_ids)

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('member_number', 'New') == 'New':
                vals['member_number'] = self.env['ir.sequence'].next_by_code('library.member') or 'New'
        return super().create(vals_list)

    @api.constrains('email')
    def _check_email(self):
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        for record in self:
            if record.email and not re.match(email_regex, record.email):
                raise ValidationError('Invalid email format!')