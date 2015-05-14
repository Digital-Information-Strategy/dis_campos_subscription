# -*- coding: utf-8 -*-
##############################################################################
#
#	OpenERP, Open Source Management Solution
#	Copyright (C) 2013 Tiny SPRL (<http://tiny.be>).
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU Affero General Public License as
#	published by the Free Software Foundation, either version 3 of the
#	License, or (at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the
#	GNU Affero General Public License for more details.
#
#	You should have received a copy of the GNU Affero General Public License
#	along with this program.	If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from osv import osv, fields
from openerp.tools.translate import _
from datetime import datetime

from lxml import etree
from openerp import netsvc
from openerp.osv import fields, osv
from openerp import tools
import openerp.addons.decimal_precision as dp
import re
import sys
reload(sys)
sys.setdefaultencoding('utf-8')


class dis_campos_tools(osv.osv):
	_name = 'subscription.subscription'
	_inherit = 'subscription.subscription'

	def name_get(self, cr, uid, ids, context=None):
		if isinstance(ids, (list, tuple)) and not len(ids):
			return []
		if isinstance(ids, (long, int)):
			ids = [ids]
		reads = self.read(cr, uid, ids, ['number','name'], context=context)
		res = []
		for record in reads:
			name = ''
			if record['number']:
				name = str(record['number'])
			if record['name']:
				name = '['+str(record['number'])+'] '+str(record['name'][1])
			res.append((record['id'], name))
		return res

	def name_search(self, cr, user, name='', args=None, operator='ilike', context=None, limit=80):
		if not args:
			args=[]
		if not context:
			context={}
		ids = self.search(cr, user, [('number', 'ilike', name)] + args, limit=limit, context=context)
		if not ids:
			ids = self.search(cr, user, [('name', operator, name)] + args, limit=limit, context=context)
		return self.name_get(cr, user, ids, context)


	def _get_document_types(self, cr, uid, context=None):
		cr.execute('select m.model, s.name from subscription_document s, ir_model m WHERE s.model = m.id order by s.name')
		return cr.fetchall()

	_columns = {
		'currency': fields.selection([('colones','Colones'),('dolares','Dolares')], 'Moneda', select=1),
		'means_payment': fields.many2one('medio.de.pago','Medio de Pago'),
		'card_type': fields.many2one('tipo.de.tarjeta','Tipo de Tarjeta'),
		'card_number': fields.char('Número de tarjeta ',  select=True, states={'draft':[('readonly',False)]}),
		'installation_date': fields.datetime('Fecha de instalación '),
		'date_payment': fields.date('Fecha de pago'),
		'responsible': fields.many2one('gestor','Gestor encargado '),
		'number': fields.integer('Número de Contrato ', select=True, states={'draft':[('readonly',False)]}),
		'description': fields.char('Descripción ',  select=True, states={'draft':[('readonly',False)]}),
		'name': fields.many2one('res.partner',domain="[('customer','=',1)]" ),
		'state': fields.selection([('draft','Draft'),('running','Running'),('done','Done'), ('close','Cerrado'), ('annulled','Anulado'), ('renovated','Renovado')], 'Status'),
        'subscription_id': fields.many2one('subscription.subscription','Contrato anterior'),
		'new_subscription_id': fields.many2one('subscription.subscription','Nuevo contrato'),
        'doc_source': fields.reference('Source Document', required=False, selection=_get_document_types, size=128, help="User can choose the source document on which he wants to create documents"),
		'due_date': fields.char('Fecha de Vencimiento',  select=True, size= 5,states={'draft':[('readonly',False)]}),
        'quality_equipment': fields.many2one('quality.equipment', 'Calidad del equipo'),
        'technical_installer': fields.char('Técnico Instalador',  select=True, states={'draft':[('readonly',False)]}),
        'account_number': fields.char('Número de cuenta',  select=True, states={'draft':[('readonly',False)]}),
        'location_document': fields.many2one('location.location','Ubicación de Contrato'),
        'TELCOM': fields.boolean('TELCOM', select=True, states={'draft': [('readonly', False)]}),
        'GSM': fields.boolean('GSM', select=True, states={'draft': [('readonly', False)]}),
        'GPRS': fields.boolean('GPRS', select=True, states={'draft': [('readonly', False)]}),
        'TCP/IP': fields.boolean('TCP/IP', select=True, states={'draft': [('readonly', False)]}),
        'title': fields.char('Tipos de Comunicación'),
        'tel_Telcom': fields.char('Número telefónico', select=True, states={'draft': [('readonly', False)]}),
        'operator_telcom': fields.char('Operadora', select=True, states={'draft': [('readonly', False)]}),
		'tel_GSM': fields.char('Número telefónico', select=True, states={'draft': [('readonly', False)]}),
		'operator_GSM': fields.char('Operadora', select=True, states={'draft': [('readonly', False)]}),
		'IMEI_GSM': fields.char('IMEI', select=True, states={'draft': [('readonly', False)]}),
		'tel_GPRS': fields.char('Número telefónico', select=True, states={'draft': [('readonly', False)]}),
		'operator_GPRS': fields.char('Operadora', select=True, states={'draft': [('readonly', False)]}),
		'IMEI_GPRS': fields.char('IMEI', select=True, states={'draft': [('readonly', False)]}),
		'tel_TCP/IP': fields.char('IP', select=True, states={'draft': [('readonly', False)]}),
		'operator_TCP/IP': fields.char('Operadora', select=True, states={'draft': [('readonly', False)]}),
		'MAC_TCP/IP': fields.char('MAC', select=True, states={'draft': [('readonly', False)]}),
		'sql_accountid': fields.integer('Id de Cuenta', select=True, states={'draft': [('readonly', False)]}),
		'sql_acctnum': fields.char('Nombre de Cuenta', select=True, size=50, states={'draft': [('readonly', False)]}),
		'sql_name': fields.char('Nombre', select=True, size=50, states={'draft': [('readonly', False)]}),
		'sql_state': fields.char('Estado', select=True, size=50, states={'draft': [('readonly', False)]}),
	}
	_sql_constraints = [
			('number_uniq', 'unique (number)', 'El número de contrato debe ser único!'),
		]

	def create(self, cr, uid, vals, context=None):
		res=super(dis_campos_tools, self).create(cr, uid, vals, context=context)
		if vals.get('TELCOM',False):
			if vals.get('tel_Telcom',False) == False or vals.get('operator_telcom',False) == False:
				raise osv.except_osv(('¡Error Creando!'), ('Por favor digite todos los campos de TELCOM'))
		if vals.get('GSM', False):
			if vals.get('tel_GSM', False) == False or vals.get('operator_GSM', False) == False or vals.get('IMEI_GSM', False) == False:
				raise osv.except_osv(('¡Error Creando!'), ('Por favor digite todos los campos de GSM'))
		if vals.get('GPRS', False):
			if vals.get('tel_GPRS', False) == False or vals.get('operator_GPRS', False) == False or vals.get('IMEI_GPRS', False) == False:
				raise osv.except_osv(('¡Error Creando!'), ('Por favor digite todos los campos GPRS'))
		if vals.get('TCP/IP', False):
			if vals.get('tel_TCP/IP', False) == False or vals.get('operator_TCP/IP', False) == False or vals.get('MAC_TCP/IP', False) == False:
				raise osv.except_osv(('¡Error Creando!'), ('Por favor digite todos los campos TCP/IP'))
		return res

	def on_change_valida_fecha(self, cr, uid, ids, due_date, context=None):
		numeros=['0','1','2','3','4','5','6','7','8','9','/']
		dic={'due_date':due_date}
		dic2={'due_date':''}
		if due_date:
			for p in str(due_date):
				if p not in numeros:
					alerta = {'title':'Atención','message':'Digite la fecha en el formato correcto '
															   '[Ej: 02/12]'}
					return { 'value':dic2,'warning': alerta, }
			if re.findall('/',str(due_date)):
					pass
			else:
				alerta = {'title':'Atención','message':'Digite la fecha en el formato correcto '
															   '[Ej: 02/12]'}
				return { 'value':dic2,'warning': alerta, }
		else:
			pass
		return {'value': dic}
	
	#SOCKET INSERT
	def set_process(self, cr, uid, ids, context=None):
		res=super(dis_campos_tools, self).set_process(cr, uid, ids, context=context)
		subscription_obj=self.browse(cr, uid, ids[0], context=context)
		cr.execute("SELECT cedfisica FROM scktabonado WHERE cedfisica = '"+str(subscription_obj.number)+"'")
		rows = cr.fetchall()
		if not rows:
			query="INSERT INTO scktabonado (nomprop, cedfisica) values(%s, %s);" #cedfisica must be unique
			data=(subscription_obj.name.name, subscription_obj.number)
			cr.execute(query, data)
			subscription_obj.doc_source.write({'subscription_id':subscription_obj.id})
		print"SUBSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSSS: "+str(subscription_obj.id)
		#raise osv.except_osv(('¡Progra!'), ('Info'))
		return res

