import unittest

from mygrations.formats.mysql.file_reader.database import database as database_reader
from mygrations.formats.mysql.mygrations.mygration import mygration

class test_add_conflicting_fks( unittest.TestCase ):

    accounts_table = """CREATE TABLE `accounts` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `name` VARCHAR(255) NOT NULL DEFAULT '',
            PRIMARY KEY (`id`)
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

    def _get_db1( self ):
        table1 = """CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `account_id` INT(10) UNSIGNED NOT NULL,
            `repeating_task_id` INT(10) UNSIGNED NOT NULL,
            `name` VARCHAR(255) NOT NULL DEFAULT '',
            PRIMARY KEY (`id`),
            KEY `account_id_tasks` (`account_id`),
            KEY `repeating_task_id_tasks` (`repeating_task_id`),
            CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        return database_reader( [ table1, self.accounts_table ] )

    def test_simple_add_and_modify( self ):
        """ Migrate to a database that has one extra table and column """

        table1 = """CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `account_id` INT(10) UNSIGNED NOT NULL,
            `repeating_task_id` INT(10) UNSIGNED NOT NULL,
            `name` VARCHAR(255) NOT NULL DEFAULT '',
            `subject` TEXT,
            PRIMARY KEY (`id`),
            KEY `account_id_tasks` (`account_id`),
            KEY `repeating_task_id_tasks` (`repeating_task_id`),
            CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        table3 = """CREATE TABLE `histories` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`)) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        db2 = database_reader( [ table1, self.accounts_table, table3 ] )
        db1 = self._get_db1()

        mygrate = mygration( db2, db1 )

        ops = [ str( op ) for op in mygrate.operations ]
        self.assertEquals( 'SET FOREIGN_KEY_CHECKS=0;', ops[0] )
        self.assertEquals( table3, ops[1] )
        self.assertEquals( 'ALTER TABLE `tasks` ADD `subject` TEXT AFTER `name`', ops[2] )
        self.assertEquals( 'SET FOREIGN_KEY_CHECKS=1;', ops[3] )

    def test_add_column_and_mutually_dependent_fk( self ):
        """ Add a column to a table that depends upon a table with a mutually-dependent FK """
        table1 = """CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`account_id` INT(10) UNSIGNED NOT NULL,
`repeating_task_id` INT(10) UNSIGNED NOT NULL,
`name` VARCHAR(255) NOT NULL DEFAULT '',
`subject` TEXT,
PRIMARY KEY (`id`),
KEY `account_id_tasks` (`account_id`),
KEY `repeating_task_id_tasks` (`repeating_task_id`),
CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
CONSTRAINT `repeating_task_id_tasks_fk` FOREIGN KEY (`repeating_task_id`) REFERENCES `repeating_tasks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        table2 = """CREATE TABLE `repeating_tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
`account_id` INT(10) UNSIGNED NOT NULL,
`task_id` INT(10) UNSIGNED NOT NULL,
`name` VARCHAR(255) NOT NULL DEFAULT '',
PRIMARY KEY (`id`),
KEY `account_id_rts` (`account_id`),
KEY `task_id_rts` (`task_id`),
CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
CONSTRAINT `task_id_rts` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        db2 = database_reader( [ table1, table2, self.accounts_table ] )

        mygrate = mygration( db2, self._get_db1() )
        ops = [ str(op) for op in mygrate.operations ]

        self.assertEquals( 'SET FOREIGN_KEY_CHECKS=0;', ops[0] )
        self.assertEquals( table2, ops[1] )

        # and then tasks will be modified
        self.assertEquals( 'ALTER TABLE `tasks` ADD `subject` TEXT AFTER `name`, ADD CONSTRAINT `repeating_task_id_tasks_fk` FOREIGN KEY (`repeating_task_id`) REFERENCES `repeating_tasks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE', ops[2] )
        self.assertEquals( 'SET FOREIGN_KEY_CHECKS=1;', ops[3] )

    def test_all_key_adjustments( self ):
        """ Add/remove/change keys! """

        table1 = """CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `account_id` INT(10) UNSIGNED NOT NULL,
            `repeating_task_id` INT(10) UNSIGNED NOT NULL,
            `name` VARCHAR(255) NOT NULL DEFAULT '',
            PRIMARY KEY (`id`),
            KEY `account_id_tasks` (`account_id`,`name`),
            KEY `cool_key` (`name`),
            CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        db2 = database_reader( [ table1, self.accounts_table ] )
        db1 = self._get_db1()

        mygrate = mygration( db2, db1 )
        ops = [ str( op ) for op in mygrate.operations ]

        self.assertEquals( 'SET FOREIGN_KEY_CHECKS=0;', ops[0] )
        self.assertEquals( 'ALTER TABLE `tasks` ADD KEY `cool_key` (`name`), DROP KEY `repeating_task_id_tasks`, DROP KEY `account_id_tasks`, ADD KEY `account_id_tasks` (`account_id`,`name`)', ops[1] )
        self.assertEquals( 'SET FOREIGN_KEY_CHECKS=1;', ops[2] )

    def test_all_column_adjustments( self ):
        """ Add/remove/change columns! """

        table1 = """CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `account_id` INT(10) UNSIGNED NOT NULL,
            `name` CHAR(16) DEFAULT NULL,
            `subject` TEXT,
            PRIMARY KEY (`id`),
            KEY `account_id_tasks` (`account_id`),
            CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        db2 = database_reader( [ table1, self.accounts_table ] )
        db1 = self._get_db1()

        mygrate = mygration( db2, db1 )
        ops = [ str( op ) for op in mygrate.operations ]

        self.assertEquals( 'SET FOREIGN_KEY_CHECKS=0;', ops[0] )
        self.assertEquals( 'ALTER TABLE `tasks` ADD `subject` TEXT AFTER `name`, CHANGE `name` `name` CHAR(16), DROP repeating_task_id, DROP KEY `repeating_task_id_tasks`', ops[1] )
        self.assertEquals( 'SET FOREIGN_KEY_CHECKS=1;', ops[2] )

    def test_all_constraint_adjustments( self ):
        """ Add/remove/change constraints! """

        table1 = """CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `account_id` INT(10) UNSIGNED NOT NULL,
            `task_id` INT(10) UNSIGNED NOT NULL,
            `repeating_task_id` INT(10) UNSIGNED NOT NULL,
            `name` VARCHAR(255) NOT NULL DEFAULT '',
            PRIMARY KEY (`id`),
            KEY `account_id_tasks` (`account_id`),
            KEY `repeating_task_id_tasks` (`repeating_task_id`),
            KEY `task_id` (`task_id`),
            CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT `task_id_fk` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        db1 = database_reader( [ table1, self.accounts_table ] )

        table1 = """CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `account_id` INT(10) UNSIGNED NOT NULL,
            `task_id` INT(10) UNSIGNED NOT NULL,
            `repeating_task_id` INT(10) UNSIGNED NOT NULL,
            `name` VARCHAR(255) NOT NULL DEFAULT '',
            PRIMARY KEY (`id`),
            KEY `account_id_tasks` (`account_id`),
            KEY `repeating_task_id_tasks` (`repeating_task_id`),
            KEY `task_id` (`task_id`),
            CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE,
            CONSTRAINT `task_id_2_fk` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""
        db2 = database_reader( [ table1, self.accounts_table ] )

        mygrate = mygration( db2, db1 )
        ops = [ str( op ) for op in mygrate.operations ]

        self.assertEquals( 'SET FOREIGN_KEY_CHECKS=0;', ops[0] )
        self.assertEquals( 'ALTER TABLE `tasks` ADD CONSTRAINT `task_id_2_fk` FOREIGN KEY (`task_id`) REFERENCES `tasks` (`id`) ON DELETE CASCADE ON UPDATE CASCADE, DROP FOREIGN KEY `account_id_tasks_fk`, ADD CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE RESTRICT ON UPDATE CASCADE, DROP FOREIGN KEY `task_id_fk`', ops[1] )
        self.assertEquals( 'SET FOREIGN_KEY_CHECKS=1;', ops[2] )

    def test_no_operations_on_1215( self ):

        table1 = """CREATE TABLE `tasks` (`id` INT(10) UNSIGNED NOT NULL AUTO_INCREMENT,
            `account_id` INT(10) NOT NULL,
            `repeating_task_id` INT(10) UNSIGNED NOT NULL,
            `name` VARCHAR(255) NOT NULL DEFAULT '',
            PRIMARY KEY (`id`),
            KEY `account_id_tasks` (`account_id`),
            KEY `repeating_task_id_tasks` (`repeating_task_id`),
            CONSTRAINT `account_id_tasks_fk` FOREIGN KEY (`account_id`) REFERENCES `accounts` (`id`) ON DELETE CASCADE ON UPDATE CASCADE,
            ) ENGINE=InnoDB DEFAULT CHARSET=utf8;"""

        db = database_reader( [ table1, self.accounts_table ] )
        mygrate = mygration( db )

        self.assertEquals( [ 'MySQL 1215 error for foreign key `account_id_tasks_fk`: unsigned mistmatch. `accounts`.`id` is unsigned but `tasks`.`account_id` is not' ], mygrate.errors_1215 )
        self.assertEquals( None, mygrate.operations )
