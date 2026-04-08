// بيانات Firebase الخاصة بك (انسخها من إعدادات مشروعك)
const firebaseConfig = {
  databaseURL: "https://telega-io-default-rtdb.firebaseio.com/"
};
firebase.initializeApp(firebaseConfig);
const database = firebase.database();

// ميزة 1: إرسال البث العالمي
function sendBroadcast() {
    const msg = document.getElementById('broadcastMsg').value;
    if(msg) {
        database.ref('global_notification').set({
            msg: msg,
            time: Date.now()
        }).then(() => alert("✅ تم إرسال الإشعار لجميع المستخدمين!"));
    }
}

// ميزة 2: تحديث الرصيد (نظام الضمان)
function updateBalance(userId, amount) {
    database.ref('wallets/' + userId).update({
        balance: amount,
        last_update: Date.now()
    });
}