class annulment_wizard(osv.osv_memory):
    _name="annulment.wizard"
    _columns={
        'note': fields.text('Notas', help="Digite motivo de anulación del contrato"),    }
    def annular(self, cr, uid, ids, context=None):
        if context is None:
		    context={}
        note=context.get('note','')
        subscription_id=context.get('subscription_id','')
        subs_obj = self.pool.get('subscription.subscription')
        subs_obj.write(cr, uid, subscription_id, {'note':note, 'state':'annulled'})
        return True
annulment_wizard()

class renew_wizard(osv.osv_memory):
    _name="renew.wizard"
    _columns={
        'interval_number': fields.integer('Período: Cantidad de tiempo'),
        'exec_init': fields.integer('Número de documentos'),
        'interval_type': fields.selection([('days', 'Dias'), ('weeks', 'Semanas'), ('months', 'Meses')], 'Unidad de intervalo'),
        'date_init': fields.datetime('Primera Fecha'),
		'number': fields.integer('Número de Contrato')
        }
    def renew(self, cr, uid, ids, context=None):
        if context is None:
		    context={}

		#CAMPOS DEL WIZARD
        interval_number=context.get('interval_number','')
        exec_init=context.get('exec_init','')
        interval_type=context.get('interval_type','')
        date_init=context.get('date_init','')
        number=context.get('number','')
        #CAMPOS DEL CONTRATO ANTERIOR
        subscription_id=context.get('subscription_id','')
        partner_id=context.get('partner_id','')
        means_payment=context.get('means_payment','')
        card_number=context.get('card_number','')
        date_due=context.get('date_due','')
        description=context.get('description','')
        nada=""

        subscription_browse_obj=self.pool.get('subscription.subscription').browse(cr, uid, subscription_id, context=context)
        name=subscription_browse_obj.name.id

        subs_obj = self.pool.get('subscription.subscription')
        result = subs_obj.create(cr, uid, {'subscription_id':subscription_id, 'name':name,'interval_number':interval_number,
										   'exec_init':exec_init, 'interval_type':interval_type,'date_init':date_init, 'number':number})
        subs_obj.write(cr, uid, subscription_id, {'new_subscription_id':result,'state':'renovated','subscription_id':nada})


	view_ref = self.pool.get('ir.model.data').get_object_reference(cr, uid, 'subscription', 'view_subscription_form')
	view_id = view_ref and view_ref[1] or False,
	return {
	'type': 'ir.actions.act_window',
	'name': 'Subscription',
	'res_model': 'subscription.subscription',
	'res_id': result,
	'view_type': 'form',
	'view_mode': 'form',
	'view_id': view_id,
	'target': 'current',
	'nodestroy': True,
	}
