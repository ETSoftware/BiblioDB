# coding=utf8
# Versione 1.0.0
import socket
import urllib2
from flask import *
import json
from Crypto.Hash import SHA512
from Crypto.Cipher import AES
import base64
import os
from datetime import date, datetime, time, timedelta
from updater import Cupdate
import traceback
Cupdate()
# the block size for the cipher object; must be 16, 24, or 32 for AES
BLOCK_SIZE = 32
 
# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length. This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '{'
 
# one-liner to sufficiently pad the text to be encrypted
pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
 
# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)

try:
	secret=os.popen("./jsonvalidator.out").read()
except:
	os.system("./keygen.sh")
	secret=os.popen("./jsonvalidator.out").read()
# create a cipher object using the random secret
cipher = AES.new(secret)
 
def encode(string):
	encoded = EncodeAES(cipher, string)
	return encoded 
# decode the encoded string
def decode(encoded):
	decoded = DecodeAES(cipher, encoded)
	return decoded 
ip={"127.0.0.1":"Server"}
ipEnabled=False
ISBNuse = {}
# Dizionario che contiene le informazioni sullo stato dell'ISBN
isbnPos = {}
# Dizionario contenente l'ISBN in relazione alla posizione del volume
titleIsbn = {}
# Dizionario contenente il titolo in relazione all'ISBN
isbnTitle = {}
# Dizionario contenente l'autore in relazione all'ISBN
isbnAuthor = {}
# Dizionario contenente il proprietario in relazione all'ISBN
ISBNown = {}
ISBNborrowDate = {}
nomeFile = "db_libri"
borrowTime = 30
utenti={"admin":"password"}
badge={"01":"admin"}
tipoUtenti={"admin":"admin"}
statoUtenti={}
badgeUtenti={}
rfidISBN={}
try:
	o = open('bibliodb.json', 'r')
except IOError:
	o = open('bibliodb.json', 'w')
	json.dump(
		(ISBNuse,
		 isbnPos,
		 titleIsbn,
		 isbnTitle,
		 isbnAuthor,
		 nomeFile,
		 ISBNown,
		 borrowTime,
		 ISBNborrowDate),
		o)
	o.close()
else:
	o.close
finally:
	with open('bibliodb.json', 'r') as o:
		ISBNuse, isbnPos, titleIsbn, isbnTitle, isbnAuthor, nomeFile, ISBNown, borrowTime, ISBNborrowDate = json.load(
			o)
		o.close
try:
	o = open('tessere.json', 'r')
except IOError:
	o = open('tessere.json', 'w')
	json.dump((statoUtenti,badgeUtenti),o)
	o.close()
else:
	o.close
finally:
	with open('tessere.json', 'r') as o:
		statoUtenti,badgeUtenti = json.load(o)
		o.close
try:
	o = open('rfid.json', 'r')
except IOError:
	o = open('rfid.json', 'w')
	json.dump((rfidISBN),o)
	o.close()
else:
	o.close
finally:
	with open('rfid.json', 'r') as o:
		rfidISBN = json.load(o)
		o.close
try:
	o = open('bibliodb-utenti.json', 'r')
except IOError:
	o = open('bibliodb-utenti.json', 'w')
	o.write(encode(json.dumps((utenti,badge,tipoUtenti))))
	o.close()
else:
	o.close
finally:
	with open('bibliodb-utenti.json', 'r') as o:
		userstring=decode(o.read())
		utenti,badge,tipoUtenti = json.loads(userstring)
		o.close
try:
	o = open('ipWhitelist.json', 'r')
except IOError:
	o = open('ipWhitelist.json', 'w')
	o.write(encode(json.dumps((ip))))
	o.close()
else:
	o.close
finally:
	with open('ipWhitelist.json', 'r') as o:
		ipstring=decode(o.read())
		ip = json.loads(ipstring)
		o.close
