#!/usr/bin/env python

import sys
import argparse
import pymysql
import pymysql.err
import pymysql.constants.ER
import pymysql.cursors
import re
import json

seq_features_re = re.compile(
    r"var\s+seqFeatures\s+=\s+new\s+Array\((?P<seq_features>.+?)\);"
)
sub_part_re = re.compile(
    r"new\s+Part\s(?P<sub_part>\(.+?\))[,\)]"
)
ac_re = re.compile(
    r"<li\s+class='boxctrl\s+box_(?P<color>green|red)'>(?P<RFC>\d+)",
    re.IGNORECASE
)


def _display_error(exc, abort=True):
    print(exc.args[1])
    if abort:
        sys.exit(1)


def _check_error(exc, detail):

    if exc.args[0] == getattr(pymysql.constants.ER, detail):
        _display_error(exc)


def no_table(exc):
    _check_error(exc, 'NO_SUCH_TABLE')


connection = None


def make_connection(args):

    try:
        return pymysql.connect(
            host=args.host,
            port=args.port,
            user=args.user,
            password=args.password,
            db=args.database,
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.err.DatabaseError as e:
        _display_error(e)


def prepare_table_structure():

    with connection.cursor() as cursor:
        try:
            cursor.execute("DESCRIBE parts")
            structures = cursor.fetchall()
        except pymysql.err.ProgrammingError as e:
            no_table(e)

        fields = {'ruler', 'ac'}
        missing = fields - set(x['Field'] for x in structures)

        if missing:
            print('Fields %s missing, altering table...' % ', '.join(missing))
            for field in missing:
                cursor.execute("ALTER TABLE parts ADD COLUMN %s longtext" % field)

    connection.commit()
    print('Table structures prepared')


def iterate_table(chunk, force):

    SQL = """
    SELECT `part_id`, `seq_edit_cache` {} FROM parts
    ORDER BY `part_id`
    """.format(', `ruler`, `ac`' if not force else '')

    with connection.cursor() as cursor:
        cursor.execute(SQL)
        while True:
            result = cursor.fetchmany(chunk)
            if not result:
                break
            yield result


def build_seq_features(string):
    return [
        dict(zip('type first last label reverse'.split(), item))
        for item in eval('[%s]' % string)
    ]


def build_sub_parts(strings):
    return [
        dict(zip('id short_name nick_name'.split(), eval(item)))
        for item in strings
    ]


def build_ac(items):
    return {
        rfc: color == 'green'
        for color, rfc in items
    }


def process(data, force, connection):

    if not data:
        return

    print('Processing parts %s ~ %s...' % (data[0]['part_id'], data[-1]['part_id']))

    with connection.cursor() as cursor:
        for item in data:

            if not force and item['ruler'] and item['ac']:
                continue

            html = item['seq_edit_cache'] or ''
            ruler = {
                'seq_features': build_seq_features(
                    (seq_features_re.findall(html) or [''])[0]
                ),
                'sub_parts': build_sub_parts(sub_part_re.findall(html))
            }
            ac = build_ac(ac_re.findall(html))

            cursor.execute(
                "UPDATE parts SET `ruler`=%s, `ac`=%s WHERE `part_id`=%s",
                (json.dumps(ruler), json.dumps(ac), item['part_id'])
            )

    connection.commit()


def main(args):

    global connection
    connection = make_connection(args)
    prepare_table_structure()

    update_connection = make_connection(args)
    for data in iterate_table(args.chunk, args.force):
        process(data, args.force, update_connection)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('database')
    parser.add_argument('--host', dest='host', default='localhost')
    parser.add_argument('--port', '-p', dest='port', type=int, default=3306)
    parser.add_argument('--user', '-u', dest='user', default='root')
    parser.add_argument('--password', '-pw', dest='password', default='')
    parser.add_argument('--chunk', '-c', dest='chunk', type=int, default=300)
    parser.add_argument('--force', '-f', dest='force', action='store_true', default=False)

    main(parser.parse_args())