renew_wizard()

#menu Ubicaciones
class location(osv.osv):
	_name = 'location.location'
	_description = 'Menu Configurable de Ubicacion'
	_columns = {
		'name' : fields.char('Ubicación', required=True),
		'description': fields.char('Descripción')
	}
location()

#menu de Calidad de los Equipos
class Quality_Equipment(osv.osv):
	_name = 'quality.equipment'
	_description = 'Menu Configurable de calidad de equipos'
	_columns = {
		'name' : fields.char('Calidad de los equipos', required=True),
		'description': fields.char('Descripción')
	}
Quality_Equipment()

class AccountInvoice(osv.osv):
	_inherit = 'account.invoice'
	_columns = {
		'state_sckt': fields.char('Estado Socket'),
		'subscription_id': fields.many2one('subscription.subscription', 'Contrato'),
	}

	def invoice_validate(self, cr, uid, ids, context=None):
		res=super(AccountInvoice, self).invoice_validate(cr, uid, ids, context=context)
		invoice_obj=self.browse(cr, uid, ids[0], context=context)
		codpropietario=0
		cr.execute("SELECT propietario FROM scktabonado WHERE cedfisica = '"+str(invoice_obj.subscription_id.number)+"'")
		rows = cr.fetchall()
		if rows:
			codpropietario=rows[0][0]
		query="INSERT INTO scktservdecobro (numfactura, codpropietario) values(%s, %s);"
		data=(invoice_obj.number, codpropietario)
		cr.execute(query, data)
		#raise osv.except_osv(('¡Progra!'), ('Jeank'))
		######################LINES
		line_obj=self.pool.get('account.invoice.line')
		line_ids = line_obj.search(cr, uid, [('invoice_id', '=', ids[0])])
		rubros_list= []
		montos_list= []

		query="INSERT INTO scktservdetallado (numfactura, numero, monto, fechavenc, fechadecobro) values(%s, %s, %s, %s, %s);"
		data=(invoice_obj.number, invoice_obj.number, invoice_obj.amount_total, self.date_to_long(invoice_obj.date_due), self.date_to_long(invoice_obj.date_invoice))
		cr.execute(query, data)

		x=0
		for l in line_obj.browse(cr, uid, line_ids, context=context):
			rubros_list.append(self.format(l.product_id.id, 4))
			montos_list.append(self.format(l.price_subtotal, 18))
		#raise osv.except_osv(('¡Progra!'), ('Jeank'))
		while x<len(rubros_list):
			#query="INSERT INTO scktservdetallado (rubro"+str(x+1)+", monto"+str(x+1)+") values(%s, %s) WHERE numfactura="+str(invoice_obj.number)
			query="UPDATE scktservdetallado SET rubro"+str(x+1)+"= %s,  monto"+str(x+1)+"= %s WHERE numfactura="+str(invoice_obj.number)
			data=(rubros_list[x], montos_list[x])
			cr.execute(query, data)
			x+=1
		return res

	def action_cancel(self, cr, uid, ids, context=None):
		query="DELETE FROM scktservdetallado WHERE numfactura = %s;"
		invoice_obj=self.browse(cr, uid, ids[0], context=context)
		data=(invoice_obj.number,)
		cr.execute(query, data)
		query="DELETE FROM scktservdecobro WHERE numfactura = %s;"
		invoice_obj=self.browse(cr, uid, ids[0], context=context)
		data=(invoice_obj.number,)
		cr.execute(query, data)
		res=super(AccountInvoice, self).action_cancel(cr, uid, ids, context=context)
		return res
	def format(self, number, digits):
		if digits!=4: # SI LOS DIGITOS NO SON PARA LOS IDS DE LOS PRODUCTOS, SE TENDRA QUE FORMATEAR COMO UN MONTO
			number=str(('%.2f' % number))
			number=number.replace('.','')
		else:
			number=str(number)
		x=len(number)
		while x<digits:
			number= "0"+str(number)
			x+=1
		return number

	def date_to_long(self, date_due):
		date_static = datetime.strptime('2000-12-31' , '%Y-%m-%d')
		date = datetime.strptime(date_due, '%Y-%m-%d')
		result = (date.toordinal() - date_static.toordinal()) + 73052
		return result
AccountInvoice()


#class campo_contrato(osv.osv):
#	_name = 'account.invoice'
#	_inherit = 'account.invoice'
#	_columns = {
#		'subscription': fields.many2one('subscription.subscription','Contrato'),
#	}
#campo_contrato()