def add(titolo,isbn,autore,pos):
	try:
		isbnPos[isbn] = pos.upper()
		titleIsbn[titolo] = isbn.upper()
		isbnTitle[isbn] = titolo.lower()
		isbnAuthor[isbn] = autore.lower()
		ISBNown[isbn]="Biblioteca"
		o = open('bibliodb.json', 'w')
		json.dump(
			(ISBNuse,
			 isbnPos,
			 titleIsbn,
			 isbnTitle,
			 isbnAuthor,
			 nomeFile,
			 ISBNown,
			 borrowTime,
			 ISBNborrowDate),
			o)
		o.close()
	except:
		return"ERRORE"
	else:
		return "Aggiunto "+titolo.title()
	pass
def addUser(cod,badge):
	try:
		statoUtenti[cod] = "OK"
		badgeUtenti[cod] = badge
		o = open('tessere.json', 'w')
		json.dump(
			(statoUtenti,
			 badgeUtenti),
			o)
		o.close()
	except:
		return"ERRORE"
	else:
		return "OK"
	pass
def find(mode,string):
	if mode==1:
		isbnCode=string.upper()
	elif mode==2:
		isbnCode=titToISBN(string.lower())
	pos=isbnPos[isbnCode].upper()
	titoloOpera=ISBNTotit(isbnCode).title()
	toReturn="----------------------------------\nTitolo:\t"+titoloOpera+"\nISBN:\t"+isbnCode+"\nAutore:\t"+ISBNToAut(isbnCode).title()+"\nPosizione:\t"+pos+"\n----------------------------------\n"
	return toReturn
def titToISBN(tit):
	try:
		Isbn = titleIsbn[tit]
	except:
		try:
			utit=tit.title()
			Isbn = titleIsbn[utit]
		except:
			Isbn=traceback.format_exc()
	return Isbn
	pass
def ISBNTotit(tISBN):
	titP = isbnTitle[tISBN]
	return titP
	pass
def ISBNToAut(aISBN):
	autP = isbnAuthor[aISBN]
	return autP
#Stato 0:prestito; stato 1:rientra
def prestaISBN(pISBN, state, owner):
	strPrestito=""
	#try:
	oldOwner=ISBNown[pISBN.upper()]
	if oldOwner=="Biblioteca":
		try:
			checkEsiste=statoUtenti[owner]
		except KeyError:
			strPrestito="L'utente è inesistente"
		else:
			ISBNuse[pISBN.upper()] = state
			ISBNown[pISBN.upper()] = owner
			data_prestito = datetime.today().strftime('%d/%m/%Y')
			data_fine = datetime.today() + timedelta(days=borrowTime)
			res = data_fine.strftime('%d/%m/%Y')
			ISBNborrowDate[pISBN] = data_prestito
			strPrestito=strPrestito+"Libro:\t" + ISBNTotit(pISBN).title() + "\nAutore: " + ISBNToAut(pISBN).title() + "\nISBN: \t" + pISBN + "\nPosizione:\t" + isbnPos[pISBN] + "\n" + 50 * '-' + '\n Stato:\n'
			if state == 0:
				strPrestito=strPrestito+"Prestato a: " + owner+'\n'
				strPrestito=strPrestito+"RENDERE ENTRO:\n"
				strPrestito=strPrestito+ res+'\n'
			elif state == 1:
				strPrestito=strPrestito+"Reso da: " + oldOwner+'\n'
				ISBNown[pISBN] = "Biblioteca"
				strPrestito=strPrestito+ "Prestato il: "+ISBNborrowDate[pISBN]+'\n'
			o = open('bibliodb.json', 'w')
			json.dump(
				(ISBNuse,
				 isbnPos,
				 titleIsbn,
				 isbnTitle,
				 isbnAuthor,
				 nomeFile,
				 ISBNown,
				 borrowTime,
				 ISBNborrowDate),
				o)
			o.close()
			#except KeyError:
			#   print"ERRORE"
	else:
		strPrestito="Il titolo è stato prestato in data "+ISBNborrowDate[pISBN]
	return strPrestito
