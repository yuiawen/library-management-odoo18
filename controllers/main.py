from odoo import http
from odoo.http import request
import json

class LibraryController(http.Controller):
    
    # CONTOH 1: GET Data Buku (Read)
    @http.route('/api/library/books', type='http', auth='public', methods=['GET'], csrf=False)
    def get_books(self, **kwargs):
        # M (Model): Mengambil data dari Model
        books = request.env['library.book'].sudo().search([])
        
        # Logika Bisnis: Format data menjadi JSON
        data = []
        for book in books:
            data.append({
                'id': book.id,
                'name': book.name,
                'author': book.author,
                'isbn': book.isbn,
                'state': book.state,
                'copies_available': book.copies_available
            })
            
        # V (View): Mengembalikan representasi JSON ke client
        return request.make_response(
            json.dumps({'status': 'success', 'data': data}),
            headers=[('Content-Type', 'application/json')]
        )

    # CONTOH 2: POST Peminjaman Buku (Write/Action)
    @http.route('/api/library/borrow', type='http', auth='public', methods=['POST'], csrf=False)
    def borrow_book(self, **kwargs):
        try:
            # Ambil data dari body request
            params = json.loads(request.httprequest.data)
            member_id = params.get('member_id')
            book_id = params.get('book_id')

            if not member_id or not book_id:
                return request.make_response(
                    json.dumps({'status': 'error', 'message': 'Missing member_id or book_id'}),
                    headers=[('Content-Type', 'application/json')]
                )

            # M (Model): Buat record baru di database
            borrowing = request.env['library.borrowing'].sudo().create({
                'member_id': int(member_id),
                'book_id': int(book_id),
            })
            
            # Panggil method logic (Controller Internal)
            borrowing.action_confirm_borrow()

            return request.make_response(
                json.dumps({
                    'status': 'success', 
                    'message': 'Book borrowed successfully',
                    'borrowing_reference': borrowing.name
                }),
                headers=[('Content-Type', 'application/json')]
            )
            
        except Exception as e:
            return request.make_response(
                json.dumps({'status': 'error', 'message': str(e)}),
                headers=[('Content-Type', 'application/json')]
            )