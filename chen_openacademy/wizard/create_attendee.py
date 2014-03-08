from osv import osv, fields


class create_attendee_wizard(osv.TransientModel):
    _name = 'openacademy.create.attendee.wizard'

    def action_add_attendee(self, cr, uid, ids, context=None):
        attendee_model = self.pool.get('openacademy.attendee')
        wizard = self.browse(cr, uid, ids[0], context=context)
        for attendee in wizard.attendee_ids:
            attendee_model.create(cr, uid, {
                'partner_id': attendee.partner_id.id,
                'session_id': wizard.session_id.id,
            })
        return {}
        #return {'type': 'ir.actions.act_window.close'}

    _columns = {
        'session_id': fields.many2one('openacademy.session', 'Session',
                                      required=True),
        'attendee_ids': fields.one2many('openacademy.attendee.wizard',
                                        'wizard_id', 'Attendees'),
    }


class attendee_wizard(osv.TransientModel):
    _name = 'openacademy.attendee.wizard'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'wizard_id': fields.many2one('openacademy.create.attendee.wizard'),
    }