def auth(user,password):
	h = SHA512.new()
	h.update(utenti[user])
	print h.hexdigest()
	try:
		if password==h.hexdigest():
			return tipoUtenti[user]
		else:
			return "Password Sbagliata"
	except:
		return "Utente inesistente"
def lista():
    list=""
    for isbn, num in isbnPos.items():
        list=list+isbn + ":\t" + ISBNTotit(isbn).title() + ", " + ISBNToAut(isbn).title() + "\t" + num.upper()+"\n"
    return list
def tsvExport():
    export = ""
    export=export +"ISBN o Codice\tTitolo\tAutore\tPosizione\n"
    for isbn, num in isbnPos.items():
        try:
            export=export+isbn +"\t" +ISBNTotit(isbn).title() +"\t" +ISBNToAut(isbn).title() +"\t" +num.upper() +"\n"
        except UnicodeEncodeError:
            export=export+" \t \t \t \n"
    return export
app = Flask(__name__)
@app.route('/users/add/<user>/<password>/<codTessera>/<badge>')
def AggiungiUtente(user, password, codTessera,badge):
	if auth(user,password)=="admin":
		return addUser(codTessera,badge)
	else:
		return"Non Autorizzato!"
@app.route('/rfid/auth/<rfid>')
def checkBadge(rfid):
	if ipEnabled==True:
		try:
			ipR= ip[request.environ['REMOTE_ADDR']]
		except KeyError:
			authStatus="2"
		else:
			try:
				if tipoUtenti[badge[urllib2.unquote(rfid).lower()]]=="admin":
					authStatus="1"
				else:
					authStatus="3"
			except:
				authStatus="Errore"
	else:
		try:
			if tipoUtenti[badge[urllib2.unquote(rfid).lower()]]=="admin":
				authStatus="1"
			else:
				authStatus="3"
		except:
			authStatus="Errore"
	return Response(response=authStatus, status=200,mimetype="text/plain")
@app.route('/auth/<user>/<password>')
def checkUser(user,password):
	if ipEnabled==True:
		try:
			ipR= ip[request.environ['REMOTE_ADDR']]
		except KeyError:
			authStatus="2"
		else:
			if auth(user,password)=="admin":
				authStatus="1"
			else:
				authStatus="3"

	else:
		if auth(user,password)=="admin":
			authStatus="1"
		else:
			authStatus="3"
	return Response(response=authStatus, status=200,mimetype="text/plain")
@app.route('/gbooks/<isbnapi>/<inforeq>')
def gBooksParser(isbnapi, inforeq):
	url="https://www.googleapis.com/books/v1/volumes?q=isbn:"+isbnapi+"&projection=lite"
	try:
		jsonurl=urllib2.urlopen(url)
		gbooksjson=json.loads(jsonurl.read())
	except:
		neterror=open('internet.jpg')
		gapi= Response(response=neterror.read(), status=200,mimetype="image/jpeg")
	else:
		try:
			a=gbooksjson["items"]
			book=a[0]
			info=book["volumeInfo"]
			if str(inforeq)=="titolo":
				inforesp=info["title"]
				gapi=Response(response=inforesp, status=200,mimetype="text/plain")
			elif str(inforeq)=="autore":
				inforesp=info["authors"]
				gapi=Response(response=inforesp, status=200,mimetype="text/plain")
			elif str(inforeq)=="copertina":
				try:
					images=info["imageLinks"]
					cover=images["thumbnail"]
				except:
					neterror=open('nodata.jpg')
					gapi= Response(response=neterror.read(), status=200,mimetype="image/jpeg")
				else:
					coverUrl=urllib2.urlopen(cover)
					inforesp=coverUrl.read()
					gapi= Response(response=inforesp, status=200,mimetype="image/jpeg")
		except:
			neterror=open('nodata.jpg')
			gapi= Response(response=neterror.read(), status=200,mimetype="image/jpeg")
	return gapi
@app.route('/rfid/add/<rfid>/<isbn>')
def rfidAdd(rfid,isbn):
	rfidISBN[urllib2.unquote(rfid).lower]=urllib2.unquote(isbn).lower
	resp=Response(response="Registrato "+isbn, status=200,mimetype="text/plain")
	return resp
