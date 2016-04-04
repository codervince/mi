from django.test                import TestCase
from django.contrib.auth.models import User
from guardian.shortcuts         import assign_perm
from guardian.shortcuts         import remove_perm
from systems.models             import System

class SystemPermissionsTestCase( TestCase ):

    def test_system_permissions( self ):

        # Create new User and System
        system = System.objects.create( systemname = 'test_system', snapshotid = 0, isActive = True, isTurf = True, exposure = ()  )
        user   =   User.objects.create( username   = 'test_user' )

        # Check that User don't have permission for System initially
        self.assertFalse( user.has_perm( 'view_system', system ) )

        # Set permissions on User for System
        assign_perm( 'view_system', user, system )

        # Check that User have permission for System
        self.assertTrue( user.has_perm( 'view_system', system ) )

        # Set permissions on User for System
        remove_perm( 'view_system', user, system )

        # Check that User don't have permission for System again
        self.assertFalse( user.has_perm( 'view_task', system ) )
