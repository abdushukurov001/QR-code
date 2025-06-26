QR Kodga Asoslangan Davomat Tizimi
Umumiy Ko‘rinish
Ushbu loyiha Django va RESTful API asosida qurilgan bo‘lib, QR kod yordamida davomatni boshqarish imkonini beradi. Tizim administratorlar, o‘qituvchilar va talabalar uchun sinflar, fanlar, darslar, QR kodlar va davomat yozuvlarini boshqarishni ta’minlaydi. Django REST Framework (DRF), SimpleJWT autentifikatsiyasi va drf-yasg orqali API hujjatlari qo‘llaniladi. Shuningdek, telefon raqami orqali parolni tiklash va rolga asoslangan kirish nazorati mavjud.
Asosiy Xususiyatlar



Xususiyat
Tavsif



Foydalanuvchi Boshqaruvi
Ro‘yxatdan o‘tish, kirish, parol tiklash, rolga asoslangan kirish (admin, o‘qituvchi, talaba).


Sinf va Fan Boshqaruvi
Sinflar va fanlarni yaratish, yangilash, o‘chirish (admin uchun).


Dars Boshqaruvi
Darslarni rejalashtirish, sana yoki rol bo‘yicha filtrlash.


QR Kod Davomati
Darslar uchun QR kodlar avtomatik yaratiladi, o‘qituvchilar tomonidan tasdiqlanadi.


Davomat Kuzatuvi
Davomat yozuvlari (kelgan, kechikkan, kelmagan), sinf/fan/sana bo‘yicha filtr.


Boshqaruv Paneli
Rolga qarab statistika (masalan, admin uchun umumiy sonlar, talaba uchun davomat foizi).


API Hujjatlari
Swagger orqali interaktiv API hujjatlari.


Texnologik Stack



Komponent
Texnologiya



Backend
Django, Django REST Framework


Autentifikatsiya
SimpleJWT


Ma’lumotlar Bazasi
Django ORM (PostgreSQL, SQLite)


QR Kod Yaratish
python-qrcode, Pillow


API Hujjatlari
drf-yasg (Swagger)


Keshlash
Django kesh ramkasi


Boshqa
uuid, base64


VS Code’da O‘rnatish va Ishga Tushirish
1. Loyihani Yuklab Olish
VS Code’da Terminal oching (Ctrl + ~) va quyidagi buyruqlarni bajaring:
git clone https://github.com/abdushukurov001/QR-code.git
cd qr-davomat-tizimi

2. Virtual Mu hit Yaratish
Python virtual muhitini yarating va faollashtiring:
python -m venv venv
source venv/bin/activate  # Windowsda: venv\Scripts\activate

VS Code’da virtual muhitni tanlash uchun:

Ctrl + Shift + P → “Python: Select Interpreter” → venv muhitini tanlang.

3. Bog‘liqliklarni O‘rnatish
requirements.txt faylini yaratish uchun VS Code’da yangi fayl oching va quyidagi tarkibni qo‘shing:
echo -e "django==4.2\ndjangorestframework==3.14\ndjangorestframework-simplejwt==5.3\ndrf-yasg==1.21\nqrcode==7.4\npillow==10.0" > requirements.txt

Keyin bog‘liqliklarni o‘rnating:
pip install -r requirements.txt

4. Atrof-muhit O‘zgaruvchilarini Sozlash
.env faylini yaratish uchun VS Code’da New File tugmasini bosing va .env nomli faylga quyidagi tarkibni qo‘shing:
SECRET_KEY=sizning_django_yashirin_kalitingiz
DEBUG=True
DATABASE_URL=sqlite:///db.sqlite3

.env faylini .gitignore ga qo‘shish:.gitignore faylini oching va quyidagi qatorni qo‘shing:
.env

5. Migratsiyalarni Qo‘llash
Ma’lumotlar bazasini sozlash uchun:
python manage.py makemigrations
python manage.py migrate

6. Superfoydalanuvchi Yaratish
Admin uchun foydalanuvchi yaratish:
python manage.py createsuperuser

7. Serverni Ishga Tushirish
Loyihani ishga tushirish:
python manage.py runserver
