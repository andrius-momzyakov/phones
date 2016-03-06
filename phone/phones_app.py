import tornado.ioloop
import tornado.web as w
from dbutils import NoRowsFound
from models import Subunit, Person, list_unit_hierarchy, \
    list_stuff_by_subunit, staff_exists, Unit



class ListUnitHandler(w.RequestHandler):
    """
    Выводит весь список контактов по выбранной компании
    """
    def get(self, unit_id: int):
        def persons_wrapper(subunit=None, lvl=0):
            return list_stuff_by_subunit(parent_su=subunit, lvl=lvl)

        subunits = lambda unit: list_unit_hierarchy(unit=unit,
                                                        cls=Subunit)
        a_unit = Unit()
        units = a_unit.objects.find(unit_id=int(unit_id))
        self.render(template_name="list_unit_page.html", subunits=subunits,
                    units=units, persons=persons_wrapper, is_filtered=False,
                    staff_exists=staff_exists)


class MainHandler(w.RequestHandler):
    """
    Головная страница - выбор компании из списка
    """
    def get(self):
        #with dbutils.db as db:
        abstract_unit = Unit()
        self.render(template_name='units_page.html',
                    units=abstract_unit.objects.all())

    def post(self):
        self.redirect('/find/%s/' % self.get_argument('search_string'))


class FinderHandler(w.RequestHandler):
    """
    Обработчик поиска по фрагменту ФИО - ищет и выводит соответствующие фио по
    всем компаниям
    """
    def get(self, param1):
        def persons_wrapper(subunit=None, lvl=0, where_clause_raw=" and "
                            "upper(full_name) like '%{}%'".format(
                param1.upper())):
            return list_stuff_by_subunit(parent_su=subunit,
                                         lvl=lvl, where_clause_raw=
                                         where_clause_raw)

        def subunits_wrapper(unit):
            return list_unit_hierarchy(unit=unit, parent_su=None,
                                       lvl=0, cls=Subunit #,
                    #  where_clause_raw=" and subunit_id in (select "
                    #                      "subunit_id from staff where "
                    #                      "upper(full_name) like '%{"
                    #                      "}%')".format(param1.upper())
                                       )

        def staff_exists_wrapper(subunit_id):
            return staff_exists(subunit_id=subunit_id, where_clause_raw=" and "
                            "upper(full_name) like '%{}%'".format(
                            param1.upper()))

        a_unit = Unit()
        units = a_unit.objects.find(where_clause_raw=" and unit_id in ("
                                                     "select unit_id "
                                                     "from subunits where "
                                                     "subunit_id in (select "
                                                     "subunit_id from staff "
                                                     "where "
                                                     "upper(full_name) like "
                                                     "'%{"
                                                     "}%')"
                                                     ")".format(
                                    param1.upper()))
        subunits = subunits_wrapper
        self.render(template_name="list_unit_page.html", subunits=subunits,
                    persons=persons_wrapper, units=units, is_filtered=True,
                    staff_exists=staff_exists_wrapper)


def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/([0-9]+)/", ListUnitHandler),
        (r"/find/(.+)/", FinderHandler),
    ])

if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    tornado.ioloop.IOLoop.current().start()