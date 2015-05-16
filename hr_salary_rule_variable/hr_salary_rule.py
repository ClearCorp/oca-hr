# -*- coding:utf-8 -*-
##############################################################################
#
#    Copyright (C) 2014 Savoir-faire Linux. All Rights Reserved.
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as published
#    by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
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

from openerp.osv import fields, orm
from openerp.tools.safe_eval import safe_eval as eval
from openerp.tools.translate import _


class hr_salary_rule(orm.Model):
    _inherit = 'hr.salary.rule'
    _columns = {
        'variable_ids': fields.one2many(
            'hr.salary.rule.variable',
            'salary_rule_id',
            'Variables',
        ),
    }

    def variable(self, cr, uid, ids, date, localdict=False, context=None):
        """
        Get a salary rule variable related to a salary rule for
        a period of time

        This method is called from the salary rule:
        rule.variable(payslip.date_from)

        By using the optional argument localdict, you can pass the value of
        salary rule already computed. Example:
        rule.variable(payslip.date_from, {'GROSS': GROSS})

        :rtype: fixed amount (a float) or a python object (most likely a dict)
        """
        if isinstance(ids, (int, float)):
            ids = [ids]

        assert(len(ids) == 1)

        rule = self.browse(cr, uid, ids[0], context=context)

        # Find the salary rule variable related to that rule for the
        # requested period
        variable_list = [
            variable for variable in rule.variable_ids
            if variable.date_from <= date <= variable.date_to
        ]
        if not variable_list:
            raise orm.except_orm(
                _("Warning"),
                _("The salary rule variable related to %s does not "
                    "exist for the date %s""") %
                (rule.code, date))
        if len(variable_list) > 1:
            raise orm.except_orm(
                _("Warning"),
                _("%s salary rule variables related to %s exist for "
                    "the date %s""") %
                (len(variable_list), rule.code, date))

        variable = variable_list[0]

        # Return the result whether the variable is fix or based on python code
        if variable.type == 'python':
            return eval(variable.python_code, localdict or {})
        else:
            return variable.fixed_amount
