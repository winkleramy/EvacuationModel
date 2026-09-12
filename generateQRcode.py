# Generate QR Code for website
# Also possible from the command line directly: qr "mtbacheloma.org" > qr.png

from PIL import Image
import qrcode

qr = qrcode.make("evacuate.mtbacheloma.org")
type(qr)  # qrcode.image.pil.PilImage
qr.save("qr.png")

qr = qr.resize((1500,1500))
qr.save("qr_resize.pdf")
qr.save("qr_resize.png")