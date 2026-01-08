# Library Management Module - Installation Guide

## 📋 Checklist Sebelum Install

### 1. Pastikan Semua File Sudah Benar di Server

Jalankan command ini untuk verifikasi:

```bash
# Cek apakah masih ada 'tree' di file views
docker compose exec odoo grep -r "<tree" /mnt/extra-addons/custom/library_management/views/

# Kalau ada output, berarti masih ada yang salah!
```

**Expected result**: Tidak ada output (tidak ada file yang pakai `<tree>`)

### 2. File-file Yang Harus Dicek

Pastikan file-file ini sudah pakai `<list>` bukan `<tree>`:

- ✅ `views/library_book_views.xml` → `<list string="Books">`
- ✅ `views/library_member_views.xml` → `<list string="Members">`
- ✅ `views/library_borrowing_views.xml` → `<list string="Borrowings">`

### 3. Quick Fix - Ganti Manual Jika Masih Error

Jika masih error "Invalid view type: 'tree'", edit manual di server:

```bash
docker compose exec odoo nano /mnt/extra-addons/custom/library_management/views/library_member_views.xml
```

**Ganti semua:**

- `<tree` → `<list`
- `</tree>` → `</list>`
- Di action, `view_mode="tree,form"` → `view_mode="list,form"`

Lakukan untuk semua 3 file views!

---

## 🚀 Instalasi Module

### Step 1: Restart Container

```bash
cd /mnt/d/Work/Internship/Nashta/odoo18/odoo-18.0
docker compose restart odoo
```

### Step 2: Update Module List (opsional jika sudah pernah coba install)

```bash
docker compose exec odoo bash -lc "odoo -c /etc/odoo/odoo.conf -d odoo18_dev -u base --stop-after-init"
```

### Step 3: Install Module

```bash
docker compose exec odoo bash -lc "odoo -c /etc/odoo/odoo.conf -d odoo18_dev -i library_management --stop-after-init"
```

### Step 4: Jika Ada Error, Uninstall Dulu

```bash
# Login ke Odoo UI, uninstall manual dari Apps menu
# Atau drop database dan buat baru:
docker compose exec db psql -U odoo -c "DROP DATABASE odoo18_dev;"
docker compose exec db psql -U odoo -c "CREATE DATABASE odoo18_dev;"

# Lalu install ulang
docker compose exec odoo bash -lc "odoo -c /etc/odoo/odoo.conf -d odoo18_dev -i library_management --stop-after-init"
```

---

## ✅ Verifikasi Sukses

Jika sukses, output terakhir akan seperti ini:

```
INFO odoo18_dev odoo.modules.loading: Modules loaded.
INFO odoo18_dev odoo.modules.registry: Registry loaded in X.XXs
INFO odoo18_dev odoo.service.server: Initiating shutdown
```

**Tidak ada ERROR atau CRITICAL!**

---

## 🐛 Troubleshooting

### Error: "Invalid view type: 'tree'"

**Solusi**: File views masih pakai `<tree>` bukan `<list>`

```bash
# Cek dan ganti manual
docker compose exec odoo sed -i 's/<tree/<list/g; s/<\/tree>/<\/list>/g' /mnt/extra-addons/custom/library_management/views/*.xml
```

### Error: "Unsearchable field 'days_overdue'"

**Solusi**: Sudah fixed di model dengan menambahkan `store=True`

### Error: Module tidak muncul di Apps

**Solusi**: Update apps list

```bash
docker compose restart odoo
# Lalu di UI: Apps → Update Apps List
```

---

## 📂 Struktur File Final

```
library_management/
├── __init__.py
├── __manifest__.py
├── models/
│   ├── __init__.py
│   ├── library_book.py
│   ├── library_member.py
│   └── library_borrowing.py
├── views/
│   ├── library_book_views.xml          (pakai <list>)
│   ├── library_member_views.xml        (pakai <list>)
│   ├── library_borrowing_views.xml     (pakai <list>)
│   └── library_menu.xml
├── security/
│   ├── library_security.xml
│   └── ir.model.access.csv
├── data/
│   └── library_data.xml
├── reports/
│   └── library_borrowing_report.xml
└── demo/
    └── library_demo.xml
```

---

## 🎯 Setelah Install Sukses

1. Login ke Odoo: `http://localhost:8069`
2. Buka menu **Library** (icon buku)
3. Test fitur:
   - ✅ Create Books
   - ✅ Register Members
   - ✅ Create Borrowing
   - ✅ Test workflow (Draft → Borrowed → Returned)
   - ✅ Check fine calculation untuk late returns

---

## 📝 Notes

- Module ini compatible dengan **Odoo 18** only
- Demo data akan ter-load otomatis jika install dengan demo mode
- Default admin punya akses penuh sebagai Library Manager
