from openerp.osv import orm, fields


class course(orm.Model):
    _name = "openacademy.course"

    # Allow to make a duplicate Course
    # def copy(self, cr, uid, id, default, context=None):
    #     course = self.browse(cr, uid, id, context=context)
    #     new_name = "Copy of %s" % course.name
    #     # =like is the original LIKE operater from SQL
    #     others_count = self.search(cr, uid, [('name', '=like', new_name+'%')],
    #                                count=True, context=context)
    #     if others_count > 0:
    #         new_name = "%s (%s)" % (new_name, others_count + 1)
    #     default['name'] = new_name
    #     return super(course, self).copy(cr, uid, id, default, context=context)
    # the following function is used in graph
    def _get_attendee_count(self, cr, uid, ids, name, args, context=None):
        res = {}
        for course in self.browse(cr, uid, ids, context=context):
            num = 0
            for course in course.session_ids:
                num += len(session.attendee_ids)
            res[course.id] = num
        return res

    _columns = {
        'name': fields.char(string="Title", size=256, required=True),
        'description': fields.text(string="Description"),
        'responsible_id': fields.many2one('res.users', ondelete='set null',
                                          string="Responsible", select=True),
        'session_ids': fields.one2many('openacademy.session', 'course_id',
                                       string='Session'),
        #  attendee_count for graph
        'attendee_count': fields.function(
            _get_attendee_count, store=True, type="integer",
            string="attendee Count")
    }

    _sql_constraints = [
        ('name_description_check',
         'CHECK(name <> description)',
         'The title of the course should be diffrent of the description'),
        ('name_unique',
         'UNIQUE(name)',
         'The title must be unique'),
    ]


class session(orm.Model):
    _name = "openacademy.session"

    def _get_taken_seats_percent(self, seats, attendee_list):
        try:
            return (100.0 * len(attendee_list)) / seats
        except ZeroDivisionError:
            return 0.0

    def _taken_seats_percent(self, cr, uid, ids, field, arg, context=None):
        result = {}
        # print "\n\n %s \n\n" % "result[session.id]"
        for session in self.browse(cr, uid, ids, context=context):
            result[session.id] = self._get_taken_seats_percent(
                session.seats, session.attendee_ids)
            # print "\n\n %s \n\n" % result
        return result

    # The function is for gantt
    def _get_attendee_count(self, cr, uid, ids, name, args, context=None):
        res = {}
        for session in self.browse(cr, uid, ids, context=context):
            res[session.id] = len(session.attendee_ids)
        return res

    def onchange_taken_seats(self, cr, uid, ids, seats, attendee_ids):
        attendee_records = self.resolve_o2m_commands_to_record_dicts(
            cr, uid, 'attendee_ids', attendee_ids, ['id'])
        res = {
            'value': {
                'taken_seats_percent': self._get_taken_seats_percent(
                    seats, attendee_records),
            },
        }
        if seats < 0:
            res['warning'] = {
                'title': "Warning: bad value",
                'message': "You cannot have negative number of session",
            }
        elif seats < len(attendee_ids):
            res['warning'] = {
                'title': "Warning: problems",
                'message': "You need more seats for this session",
            }
        return res

    def action_draft(self, cr, uid, ids, context=None):
        # set to "draft" state
        return self.write(cr, uid, ids, {'state': 'draft'}, context=context)

    def action_confirm(self, cr, uid, ids, context=None):
        # set to "confirmed" state
        return self.write(cr, uid, ids, {'state': 'confirmed'}, context=context)

    def action_done(self, cr, uid, ids, context=None):
        # set to "done" state
        return self.write(cr, uid, ids, {'state': 'done'}, context=context)

    _columns = {
        'name': fields.char(string="Name", size=256, required=True),
        'start_date': fields.date(string="Start date"),
        'duration': fields.float(string="Duration", digits=(6, 2),
                                 help="Duration in days"),
        'seats': fields.float(string="Number of seats"),
        'active': fields.boolean("Actice"),

        'state': fields.selection(
                     [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('done', 'Done')],
                     'State', readonly=True, required=True),
        'taken_seats_percent': fields.function(
            _taken_seats_percent, type="float", string="Taken Seats"),
        'instructor_id': fields.many2one(
            'res.partner', string="instructor",
            domain=['|', ('instructor', '=', True),
                    ('category_id.name', 'ilike', 'Teacher')]),
        'course_id': fields.many2one('openacademy.course', ondelete='cascade',
                                     string='course', required=True),
        'attendee_ids': fields.one2many('openacademy.attendee', 'session_id',
                                        string='Attendees'),
        # attendee_count is for graph
        'attendee_count': fields.function(
            _get_attendee_count, type='integer', string='attendee Count'),
    }

    _defaults = {
        # You can give a function or a lambda for default value. Openerp will
        # automatically call it and get its return value at each record
        # creation. 'today' is a method of the object 'date' of module 'fields'
        # that returns -in the right timezone- the current date in the OpenERP
        # format
        'start_date': fields.date.today,
        # Beware that is not the same as :
        # 'start_date': fields.date.today(),
        # which actually call the method at Openerp startup!
        'active': True,
        'state': 'draft',
    }

    def _check_instructor_not_in_attendees(self, cr, uid, ids, context=None):
        for session in self.browse(cr, uid, ids, context=None):
            partners = [att.partner_id for att in session.attendee_ids]
            if session.instructor_id and session.instructor_id in partners:
                return False
        return True

    _constraints = [
        (_check_instructor_not_in_attendees,
         "The instructor can not be also an attendee!",
         ['instructor_id', 'attendee_ids']),
    ]


class attendee(orm.Model):
    _name = "openacademy.attendee"

    _rec_name = 'partner_id'

    _columns = {
        'partner_id': fields.many2one('res.partner', string="Partner",
                                      required=True, ondelete='cascade'),
        'session_id': fields.many2one('openacademy.session', string="Session",
                                      required=True, ondelete='cascade'),
    }

    _sql_constraints = [
        ('partner_session_unique',
         'UNIQUE(partner_id, session_id)',
         'You can not insert the same attendee multiple times!'),
    ]
