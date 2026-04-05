import sqlite3

conn = sqlite3.connect('gift_shop.db')
cursor = conn.cursor()

# حذف الجداول القديمة تماماً للبدء بنظافة
cursor.execute("DROP TABLE IF EXISTS users")
cursor.execute("DROP TABLE IF EXISTS gifts")
cursor.execute("DROP TABLE IF EXISTS sales")

# 1. جدول المستخدمين (مع العمود المسبب للمشكلة)
cursor.execute('''
    CREATE TABLE users (
        user_id INTEGER PRIMARY KEY, 
        username TEXT, 
        points INTEGER DEFAULT 0
    )
''')

# 2. جدول الهدايا (مع عمود الصور الجديد)
cursor.execute('''
    CREATE TABLE gifts (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price INTEGER,
        icon TEXT,
        image_url TEXT
    )
''')

# 3. جدول المبيعات
cursor.execute("CREATE TABLE sales (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, gift_id INTEGER)")

# إضافة البيانات بالروابط الجديدة
gifts = [
    (1, 'خاتم قبيلة كايي', 100, '💍', 'https://i.ibb.co/LzNfM9v/ring.png'),
    (2, 'سيف ذو الفقار الذهبي', 500, '⚔️', 'https://i.ibb.co/vY7mS9S/sword.png'),
    (3, 'خريطة الفتوحات الجلدية', 1500, '📜', 'https://i.ibb.co/6YfM6Yf/map.png'),
    (4, 'تاج السلطان القانوني', 5000, '👑', 'https://i.ibb.co/3WfM3Wf/crown.png')
]
cursor.executemany("INSERT INTO gifts VALUES (?, ?, ?, ?, ?)", gifts)

# تسجيلك كأدمن
cursor.execute("INSERT INTO users (user_id, username, points) VALUES (?, ?, ?)", (549686235, 'Ameen', 0))

conn.commit()
conn.close()
print("✅ تم تصفير القاعدة وإنشاؤها بنجاح! اختفت مشكلة username.")
