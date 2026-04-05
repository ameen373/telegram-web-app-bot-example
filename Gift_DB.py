import sqlite3

def setup():
    conn = sqlite3.connect('gift_shop.db')
    cursor = conn.cursor()

    print("🛠️ جاري تحديث قاعدة البيانات بالروابط المستقرة...")

    # تنظيف الجداول القديمة
    cursor.execute("DROP TABLE IF EXISTS users")
    cursor.execute("DROP TABLE IF EXISTS gifts")
    cursor.execute("DROP TABLE IF EXISTS sales")

    # إنشاء الجداول بالهيكلية الصحيحة
    cursor.execute('''CREATE TABLE users (
        user_id INTEGER PRIMARY KEY, 
        username TEXT, 
        points INTEGER DEFAULT 0)''')

    cursor.execute('''CREATE TABLE gifts (
        id INTEGER PRIMARY KEY,
        name TEXT,
        price INTEGER,
        icon TEXT,
        image_url TEXT)''')

    cursor.execute("CREATE TABLE sales (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, gift_id INTEGER)")

    # قائمة الهدايا بروابط CDN المضمونة 100%
    gifts_list = [
        (1, 'خاتم قبيلة كايي', 100, '💍', 'https://cdn-icons-png.flaticon.com/512/6591/6591461.png'),
        (2, 'سيف ذو الفقار الذهبي', 500, '⚔️', 'https://cdn-icons-png.flaticon.com/512/9343/9343940.png'),
        (3, 'خريطة الفتوحات الجلدية', 1500, '📜', 'https://cdn-icons-png.flaticon.com/512/854/854878.png'),
        (4, 'تاج السلطان القانوني', 5000, '👑', 'https://cdn-icons-png.flaticon.com/512/2353/2353724.png')
    ]
    
    cursor.executemany("INSERT INTO gifts VALUES (?, ?, ?, ?, ?)", gifts_list)

    # إضافة بياناتك كأدمن
    cursor.execute("INSERT INTO users (user_id, username, points) VALUES (?, ?, ?)", (549686235, 'Ameen', 0))

    conn.commit()
    conn.close()
    print("✅ تم التحديث بنجاح! الصور الآن ستعمل في الفواتير.")

if __name__ == "__main__":
    setup()
