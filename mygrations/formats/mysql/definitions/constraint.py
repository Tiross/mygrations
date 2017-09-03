class constraint( object ):

    _errors = None
    _warnings = None
    _name = ''
    _column = ''
    _foreign_table = ''
    _foreign_column = ''
    _on_delete = ''
    _on_update = ''

    @property
    def name( self ):
        """ Public getter.  Returns the name of the column.

        :returns: The index name
        :rtype: string
        """

        return self._name

    @property
    def column( self ):
        """ Public getter.  Returns the name of the column this constraint is on

        :returns: The column name
        :rtype: string
        """

        return self._column

    @property
    def foreign_table( self ):
        """ Public getter.  Returns the name of the table this constraint is to

        :returns: The table name
        :rtype: string
        """

        return self._foreign_table

    @property
    def foreign_column( self ):
        """ Public getter.  Returns the name of the column in the foreign table this constraint is to

        :returns: The column name
        :rtype: string
        """

        return self._foreign_column

    @property
    def on_delete( self ):
        """ Public getter.  Returns the ON DELETE action for this constraint

        :returns: The ON DELETE action
        :rtype: string
        """

        return self._on_delete

    @property
    def on_update( self ):
        """ Public getter.  Returns the ON UPDATE action for this constraint

        :returns: The ON UPDATE action
        :rtype: string
        """

        return self._on_update

    @property
    def errors( self ):
        """ Public getter.  Returns a list of parsing errors

        :returns: A list of parsing errors
        :rtype: list
        """
        return [] if self._errors is None else self._errors

    @property
    def warnings( self ):
        """ Public getter.  Returns a list of parsing/table warnings

        :returns: A list of parsing/table warnings
        :rtype: list
        """
        return [] if self._warnings is None else self.warnings
