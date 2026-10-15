# -*- coding: utf-8 -*-
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import json, socket, threading, webbrowser, os
HOST, PORT = "0.0.0.0", int(os.environ.get("PORT", "8080"))
DATA = Path(os.environ.get("ZALP_DATA_FILE", str(Path(__file__).resolve().parent / "zalp_web_data" / "database.json")))
DEFAULT = {"projects":[{"id":"p1","name":"ZALP HOME EDITION","edition":"V1.0","status":"Működő prototípus","amplifier":"ZK-TB21","power":"18 V akkumulátor","cooling":"PS4 ventilátor","notes":""}],"speakers":[],"active":"p1"}
HTML = """<!doctype html><html lang="hu"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>ZALP Web Command Center v2</title>
<style>
:root{--g:#52f59b;--bg:#07110d;--p:#10251b;--m:#9cb8a7;--b:#234b36}*{box-sizing:border-box}body{margin:0;background:radial-gradient(ellipse at top,#123322,#07110d 65%);color:#eafff1;font:15px/1.5 Segoe UI,Arial}header{padding:20px 16px 14px;border-bottom:1px solid var(--b);background:#07110dee;position:sticky;top:0}.wrap,main{max-width:1150px;margin:auto}.brand{display:flex;gap:12px;align-items:center}.logo{border:1px solid var(--g);border-radius:13px;width:48px;height:48px;display:grid;place-items:center;color:var(--g);font-size:22px;font-weight:900}h1{font-size:clamp(19px,3vw,28px);margin:0}.muted,.sub{color:var(--m);font-size:13px}nav{display:flex;gap:7px;flex-wrap:wrap;margin-top:16px}.tab{background:#0b1a12;border:1px solid var(--b);color:var(--m);padding:10px 13px;border-radius:10px;cursor:pointer;font-weight:700}.tab.active,.tab:hover{background:var(--g);color:#06150d}main{padding:22px 16px 40px}.page{display:none}.page.active{display:block}.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.card{background:linear-gradient(145deg,#10251b,#0a1710);border:1px solid var(--b);border-radius:15px;padding:18px;min-width:0}.card h2{font-size:18px;color:var(--g);margin:0 0 12px}.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.stat,.item,.result{background:#07130c;border:1px solid var(--b);padding:12px;border-radius:10px;margin-top:10px}.stat b,.item strong{display:block;color:var(--g);font-size:17px}.stat span{font-size:12px;color:var(--m)}label{display:block;color:var(--m);font-size:13px;margin:10px 0 4px}input,textarea{width:100%;padding:10px;border:1px solid #315b42;border-radius:8px;background:#06110b;color:#eafff1;font:inherit}textarea{min-height:70px}button.primary{margin-top:12px;border:0;background:var(--g);color:#06150d;padding:10px 14px;border-radius:8px;font-weight:800;cursor:pointer}button.secondary,button.danger{margin-top:8px;border:1px solid var(--b);background:var(--p);color:#eafff1;padding:8px 11px;border-radius:8px;cursor:pointer}.danger{color:#ffbaba!important}.result{color:var(--g);white-space:pre-wrap}.notice{padding:12px;border:1px solid #705b23;background:#2a230d;color:#ffd36a;border-radius:10px;margin-top:14px;font-size:13px}.empty{color:var(--m);border:1px dashed var(--b);padding:14px;border-radius:9px}.actions{display:flex;gap:6px;flex-wrap:wrap}footer{text-align:center;padding:18px;color:var(--m);font-size:12px;border-top:1px solid var(--b)}@media(max-width:700px){header{position:static}.grid{grid-template-columns:1fr}.stats{grid-template-columns:1fr}.tab{flex:1 1 40%;padding:10px 6px}main{padding:15px 10px 30px}.card{padding:14px}}
</style></head><body><header><div class="wrap"><div class="brand"><div class="logo">Z</div><div><h1>ZALP WEB COMMAND CENTER v2.0</h1><div class="sub">AUDIO SYSTEMS • LOCAL DASHBOARD</div></div></div><nav><button class="tab active" data-page="home">Áttekintés</button><button class="tab" data-page="audio">Audio Designer</button><button class="tab" data-page="power">Power Station</button><button class="tab" data-page="speakers">Hangszórók</button><button class="tab" data-page="projects">Projektek</button></nav></div></header><main>
<section class="page active" id="home"><div class="card"><b style="color:var(--g)">● RENDSZER ONLINE</b><h2>ZALP vezérlőközpont</h2><p class="muted">Projekt- és hangszóró-adatbázis, mobilbarát felület.</p><div class="stats"><div class="stat"><b>v2.0</b><span>Webes dashboard</span></div><div class="stat"><b id="pc">1</b><span>Projekt</span></div><div class="stat"><b id="sc">0</b><span>Hangszóró</span></div></div></div><div class="grid"><div class="card"><h2>Gyorsindítás</h2><p>🔊 Doboz és reflexcső kalkulátor</p><p>⚡ Teljesítmény és üzemidő</p><p>📚 Hangszórók mentése</p><p>🗂️ Több projekt kezelése</p></div><div class="card"><h2>Aktív projekt</h2><div id="summary" class="muted">Betöltés…</div><button class="secondary" onclick="tab('projects')">Projektek kezelése</button></div></div><div class="notice">Csak helyi hálózaton használd. Nincs bejelentkezés; ne tedd ki az internetre porttovábbítással.</div></section>
<section class="page" id="audio"><div class="grid"><div class="card"><h2>Doboz térfogata</h2><label>Hossz (cm)</label><input id="len" type="number" value="40"><label>Szélesség (cm)</label><input id="wid" type="number" value="30"><label>Magasság (cm)</label><input id="hei" type="number" value="30"><button class="primary" onclick="volume()">Számítás</button><div class="result" id="vr">Eredmény</div></div><div class="card"><h2>Reflexcső-becslő</h2><label>Nettó térfogat (liter)</label><input id="bv" type="number" value="30"><label>Célfrekvencia (Hz)</label><input id="freq" type="number" value="40"><label>Cső belső átmérője (cm)</label><input id="dia" type="number" value="7"><button class="primary" onclick="port()">Csőhossz becslése</button><div class="result" id="pr">Eredmény</div></div></div><div class="notice">A reflexcsőhossz közelítő becslés; a tényleges hangolás a hangszórótól és dobozkialakítástól is függ.</div></section>
<section class="page" id="power"><div class="grid"><div class="card"><h2>Teljesítmény</h2><label>Feszültség (V)</label><input id="volt" type="number" value="18"><label>Áramerősség (A)</label><input id="amp" type="number" value="5"><button class="primary" onclick="power()">P = U × I</button><div class="result" id="powr">Eredmény</div></div><div class="card"><h2>Akkumulátor-üzemidő</h2><label>Feszültség (V)</label><input id="bvolt" type="number" value="18"><label>Kapacitás (Ah)</label><input id="ah" type="number" value="4"><label>Fogyasztás (W)</label><input id="load" type="number" value="30"><button class="primary" onclick="battery()">Üzemidő becslése</button><div class="result" id="br">Eredmény</div></div><div class="card"><h2>Ohm-törvény</h2><label>Mit számoljunk?</label><select id="ot"><option value="r">Ellenállás R=U/I</option><option value="i">Áram I=U/R</option><option value="u">Feszültség U=I×R</option></select><label>U (V)</label><input id="ou" type="number" value="12"><label>I (A)</label><input id="oi" type="number" value="2"><label>R (Ω)</label><input id="or" type="number" value="6"><button class="primary" onclick="ohm()">Kiszámítás</button><div class="result" id="orr">Eredmény</div></div></div></section>
<section class="page" id="speakers"><div class="grid"><div class="card"><h2>Hangszóró-adatlap</h2><label>Megnevezés</label><input id="sn" placeholder="ZALP 10 inch subwoofer"><label>Átmérő (inch)</label><input id="ss" type="number" placeholder="10"><label>Impedancia (Ω)</label><input id="si" type="number" placeholder="4"><label>Névleges teljesítmény (W)</label><input id="sw" type="number" placeholder="200"><label>Megjegyzés</label><textarea id="snote" placeholder="Típus, érzékenység, T/S adatok…"></textarea><button class="primary" onclick="addSpeaker()">Hangszóró mentése</button><div class="result" id="sres"></div></div><div class="card"><h2>Mentett hangszórók</h2><div id="slist" class="empty">Betöltés…</div></div></div></section>
<section class="page" id="projects"><div class="grid"><div class="card"><h2>Új projekt</h2><label>Projekt neve</label><input id="pn" placeholder="RoadBass RS540W"><label>Verzió</label><input id="pe" placeholder="V1.0"><label>Állapot</label><input id="pst" placeholder="Tervezés alatt"><label>Erősítő</label><input id="pa" placeholder="ZK-TB21"><label>Tápellátás</label><input id="pp" placeholder="18 V akkumulátor"><label>Hűtés</label><input id="pc" placeholder="Ventilátor"><label>Megjegyzések</label><textarea id="pnote"></textarea><button class="primary" onclick="addProject()">Projekt mentése</button><div class="result" id="pres"></div></div><div class="card"><h2>Projektjeim</h2><div id="plist" class="empty">Betöltés…</div></div></div></section></main><footer>ZALP WEB COMMAND CENTER v2.0 • helyi hálózati projekt</footer>
<script>
const $=id=>document.getElementById(id), n=id=>Number($(id).value), f=x=>x.toLocaleString('hu-HU',{maximumFractionDigits:2});
function tab(id){document.querySelectorAll('.tab').forEach(b=>b.classList.toggle('active',b.dataset.page===id));document.querySelectorAll('.page').forEach(p=>p.classList.toggle('active',p.id===id));if(id==='projects'||id==='speakers')refresh();window.scrollTo({top:0,behavior:'smooth'})}document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>tab(b.dataset.page)));
function volume(){let a=n('len'),b=n('wid'),c=n('hei');$('vr').textContent=a>0&&b>0&&c>0?`Bruttó térfogat: ${f(a*b*c/1000)} liter\\nA hangszóró és merevítések térfogatát vond le.`:'Adj meg pozitív méreteket.'}
function port(){let v=n('bv'),h=n('freq'),d=n('dia'),l=23562.5*d*d/(h*h*v)-.732*d;$('pr').textContent=v>0&&h>0&&d>0&&l>0?`Becsült csőhossz: ${f(l)} cm`:'Ellenőrizd az értékeket.'}
function power(){let u=n('volt'),i=n('amp');$('powr').textContent=u>0&&i>0?`Elektromos bemenő teljesítmény: ${f(u*i)} W`:'Adj meg pozitív értékeket.'}
function battery(){let u=n('bvolt'),a=n('ah'),w=n('load'),h=u*a/w;$('br').textContent=u>0&&a>0&&w>0?`Névleges energia: ${f(u*a)} Wh\\nElméleti üzemidő: ${f(h)} óra (${f(h*60)} perc)\\nA valós üzemidő rövidebb lehet.`:'Adj meg pozitív értékeket.'}
function ohm(){let t=$('ot').value,u=n('ou'),i=n('oi'),r=n('or'),v,unit;if(t==='r'){v=u/i;unit='Ω'}else if(t==='i'){v=u/r;unit='A'}else{v=i*r;unit='V'}$('orr').textContent=Number.isFinite(v)&&v>=0?`Eredmény: ${f(v)} ${unit}`:'Ellenőrizd az értékeket.'}
async function api(url,opt={}){let r=await fetch(url,{headers:{'Content-Type':'application/json'},...opt}),j=await r.json();if(!r.ok||j.error)throw Error(j.error||'Szerverhiba');return j}
function esc(s){return String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]))}
async function refresh(){try{let d=await api('/api/db');$('pc').textContent=d.projects.length;$('sc').textContent=d.speakers.length;let a=d.projects.find(p=>p.id===d.active)||d.projects[0];$('summary').innerHTML=a?`<p><b>${esc(a.name)}</b> ${esc(a.edition||'')}</p><p>Erősítő: ${esc(a.amplifier||'—')}</p><p>Táp: ${esc(a.power||'—')}</p><p>Állapot: ${esc(a.status||'—')}</p>`:'Nincs projekt';$('plist').innerHTML=d.projects.length?d.projects.map(p=>`<div class="item"><strong>${esc(p.name)}</strong><p>${esc(p.edition||'')} • ${esc(p.status||'')}</p><div class="actions"><button class="secondary" onclick="activate('${esc(p.id)}')">${p.id===d.active?'Aktív':'Aktiválás'}</button><button class="danger" onclick="delProject('${esc(p.id)}')">Törlés</button></div></div>`).join(''):'<div class="empty">Nincs projekt.</div>';$('slist').innerHTML=d.speakers.length?d.speakers.map(s=>`<div class="item"><strong>${esc(s.name)}</strong><p>${esc(s.size||'')}″ • ${esc(s.impedance||'')} Ω • ${esc(s.watts||'')} W</p><p>${esc(s.notes||'')}</p><button class="danger" onclick="delSpeaker('${esc(s.id)}')">Törlés</button></div>`).join(''):'<div class="empty">Még nincs mentett hangszóró.</div>'}catch(e){console.error(e)}}
async function addProject(){let p={name:$('pn').value.trim(),edition:$('pe').value,status:$('pst').value,amplifier:$('pa').value,power:$('pp').value,cooling:$('pc').value,notes:$('pnote').value};if(!p.name)return $('pres').textContent='A projekt neve kötelező.';try{await api('/api/projects',{method:'POST',body:JSON.stringify(p)});$('pres').textContent='Projekt elmentve!';['pn','pe','pst','pa','pp','pc','pnote'].forEach(x=>$(x).value='');refresh()}catch(e){$('pres').textContent=e.message}}
async function activate(id){try{await api('/api/active',{method:'POST',body:JSON.stringify({id})});refresh()}catch(e){alert(e.message)}}
async function delProject(id){if(!confirm('Biztosan törlöd a projektet?'))return;try{await api('/api/project-delete',{method:'POST',body:JSON.stringify({id})});refresh()}catch(e){alert(e.message)}}
async function addSpeaker(){let s={name:$('sn').value.trim(),size:$('ss').value,impedance:$('si').value,watts:$('sw').value,notes:$('snote').value};if(!s.name)return $('sres').textContent='A név kötelező.';try{await api('/api/speakers',{method:'POST',body:JSON.stringify(s)});$('sres').textContent='Hangszóró elmentve!';['sn','ss','si','sw','snote'].forEach(x=>$(x).value='');refresh()}catch(e){$('sres').textContent=e.message}}
async function delSpeaker(id){if(!confirm('Biztosan törlöd a hangszórót?'))return;try{await api('/api/speaker-delete',{method:'POST',body:JSON.stringify({id})});refresh()}catch(e){alert(e.message)}}refresh();
</script></body></html>"""


