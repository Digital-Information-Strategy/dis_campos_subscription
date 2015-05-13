# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 DIS (<http://www.dis.co.cr>).
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
{
    "name" : "Cambios Visuales en Subscription",
    "version" : "0.1",
    "author" : "DIS S.A.",
    "website" : "http://www.dis.co.cr",
    "category" : "Desarrollo",
    "description": """Agrega y valida campos en subscription, crea wizards de renovar y anular contratos""",
    "depends" : ['base','subscription','dis_form_TipoDeTarjeta','dis_form_MedioDePago','dis_form_gestores','account_voucher','account'],
    "init_xml" : [ ],
    "demo_xml" : [ ],
    "update_xml" : ['views/dis_campos_susbcription_view.xml'],
    "installable": True
}
