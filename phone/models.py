from dbutils import db_connected, Model, TooManyRoots, NoRowsFound


class Person(Model):
    """
    Запись о сотруднике в телефонном справочнике
    """
    def __init__(self, **fields):
        super().__init__(db_table='staff', pk_name='oid', select_list=('oid',
                                      'full_name', 'phone1',
                                         'phone2', 'subunit_id', 'email1',
                                         'is_head'), **fields)
        self.lvl = 0  # Свойство уровня иерархии - зарезервировано для
        # указания уровня в текущей иерархии

    def __str__(self):
        return self.lvl*' ' + '  !{full_name} ! {phone1} ! {phone2} ! \
                                    {email1}!'.format(**self.params)


class Subunit(Model):
    """
    Запись о подразделении внутри компании. Компания представлена иерархией
    подразделений в виде дерева.
    """
    def __init__(self, **fields):
        super().__init__(db_table='subunits', pk_name='subunit_id',
                         select_list=('oid', 'subunit_id','name',
                                      'unit_id'), **fields)
        self.lvl = 0  # Свойство уровня иерархии - зарезервировано для указания
        # уровня в текущей иерархии

    def __str__(self):
        return self.lvl * ' ' + self.name


class Unit(Model):
    """
    Запись о компании группы компаний
    """
    def __init__(self, **fields):
        super().__init__(db_table='units', pk_name='unit_id',
                         select_list=('unit_id', 'name'), **fields)

    def __str__(self):
        return self.name


@db_connected
def find_root_subunit(db, *, unit):
    """
    Поиск головного подразделения
    :param db:
    :param unit:
    :return:
    """
    with db as db:
        root = None
        # Ищем головное подр-е
        cursor = db.cursor()
        cursor.execute('''select * from subunits su where su.unit_id = {}
                          and not exists(select 1 from subunit_rels
                          where child_id = su.subunit_id)'''
                       .format(str(unit)))
        root = cursor.fetchone()
        if cursor.rowcount > 1:
            raise TooManyRoots
        if cursor.rowcount == 0:
            raise NoRowsFound
        return root[0]


@db_connected
def list_unit_hierarchy(db, *, unit, parent_su=None, lvl=0, cls=Subunit,
                        where_clause_raw=''):
    """
    Итератор для вывода структуры подразделений комании в соответствии с
    иерархией
    :param db: соединение с БД
    :param unit: id компании
    :param parent_su: головное подразделение - id
    :param lvl: уровень в иерархии (0-верхний)
    :param cls: модель для подразделения
    :param where_clause_raw:
    :return:
    """
    lvl_ = lvl
    with db as db:
        if not parent_su:
            try:
                parent_su_ = find_root_subunit(unit=unit)
            except NoRowsFound:
                return
            except:
                raise
        else:
            parent_su_ = parent_su
        abstract_subunit = cls()
        # print(parent_su_)
        yield abstract_subunit.objects.get(parent_su_), lvl_
        # выбираем потомков
        lvl_ += 1
        where_clause_raw = (' and subunit_id in (select child_id from ' \
                           'subunit_rels where parent_id={})' + \
                           where_clause_raw )\
                            .format(parent_su_)
        for su_obj in abstract_subunit.objects.find(where_clause_raw=
                                                    where_clause_raw,
                                                    unit_id=unit):
            for su_obj, l in list_unit_hierarchy(unit=unit, parent_su=su_obj
                                                 .subunit_id,
                                                 lvl=lvl_):
                yield su_obj, l
        lvl_ -= 1


@db_connected
def list_stuff_by_units(db, *, unit, parent_su=None):
    """
    Итератор для вывода списка сотрудников компании в соответствии с
    иерархией подразделений
    :param db:
    :param unit:
    :param parent_su:
    :return:
    """
    if parent_su:
        parent_su_ = parent_su
    else:
        try:
            parent_su_ = find_root_subunit(unit=unit)
        except TooManyRoots:
            raise
    i = 0
    for subunit_obj, lvl in list_unit_hierarchy(db=db, unit=unit,
                                                parent_su=parent_su_):
        subunit_obj.lvl = lvl
        yield subunit_obj
        abstract_person = Person()
        for p in abstract_person.objects.find(subunit_id=subunit_obj
                                              .subunit_id):
            p.lvl = lvl
            yield p


@db_connected
def list_stuff_by_subunit(db, *, parent_su, lvl=0, where_clause_raw=''):

    abstract_person = Person()
    if parent_su:
        for p in abstract_person.objects.find(subunit_id=parent_su,
                                              where_clause_raw=where_clause_raw):
            p.lvl = lvl
            yield p
        return
    for p in abstract_person.objects.find(where_clause_raw=where_clause_raw):
        p.lvl = lvl
        yield p

@db_connected
def staff_exists(db, subunit_id, where_clause_raw=''):
    for p in list_stuff_by_subunit(parent_su=subunit_id,
                                   where_clause_raw=where_clause_raw):
        return True
    return False

@db_connected
def find_by_full_name(db, search_pattern=''):
    with db as db:
        a_person = Person()
        for person in a_person.objects.find(where_clause_raw=" and "
                                                             "upper(full_name) "
                                                             "like '%{"
                                                             "}%'".format(
            search_pattern.upper())):
            yield person



if __name__ == '__main__':
    #p = Person(full_name='Test', phone1='123', phone2='234567',
    #           email1='mail@y.y')
    #print(p)
    #for per in p.objects.find(subunit_id=1):
    #    print(per)
    i = 0

    for person in find_by_full_name(search_pattern='Абрам'):
        print(person)

    #for line in list_stuff_by_units(unit=1):
    #    i += 1
    #    print(line)
