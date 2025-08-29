# -*- coding: utf-8 -*-
from odoo import api, fields, models,  _

class Picking(models.Model):
    _inherit = "stock.picking"

    code_contpaqi = fields.Char(string="Código contpaqi", help="Atributo para especificar el código del concepto base de ContPAQi que se procesará en la llamada. Listado de Conceptos")

class Picking(models.Model):
    _inherit = "stock.picking.type"

    code_contpaqi = fields.Char(string="Código contpaqi", help="Atributo obligatorio que contiene el código del Almacén a Afectar")