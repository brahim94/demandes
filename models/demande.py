# -*- coding: utf-8 -*-

from odoo import models, fields, api

_STATES = [
    ("draft", "Brouillon"),
    ("approved_responsable", "Approbée par son hiérarchie"),
    ("approved_da", "Approbée par la DA"),
    ("approved_it", "Approbée par le Service IT"),
    ("rejected", "Rejetée"),
    ("done", "Traitée"),
]

class demandes_stats(models.Model):
    _name = 'demandes.stats'
    _rec_name = 'type_demande'

    @api.model
    def _get_default_demanded_by(self):
        return self.env["res.users"].browse(self.env.uid)

    state = fields.Selection(
        selection=_STATES,
        string="Status",
        index=True,
        track_visibility="onchange",
        required=True,
        copy=False,
        default="draft",
    )
    demandor_id = fields.Many2one(comodel_name="res.users",
        string="Demandé par: ",
        required=True,
        copy=False,
        track_visibility="onchange",
        default=_get_default_demanded_by,
    )
    traited_by = fields.Many2one('res.partner', string="Traiter par :")
    demande_date = fields.Date(string="Date de demande")
    intervention_date = fields.Date(string="Date de traitement")
    description = fields.Text(string="Description")
    type_demande = fields.Selection(
        [('crf', 'Création Fournisseur'), ('crc', 'Création Client'), ('corc', 'Demande de Correction')], string='Nature de demande')
    
    assigned_to = fields.Many2one(comodel_name="res.users", string="Responsable", track_visibility="onchange",
        domain=lambda self: [("groups_id", "in", self.env.ref("demandes_stats.group_market_execution_achat").id)],
        default=lambda self:self.env.uid)

    def _get_my_department(self):
        employees = self.env.user.employee_ids
        return (
            employees[0].department_id
            if employees
            else self.env["hr.department"] or False
    )

    department_id = fields.Many2one(
        "hr.department", "Department", default=_get_my_department
    )

    @api.onchange("demandor_id")
    def onchange_requested_by(self):
        employees = self.demandor_id.employee_ids
        self.department_id = (
            employees[0].department_id
            if employees
            else self.env["hr.department"] or False
        )


    @api.onchange('department_id')
    def onchange_department(self):
        if self.department_id and self.department_id.manager_id:
            self.assigned_to = self.department_id.manager_id.user_id.id if self.department_id.manager_id.user_id else False

    
    def button_approved_responsable(self):
        return self.write({"state": "approved_responsable"})

    def print_vendor_creation(self):
        return self.env.ref('demandes_stats.action_vendor_creation').report_action(self)

    # def open_assignation_total(self):
    #         return {
    #         'name': _('Balance'),
    #         'type': 'ir.actions.act_window',
    #         'res_model': 'demandes.stats',
    #         'view_mode': 'tree',
    #         'view_id': False,
    #         'target': 'new',
    #     }