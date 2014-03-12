from osv import osv, fields


class create_attendee_wizard(osv.TransientModel):
    _name = 'openacademy.create.attendee.wizard'

    def action_add_attendee(self, cr, uid, ids, context=None):
        session_model = self.pool.get('openacademy.session')
        wizard = self.browse(cr, uid, ids[0], context=context)
        session_ids = [sess.id for sess in wizard.session_ids]
        att_data = [{'partner_id': att.partner_id.id for att in wizard.attendee_ids}]
        session_model.write(cr, uid, session_ids,
                            {'attendee_ids': [(0, 0, data) for data in att_data]},
                            context=context)
        return {}
        #return {'type': 'ir.actions.act_window.close'}

    def _get_active_session(self, cr, uid, context):
        if context.get('active_model') == 'openacademy.session':
            return context.get('active_id', False)
        return False

    _columns = {
        'session_ids': fields.many2many('openacademy.session', 'Session',
                                        required=True),
        'attendee_ids': fields.one2many('openacademy.attendee.wizard',
                                        'wizard_id', 'Attendees'),
    }

    _defaults = {
        'session_ids': _get_active_session,
    }


class attendee_wizard(osv.TransientModel):
    _name = 'openacademy.attendee.wizard'

    _columns = {
        'partner_id': fields.many2one('res.partner', 'Partner', required=True),
        'wizard_id': fields.many2one('openacademy.create.attendee.wizard'),
    }
