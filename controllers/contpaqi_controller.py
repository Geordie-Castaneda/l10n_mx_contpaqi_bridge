import logging
from odoo import http
from odoo.http import request

_logger = logging.getLogger(__name__)

class ContpaqiDocumentController(http.Controller):

    @http.route('/GetDocumentos/', type='json', auth='user', methods=['GET'], csrf=False)
    def get_documentos(self, **kwargs):
        """
        Endpoint que retorna los documentos de Odoo con estatus 0,2,3
        para sincronizar con ContPAQi
        """
        try:
            # 🔎 Verificar que hay sesión activa
            uid = request.session.uid
            if not uid:
                return {"error": "Usuario no autenticado"}
            print("request ", request, "\n ")
            print("session ", request.session, "\n ")
            print("uid ", uid)
            documents_list = []

            self.get_contacts(request, False, documents_list)
            self.get_purchase_orders(request, False, documents_list)
            self.get_sale_orders(request, False, documents_list)
            self.get_products(request, False, documents_list)

            documentos = {
                "Documentos": {
                    "Documento": documents_list
                }
            }
            return documentos

        except Exception as e:
            _logger.error("Error en get_documentos: %s", str(e))
            return {"error": str(e)}

    @http.route('/GetDocumentosById/', type='json', auth='user', methods=['POST'], csrf=False)
    def get_documentos_by_id(self, **kwargs):
        """
        Endpoint que retorna los documentos (ventas y compras)
        filtrados por un array de IDs
        """
        try:
            # 🔎 Verificar sesión
            uid = request.session.uid
            if not uid:
                return {"error": "Usuario no autenticado"}

            ids = kwargs.get("ArrayIds", [])
            print("ids ", ids)
            if not ids:
                return {"error": "Debe enviar ArrayIds con al menos un ID"}

            documents_list = []
            # --- Ventas (usamos helper) ---
            self.get_sale_orders(request, ids, documents_list)
            self.get_purchase_orders(request, ids, documents_list)

            return {
                "Documentos": {
                    "Documento": documents_list
                }
            }

        except Exception as e:
            return {"error": str(e)}


    def get_sale_orders(self, request, orders, documents_list):
        """Construye documentos de ventas y los agrega a documents_list"""
        if not orders:
            sales = request.env['sale.order'].search([])
        else:
            sales = request.env['sale.order'].search([('id', 'in', orders)])

        for sale in sales:
            movimientos_sale_list = []
            for line in sale.order_line:
                movimientos_sale_list.append({
                    "NoIdentificacion": line.product_id.default_code or '',
                    "Descripcion": line.product_id.name or '',
                    # "ClaveSAT": line.product_id.l10n_mx_edi_code or '01010101',
                    # "ClaveUnidad": line.product_uom_id.l10n_mx_edi_code or '',
                    "Cantidad": line.product_qty,
                    "ValorUnitario": line.price_unit,
                    "Almacen01": "1",
                    "Almacen02": "1",
                    "Clasificacion01": "MAT",
                    "Clasificacion02": "CON",
                    "Clasificacion03": "AMB"
                })
            
            documents_list.append({
                "Encabezado": {
                    "IdOdoo": sale.id,
                    "Estatus": "0",
                    "CodigoConceptoCi": "",
                    "Serie": "",
                    "Folio": "",
                    "Fecha": sale.date_order.strftime('%Y-%m-%d') if sale.date_order else '',
                    "Vencimiento": sale.validity_date.strftime('%Y-%m-%d') if sale.validity_date else '',
                    "MetodoPago": sale.payment_term_id.name,
                    "FormaPago": "254",
                    "UsoCFDI": "G01",
                    "Subtotal": sale.amount_untaxed,
                    "Impuestos": sale.amount_total - sale.amount_untaxed,
                    "Total": sale.amount_total,
                    "TimeStamp": "2025-01-09T12:14:46",
                    "Observaciones": sale.note or '',
                    "Referencias": sale.name,
                    "CTextoE01": "Texto Extra 01",
                    "CTextoE02": "Texto Extra 02",
                    "CTextoE03": "Texto Extra 03"
                },
                "ClienteProveedor": {
                    "Codigo": sale.partner_id.id,
                    "Nombre": sale.partner_id.name or '',
                    "Rfc": sale.partner_id.vat or '',
                    "RegimenFiscal": sale.partner_id.l10n_mx_edi_fiscal_regime or '',
                    "Email": sale.partner_id.email or '',
                    "Telefono": sale.partner_id.phone or '',
                    "CodigoPostal": sale.partner_id.zip or '',
                    "Colonia": "",
                    "Calle": sale.partner_id.street or '',
                    "Exterior": "",
                    "Interior": "",
                    "Ciudad": sale.partner_id.city or '',
                    "Municipio": "",
                    "Estado": sale.partner_id.state_id.name if sale.partner_id.state_id else '',
                    "Pais": sale.partner_id.country_id.name if sale.partner_id.country_id else '',
                },
                "Movimientos": {
                    "Movimiento": movimientos_sale_list
                }
            })
        return documents_list
    
    def get_purchase_orders(self, request, orders, documents_list):
        """Construye documentos de compras y los agrega a documents_list"""
        if not orders:
            purchases = request.env['purchase.order'].search([])
        else:
            purchases = request.env['purchase.order'].search([('id', 'in', orders)])
        
        for purchase in purchases:
            # Construir lista de movimientos
            movimientos_list = []
            for line in purchase.order_line:
                movimientos_list.append({
                    "NoIdentificacion": line.product_id.default_code or '',
                    "Descripcion": line.product_id.name or '',
                    # "ClaveSAT": line.product_id.l10n_mx_edi_code or '01010101',
                    # "ClaveUnidad": line.product_uom_id.l10n_mx_edi_code or '',
                    "Cantidad": line.product_qty,
                    "ValorUnitario": line.price_unit,
                    "Almacen01": "1",
                    "Almacen02": "1",
                    "Clasificacion01": "MAT",
                    "Clasificacion02": "CON",
                    "Clasificacion03": "AMB"
                })

            # Construir documento
            documents_list.append({
                "Encabezado": {
                    "IdOdoo": purchase.id,
                    "Estatus": "0",
                    "CodigoConceptoCi": "",
                    "Serie": "",
                    "Folio": "",
                    "Fecha": purchase.date_approve.strftime('%Y-%m-%d') if purchase.date_approve else '',
                    "Vencimiento": purchase.date_planned.strftime('%Y-%m-%d') if purchase.date_planned else '',
                    "MetodoPago": purchase.payment_term_id.name,
                    "FormaPago": "254",
                    "UsoCFDI": "G01",
                    "Subtotal": purchase.amount_untaxed,
                    "Impuestos": purchase.amount_total - purchase.amount_untaxed,
                    "Total": purchase.amount_total,
                    "TimeStamp": "2025-01-09T12:14:46",
                    "Observaciones": purchase.notes or '',
                    "Referencias": purchase.partner_ref,
                    "CTextoE01": "Texto Extra 01",
                    "CTextoE02": "Texto Extra 02",
                    "CTextoE03": "Texto Extra 03"
                },
                "ClienteProveedor": {
                    "Codigo": purchase.partner_id.id,
                    "Nombre": purchase.partner_id.name or '',
                    "Rfc": purchase.partner_id.vat or '',
                    "RegimenFiscal": purchase.partner_id.l10n_mx_edi_fiscal_regime or '',
                    "Email": purchase.partner_id.email or '',
                    "Telefono": purchase.partner_id.phone or '',
                    "CodigoPostal": purchase.partner_id.zip or '',
                    "Colonia": "",
                    "Calle": purchase.partner_id.street or '',
                    "Exterior": "",
                    "Interior": "",
                    "Ciudad": purchase.partner_id.city or '',
                    "Municipio": "",
                    "Estado": purchase.partner_id.state_id.name if purchase.partner_id.state_id else '',
                    "Pais": purchase.partner_id.country_id.name if purchase.partner_id.country_id else '',
                },
                "Movimientos": {
                    "Movimiento": movimientos_list
                }
            })
        return documents_list

    def get_contacts(self, request, contacts, documents_list):
        """Construye documentos de clientes y los agrega a documents_list"""
        if not contacts:
            partners = request.env['res.partner'].search([])
        else:
            partners = request.env['res.partner'].search([('id', 'in', contacts)])

        for contact in partners:
                documents_list.append({
                    "ClienteProveedor": {
                        "Codigo": contact.id,
                        "Nombre": contact.name or '',
                        "Rfc": contact.vat or '',
                        "RegimenFiscal": contact.l10n_mx_edi_fiscal_regime or '',
                        "Email": contact.email or '',
                        "Telefono": contact.phone or '',
                        "CodigoPostal": contact.zip or '',
                        "Colonia": "",
                        "Calle": contact.street or '',
                        "Exterior": "",
                        "Interior": "",
                        "Ciudad": contact.city or '',
                        "Municipio": "",
                        "Estado": contact.state_id.name if contact.state_id else '',
                        "Pais": contact.country_id.name if contact.country_id else '',
                    }
                })
        return documents_list
    
    def get_products(self, request, items, documents_list):
        """Construye documentos de productos/servicios y los agrega a documents_list"""
        if not items:
            products = request.env['product.template'].search([])
        else:
            products = request.env['product.template'].search([('id', 'in', items)])


        return documents_list