@app.route('/rfid/isbn/<rfid>')
def rfidISBN(rfid):
	try:
		resp=Response(response=rfidISBN[urllib2.unquote(rfid).lower], status=200,mimetype="text/plain")
	except:
		resp=Response(response="Errore", status=200,mimetype="text/plain")
	return resp
@app.route('/rfid/auth/')
@app.route('/isbninfo/titolo/<isbn>')
def isbnTitolo(isbn):
	resp=Response(response=ISBNTotit(urllib2.unquote(str(isbn)).upper()).title(), status=200,mimetype="text/plain")
	return resp
@app.route('/isbninfo/scheda/<titolo>')
def scheda(titolo):
	resp=""
	try:
		isbn=str(titToISBN(urllib2.unquote(titolo.lower())))
		if ISBNown[isbn.upper()]=="Biblioteca":
			statoLibro="Non prestato"
		else:
			statoLibro="Prestato"
		resp=Response(response="\nTitolo: "+titolo.title()+"\nAutore: "+ISBNToAut(str(isbn).upper()).title()+"\nPosizione: "+isbnPos[isbn.upper()].upper()+"\nISBN: "+isbn.upper()+"\nStato: "+statoLibro, status=200,mimetype="text/plain")
	except:
#		resp=Response(response="Errore: Controlla il titolo",status=200,mimetype="text/plain")
		resp=Response(response=titolo+'\n'+isbn+'\n'+traceback.format_exc(),status=200,mimetype="text/plain")
	finally:
		return resp
@app.route('/isbninfo/isbn/<titolo>')
def TitoloIsbn(titolo):
	resp=Response(response=titToISBN(urllib2.unquote(str(titolo)).lower()).title(), status=200,mimetype="text/plain")
	return resp
@app.route('/isbninfo/posizione/<isbn>')
def isbnPosizione(isbn):
	resp = Response(response=isbnPos[str(isbn).upper()].upper(), status=200,mimetype="text/plain")
	return resp
@app.route('/isbninfo/autore/<isbn>')
def isbnAutore(isbn):
	resp = Response(response=ISBNToAut(str(isbn).upper()).title(), status=200,mimetype="text/plain")
	return resp
@app.route('/lista')
def listaTitoli():
	resp = Response(response=lista(), status=200,mimetype="text/plain")
	return resp
@app.route('/json')
def jsonGetter():
	json=open('bibliodb.json','r')
	str=""
	for lines in json:
		str=str+lines
	resp = Response(response=str, status=200,mimetype="application/json")
	return resp
@app.route('/tsv')
def tsvGetter():
	tsv=tsvExport()
	resp = Response(response=tsv, status=200,mimetype="text/tab-separeted-values")
	return resp
@app.route('/')
def Welcome():
	return'<html><head><title>BiblioDB API</title></head><body><h1>Benvenuti in BiblioDB!</h1><br><p>Per utilizzare le api bisogna modificare lo URL.</p><form action="https://www.paypal.com/cgi-bin/webscr" method="post" target="_top"><input type="hidden" name="cmd" value="_s-xclick"><input type="hidden" name="hosted_button_id" value="VFZK6WR23YBQL"><input type="image" src="https://www.paypalobjects.com/it_IT/IT/i/btn/btn_donateCC_LG.gif" border="0" name="submit" alt="PayPal - Il metodo rapido, affidabile e innovativo per pagare e farsi pagare."><img alt="" border="0" src="https://www.paypalobjects.com/it_IT/i/scr/pixel.gif" width="1" height="1"></form></body></html>'
@app.route('/qrcode.png')
def QrCode():
	try:
		s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
		s.connect(("etsoftware.forumfree.it",80))
		url="http://qrfree.kaywa.com/?s=20&d=http://"+s.getsockname()[0]+":5000/static/index.html"
		s.close()
		qrurl=urllib2.urlopen(url)
		qr=qrurl.read()
		return Response(response=qr, status=200,mimetype="image/png")
	#print url
	except:
		return "<h1>Errore</h1><p>Connettere il server ad Internet.<br><h2>Velocità Download:</h2><br>Modem 56 kbps:\t1s<br>ADSL:\t<1s</p>"
