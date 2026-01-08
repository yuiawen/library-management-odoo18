# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError, UserError
from datetime import timedelta


class LibraryBorrowing(models.Model):
    _name = 'library.borrowing'
    _description = 'Library Borrowing Record'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _order = 'borrow_date desc'

    name = fields.Char('Reference', required=True, copy=False, readonly=True, default='New')
    member_id = fields.Many2one('library.member', string='Member', required=True, tracking=True)
    book_id = fields.Many2one('library.book', string='Book', required=True, tracking=True)
    
    borrow_date = fields.Date('Borrow Date', default=fields.Date.today, required=True, tracking=True)
    due_date = fields.Date('Due Date', required=True, tracking=True)
    return_date = fields.Date('Return Date', tracking=True)
    
    state = fields.Selection([
        ('draft', 'Draft'),
        ('borrowed', 'Borrowed'),
        ('returned', 'Returned'),
        ('lost', 'Lost')
    ], string='Status', default='draft', required=True, tracking=True)
    
    notes = fields.Text('Notes')
    days_overdue = fields.Integer('Days Overdue', compute='_compute_days_overdue', store=True)
    fine_amount = fields.Float('Fine Amount', compute='_compute_fine_amount', store=True)

    @api.depends('return_date', 'due_date', 'state', 'borrow_date')
    def _compute_days_overdue(self):
        for record in self:
            if record.state == 'borrowed' and record.due_date:
                today = fields.Date.today()
                if today > record.due_date:
                    record.days_overdue = (today - record.due_date).days
                else:
                    record.days_overdue = 0
            elif record.state == 'returned' and record.return_date and record.due_date:
                if record.return_date > record.due_date:
                    record.days_overdue = (record.return_date - record.due_date).days
                else:
                    record.days_overdue = 0
            else:
                record.days_overdue = 0

    @api.depends('days_overdue')
    def _compute_fine_amount(self):
        fine_per_day = 5000  # IDR 5000 per day
        for record in self:
            record.fine_amount = record.days_overdue * fine_per_day

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if vals.get('name', 'New') == 'New':
                vals['name'] = self.env['ir.sequence'].next_by_code('library.borrowing') or 'New'
        return super().create(vals_list)

    @api.onchange('borrow_date')
    def _onchange_borrow_date(self):
        if self.borrow_date:
            self.due_date = self.borrow_date + timedelta(days=14)

    def action_confirm_borrow(self):
        for record in self:
            if record.book_id.copies_available <= 0:
                raise UserError('No copies available for this book!')
            
            if record.member_id.borrowed_books_count >= record.member_id.max_books:
                raise UserError(f'Member has reached maximum borrowing limit ({record.member_id.max_books} books)!')
            
            record.write({'state': 'borrowed'})

    def action_return_book(self):
        self.write({
            'state': 'returned',
            'return_date': fields.Date.today()
        })

    def action_mark_lost(self):
        self.write({'state': 'lost'})

    @api.constrains('due_date', 'borrow_date')
    def _check_dates(self):
        for record in self:
            if record.due_date and record.borrow_date and record.due_date < record.borrow_date:
                raise ValidationError('Due date cannot be before borrow date!')