def load_db():
    DATA.parent.mkdir(exist_ok=True)
    if not DATA.exists(): save_db(DEFAULT)
    try: return json.loads(DATA.read_text(encoding="utf-8"))
    except Exception: return json.loads(json.dumps(DEFAULT))


def save_db(db):
    DATA.parent.mkdir(exist_ok=True)
    DATA.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")


def send_json(h, data, status=200):
    raw=json.dumps(data,ensure_ascii=False).encode()
    h.send_response(status); h.send_header("Content-Type","application/json; charset=utf-8"); h.send_header("Content-Length",str(len(raw))); h.send_header("Cache-Control","no-store"); h.end_headers(); h.wfile.write(raw)


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            raw=HTML.encode(); self.send_response(200); self.send_header("Content-Type","text/html; charset=utf-8"); self.send_header("Content-Length",str(len(raw))); self.send_header("Cache-Control","no-store"); self.end_headers(); self.wfile.write(raw)
        elif self.path == "/api/db": send_json(self,load_db())
        else: self.send_error(404)
    def do_POST(self):
        try:
            length=int(self.headers.get("Content-Length","0"))
            if length>100000: raise ValueError("Túl nagy kérés")
            data=json.loads(self.rfile.read(length).decode()); db=load_db(); path=self.path
            if path=="/api/projects":
                name=str(data.get("name","")).strip()[:120]
                if not name: return send_json(self,{"error":"A projekt neve kötelező."},400)
                p={"id":"p"+os.urandom(7).hex(),"name":name,"edition":str(data.get("edition",""))[:80],"status":str(data.get("status",""))[:120],"amplifier":str(data.get("amplifier",""))[:120],"power":str(data.get("power",""))[:120],"cooling":str(data.get("cooling",""))[:120],"notes":str(data.get("notes",""))[:2000]}
                db["projects"].append(p); db["active"]=p["id"]
            elif path=="/api/active":
                pid=str(data.get("id",""))
                if not any(p["id"]==pid for p in db["projects"]): return send_json(self,{"error":"Projekt nem található"},404)
                db["active"]=pid
            elif path=="/api/project-delete":
                pid=str(data.get("id","")); db["projects"]=[p for p in db["projects"] if p["id"]!=pid]
                if not db["projects"]: db["active"]=""
                elif db["active"]==pid: db["active"]=db["projects"][0]["id"]
            elif path=="/api/speakers":
                name=str(data.get("name","")).strip()[:120]
                if not name: return send_json(self,{"error":"A hangszóró neve kötelező."},400)
                db["speakers"].append({"id":"s"+os.urandom(7).hex(),"name":name,"size":str(data.get("size",""))[:30],"impedance":str(data.get("impedance",""))[:30],"watts":str(data.get("watts",""))[:30],"notes":str(data.get("notes",""))[:2000]})
            elif path=="/api/speaker-delete":
                sid=str(data.get("id","")); db["speakers"]=[s for s in db["speakers"] if s["id"]!=sid]
            else: return send_json(self,{"error":"Ismeretlen útvonal"},404)
            save_db(db); send_json(self,{"ok":True})
        except Exception as e: send_json(self,{"error":str(e)},400)
    def log_message(self,fmt,*args): print("[ZALP WEB] "+(fmt%args))


def main():
    load_db(); server=ThreadingHTTPServer((HOST,PORT),Handler)
    s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    try: s.connect(("192.0.2.1",80)); ip=s.getsockname()[0]
    except OSError: ip="127.0.0.1"
    finally: s.close()
    print("ZALP WEB COMMAND CENTER v2.0")
    print(f"Ezen a gépen: http://127.0.0.1:{PORT}")
    print(f"Helyi hálózaton: http://{ip}:{PORT}")
    print("Leállítás: Ctrl+C. Ne tedd ki az internetre porttovábbítással.")
    if not os.environ.get("RAILWAY_ENVIRONMENT"):
        threading.Timer(.7, lambda: webbrowser.open(f"http://127.0.0.1:{PORT}")).start()
    try: server.serve_forever()
    except KeyboardInterrupt: print("ZALP szerver leáll.")
    finally: server.server_close()

if __name__=="__main__":
    try: main()
    except OSError as e: print("Indítási hiba:",e); input("Enter a kilépéshez...")