@app.route('/zipclient')
def zipClient():
	zipFile=open('BiblioDBnet.zip')
	return zipFile.read()
@app.route('/add/<user>/<password>/<titolo>/<isbn>/<autore>/<posizione>')
def addBook(user,password,titolo,isbn,autore,posizione):
	titolo=titolo.lower()
	err401="<html><head><title>Non Autorizzato</title></head><body><h1>Errore 401 - Non autorizzato</h1><br><i>Probabilmente si sta usando il programma su un dispositivo non autorizzato</i></body></html>"
	if ipEnabled==True:
		try:
			ipR= ip[request.environ['REMOTE_ADDR']]
		except KeyError:
			return err401
		else:
			if auth(user,password)=="admin":
				if add(titolo,isbn,autore,posizione)=="OK":
					return "Titolo Aggiunto"
				else:
					return "Errore"
			else:
				return err401

	else:
		if auth(user,password)=="admin":
			if add(titolo,isbn,autore,posizione)=="OK":
				return "Titolo Aggiunto"
			else:
				return "Errore"
		else:
			return err401
@app.route('/presta/<userP>/<passwordP>/<isbnP>/<idB>/<statoP>')
def prestaBook(userP,passwordP,isbnP,idB,statoP):
	err401="<html><head><title>Non Autorizzato</title></head><body><h1>Errore 401 - Non autorizzato</h1><br><i>Probabilmente si sta usando il programma su un dispositivo non autorizzato</i></body></html>"
	if ipEnabled==True:
		try:
			ipR= ip[request.environ['REMOTE_ADDR']]
		except KeyError:
			return err401
		else:
			if auth(userP,passwordP)=="admin":
				try:
					return Response(response=prestaISBN(isbnP,int(statoP),idB), status=200,mimetype="text/plain")
				except:
					return "Errore"
			else:
				return err401
	else:
		if auth(userP,passwordP)=="admin":
			try:
				return Response(response=prestaISBN(isbnP,int(statoP),idB), status=200,mimetype="text/plain")
			except:
			 	return "Errore"
		else:
			return err401
@app.route('/favicon.ico')
def returnIcon():
	icon=open('static/favicon.ico')
	return Response(response=icon.read(), status=200,mimetype="image/icon")
@app.route('/update')
def update():
	ISBNuse = {}
	# Dizionario che contiene le informazioni sullo stato dell'ISBN
	isbnPos = {}
	# Dizionario contenente l'ISBN in relazione alla posizione del volume
	titleIsbn = {}
	# Dizionario contenente il titolo in relazione all'ISBN
	isbnTitle = {}
	# Dizionario contenente l'autore in relazione all'ISBN
	isbnAuthor = {}
	# Dizionario contenente il proprietario in relazione all'ISBN
	ISBNown = {}
	ISBNborrowDate = {}
	nomeFile = "db_libri"
	borrowTime = 30
	try:
		o = open('bibliodb.json', 'r')
	except IOError:
		o = open('bibliodb.json', 'w')
		json.dump(
			(ISBNuse,
			 isbnPos,
			 titleIsbn,
			 isbnTitle,
			 isbnAuthor,
			 nomeFile,
			 ISBNown,
			 borrowTime,
			 ISBNborrowDate),
			o)
		o.close()
	else:
		o.close
	finally:
		with open('bibliodb.json', 'r') as o:
			ISBNuse, isbnPos, titleIsbn, isbnTitle, isbnAuthor, nomeFile, ISBNown, borrowTime, ISBNborrowDate = json.load(
				o)
			o.close()
		return "<h1>Il DataBase e stato aggiornato!</h1>"
if __name__ == '__main__':
	app.run(host='0.0.0.0')