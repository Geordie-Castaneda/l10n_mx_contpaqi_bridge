import json
import logging
from odoo import http
from odoo.http import request, Response

_logger = logging.getLogger(__name__)

class ContpaqiAuthController(http.Controller):
    
    @http.route('/contpaqi/auth', type='json', auth='none', methods=['POST'], csrf=False)
    def authenticate(self, **kwargs):
        """Autenticación estilo JSON-RPC de Odoo"""
        try:
            # Los datos vienen automáticamente en kwargs para type='json'
            _logger.info("Datos recibidos: %s", kwargs)
            
            db = kwargs.get('db')
            login = kwargs.get('login')
            password = kwargs.get('password')
            
            _logger.info("DB: %s, Login: %s", db, login)
            
            if not all([db, login, password]):
                return {
                    'success': False,
                    'error': 'Faltan parámetros: db, login, password'
                }
            
            # Autenticar usando el sistema de Odoo
            uid = request.session.authenticate(db, login, password)
            if uid:
                return {
                    'success': True,
                    'uid': uid,
                    'session_id': request.session.sid,
                    'message': 'Autenticación exitosa'
                }
            else:
                return {
                    'success': False,
                    'error': 'Credenciales inválidas'
                }
                
        except Exception as e:
            _logger.error("Error en autenticación: %s", str(e))
            return {
                'success': False,
                'error': f'Error de autenticación: {str(e)}'
            }