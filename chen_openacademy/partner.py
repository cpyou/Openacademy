from openerp.osv import orm, fields


class partner(orm.Model):
    """ Inherited res.partner """

    # The line above is the Python's way to document
    # your objects  (like classes)
    _inherit = 'res.partner'

    _columns = {
        # We just add a new column in res.partner model
        'instructor': fields.boolean("Instructor"),
    }

    _defaults = {
        # By default, no partner is an instructor
        'instructor': False,
    }
