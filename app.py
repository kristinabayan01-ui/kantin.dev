from flask import Flask, request, jsonify
import qrcode, io, base64, datetime
app = Flask(__name__)

MENU = {
    "nasi_goreng":{"nama":"Nasi Goreng","harga":15000},
    "mie_goreng":{"nama":"Mie Goreng","harga":12000},
    "nasi_kuning":{"nama":"Nasi Kuning","harga":13000},
    "soto_kuah":{"nama":"Soto Kuah Kuning","harga":15000},
    "es_teh":{"nama":"Es Teh","harga":5000},
    "kopi_hitam":{"nama":"Kopi Hitam","harga":7000},
}
pesanan_list = []
WA_ADMIN = "6282348662939" # <-- GANTI NOMOR WA KAMU DISINI

def cek_promo():
    jam = datetime.datetime.now().hour
    return 11 <= jam <= 14 # promo jam 11-14

@app.route("/meja/<id_meja>")
def pesan_meja(id_meja):
    is_promo = cek_promo()
    menu_html=""
    for k,v in MENU.items():
        menu_html+=f"<div class='menu'><span>{v['nama']} - Rp{v['harga']}</span><button onclick=\"add('{k}',{v['harga']})\">+ ADD</button></div>"
    
    banner_promo = f"<div style='background:yellow;border:2px solid black;padding:10px;text-align:center;font-weight:bold'>🔥 PROMO MAHASISWA 20% OFF! JAM MAKAN SIANG (11-14) 🔥</div>" if is_promo else ""

    return f"""
    <html><head><meta name="viewport" content="width=device-width,initial-scale=1">
    <style>
    body{{font-family:monospace;padding:15px;max-width:500px;margin:auto;padding-bottom:80px}}
    .menu{{border:1px solid #000;padding:12px;margin:6px 0;display:flex;justify-content:space-between;background:white}}
    #wa-btn{{position:fixed;bottom:15px;right:15px;background:#25D366;color:white;padding:12px 18px;border-radius:30px;text-decoration:none;font-weight:bold;box-shadow:0 2px 5px rgba(0,0,0,0.3)}}
    </style></head><body>
    <h1>kantin.dev - MEJA {id_meja}</h1>
    {banner_promo}
    <div style='margin:10px 0;background:#eee;padding:10px'>⭐ Poin Loyalitas: <b id='poin'>0</b> | <button onclick='tukarPoin()'>Tukar 50 Poin = Rp5000</button></div>
    {menu_html}
    <h3>Total: Rp<span id='total'>0</span> <span id='diskon-info'></span></h3>
    <p>Keranjang: <span id='cart'>kosong</span></p>
    <button style='width:100%;padding:15px;background:black;color:white' onclick='kirim()'>KIRIM PESANAN</button>

    <a id='wa-btn' href='https://wa.me/{WA_ADMIN}?text=Halo%20kantin.dev%20Meja%20{id_meja}%20saya%20butuh%20bantuan' target='_blank'>💬 Bantuan WA</a>

    <script>
    let cart=[]; let total=0; let potonganPoin=0;
    let poin = parseInt(localStorage.getItem('kantin_poin')||'0');
    document.getElementById('poin').innerText=poin;
    let isPromo = {'true' if is_promo else 'false'};

    function add(id,harga){{cart.push(id); total+=harga; update();}}
    function update(){{
        let diskonPromo = isPromo ? total*0.2 : 0;
        let totalAkhir = total - diskonPromo - potonganPoin;
        document.getElementById('cart').innerText=cart.join(', ');
        document.getElementById('total').innerText=totalAkhir;
        document.getElementById('diskon-info').innerText = (isPromo?`(Promo -20%: -Rp${{diskonPromo}}) `:'') + (potonganPoin?`(Poin: -Rp${{potonganPoin}})`:'');
    }}
    function tukarPoin(){{
        if(poin>=50){{poin-=50; potonganPoin=5000; localStorage.setItem('kantin_poin',poin); document.getElementById('poin').innerText=poin; update(); alert('Berhasil tukar poin!');}}
        else{{alert('Poin kurang, butuh 50. Poin kamu: '+poin);}}
    }}
    function kirim(){{
        if(cart.length==0){{alert('Kosong'); return;}}
        fetch('/api/pesan',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{meja:'{id_meja}',items:cart,total:document.getElementById('total').innerText}})}})
        .then(r=>r.json()).then(d=>{{
            poin+=10; localStorage.setItem('kantin_poin',poin);
            alert(d.message + ' +10 Poin!');
            cart=[]; total=0; potonganPoin=0; update();
        }});
    }}
    </script></body></html>
    """

@app.route("/api/pesan", methods=["POST"])
def api_pesan():
    data=request.json
    pesanan_list.append(data)
    return jsonify({"message":f"Pesanan Meja {data['meja']} masuk!"})

@app.route("/")
def index():
    html="<h1>QR Meja kantin.dev</h1>"
    for i in range(1,11):
        url=f"http://192.168.1.10:5000/meja/{i}"; qr=qrcode.make(url); buf=io.BytesIO(); qr.save(buf,format='PNG'); b64=base64.b64encode(buf.getvalue()).decode()
        html+=f"<div><h3>Meja {i}</h3><img src='data:image/png;base64,{b64}' width='150'></div>"
    return html

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)