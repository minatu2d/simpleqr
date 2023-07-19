import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, GdkPixbuf, Gdk
import qrcode
import cv2

class QRCodeApp(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="QR Code App")

        self.set_border_width(10)
        self.set_default_size(400, 300)

        vbox = Gtk.VBox(spacing=10)
        self.add(vbox)

        self.entry = Gtk.Entry()
        vbox.pack_start(self.entry, True, True, 0)

        generate_button = Gtk.Button(label="Generate QR Code")
        generate_button.connect("clicked", self.generate_qrcode)
        vbox.pack_start(generate_button, True, True, 0)

        decode_button = Gtk.Button(label="Decode QR Image")
        decode_button.connect("clicked", self.decode_qrcode)
        vbox.pack_start(decode_button, True, True, 0)

        export_button = Gtk.Button(label="Export Image")
        export_button.connect("clicked", self.export_image)
        vbox.pack_start(export_button, True, True, 0)

        clipboard_button = Gtk.Button(label="Encode from Clipboard")
        clipboard_button.connect("clicked", self.encode_from_clipboard)
        vbox.pack_start(clipboard_button, True, True, 0)

        self.qr_image = Gtk.Image()
        vbox.pack_start(self.qr_image, True, True, 0)

        # Enable drag and drop
        # self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.drag_dest_set(Gtk.DestDefaults.ALL, [], Gdk.DragAction.COPY)
        self.drag_dest_add_uri_targets()
        self.connect("drag-data-received", self.on_drag_data_received)

    def generate_qrcode(self, button):
        text = self.entry.get_text()
        if text:
            qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
            qr.add_data(text)
            qr.make(fit=True)

            img = qr.make_image(fill_color="black", back_color="white")

            # Convert the PIL image to a GdkPixbuf
            pil_image = img.convert("RGBA")
            width, height = pil_image.size
            data = pil_image.tobytes()
            pixbuf = GdkPixbuf.Pixbuf.new_from_data(data, GdkPixbuf.Colorspace.RGB, True, 8, width, height, width * 4)

            # Set the Pixbuf to the Gtk Image widget
            self.qr_image.set_from_pixbuf(pixbuf)
        else:
            self.qr_image.clear()

    def decode_qrcode(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Select QR Image",
            parent=self,
            action=Gtk.FileChooserAction.OPEN,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_OPEN, Gtk.ResponseType.OK
        )
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()

            image = cv2.imread(filename)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            qr_decoder = cv2.QRCodeDetector()
            decoded_data, _, _ = qr_decoder.detectAndDecode(gray)

            if decoded_data:
                self.entry.set_text(decoded_data)
        dialog.destroy()

    def export_image(self, button):
        dialog = Gtk.FileChooserDialog(
            title="Save QR Image",
            parent=self,
            action=Gtk.FileChooserAction.SAVE,
        )
        dialog.add_buttons(
            Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
            Gtk.STOCK_SAVE, Gtk.ResponseType.OK
        )
        dialog.set_do_overwrite_confirmation(True)
        response = dialog.run()
        if response == Gtk.ResponseType.OK:
            filename = dialog.get_filename()

            # Get the GdkPixbuf from the Gtk Image widget
            pixbuf = self.qr_image.get_pixbuf()

            # Save the GdkPixbuf as an image file
            pixbuf.savev(filename, "png", [], [])
        dialog.destroy()

    def encode_from_clipboard(self, button):
        clipboard = Gtk.Clipboard.get(Gdk.SELECTION_CLIPBOARD)
        clipboard_text = clipboard.wait_for_text()

        if clipboard_text:
            self.entry.set_text(clipboard_text)
            self.generate_qrcode(button)

    def on_drag_data_received(self, widget, drag_context, x, y, data, info, time):
        uri_list = data.get_uris()
        if uri_list:
            filename = Gtk.filename_from_uri(uri_list[0])
            self.decode_image_file(filename)

    def decode_image_file(self, filename):
        try:
            image = cv2.imread(filename)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            qr_decoder = cv2.QRCodeDetector()
            decoded_data, _, _ = qr_decoder.detectAndDecode(gray)

            if decoded_data:
                self.entry.set_text(decoded_data)
            else:
                self.show_error_dialog("No QR Code found in the image")
        except Exception as e:
            self.show_error_dialog(str(e))

    def show_error_dialog(self, message):
        dialog = Gtk.MessageDialog(
            parent=self,
            flags=Gtk.DialogFlags.MODAL,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()

win = QRCodeApp()
win.connect("destroy", Gtk.main_quit)
win.show_all()
Gtk.main()
