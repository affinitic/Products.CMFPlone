from AccessControl import Unauthorized
from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.utils import set_own_login_name
from Products.CMFPlone.RegistrationTool import get_member_by_login_name


class TestEmailLogin(PloneTestCase.PloneTestCase):

    def testUseEmailProperty(self):
        props = getToolByName(self.portal, 'portal_properties').site_properties
        self.assertTrue(props.hasProperty('use_email_as_login'))
        self.assertEqual(props.getProperty('use_email_as_login'), False)

    def testSetOwnLoginName(self):
        memship = self.portal.portal_membership
        users = self.portal.acl_users.source_users
        member = memship.getAuthenticatedMember()
        self.assertEqual(users.getLoginForUserId(PloneTestCase.default_user),
                         PloneTestCase.default_user)
        set_own_login_name(member, 'maurits')
        self.assertEqual(users.getLoginForUserId(PloneTestCase.default_user),
                         'maurits')

    def testSetLoginNameOfOther(self):
        memship = self.portal.portal_membership
        memship.addMember('maurits', 'secret', [], [])
        member = memship.getMemberById('maurits')
        self.assertRaises(Unauthorized, set_own_login_name, member, 'vanrees')
        # The admin *should* be able to change the login name of
        # another user.  See http://dev.plone.org/plone/ticket/11255
        self.loginAsPortalOwner()
        set_own_login_name(member, 'vanrees')
        users = self.portal.acl_users.source_users
        self.assertEqual(users.getLoginForUserId('maurits'), 'vanrees')

    def testAdminSetOwnLoginName(self):
        memship = self.portal.portal_membership
        self.loginAsPortalOwner()
        member = memship.getAuthenticatedMember()
        # We are not allowed to change a user at the root zope level.
        self.assertRaises(KeyError, set_own_login_name, member, 'vanrees')

    def testNormalMemberIdsAllowed(self):
        pattern = self.portal.portal_registration._ALLOWED_MEMBER_ID_PATTERN
        self.assertTrue(pattern.match('maurits'))
        self.assertTrue(pattern.match('Maur1ts'))
        # PLIP9214: the next test actually passes with the original
        # pattern but fails with the new one as email addresses cannot
        # end in a number:
        #self.assertTrue(pattern.match('maurits76'))
        self.assertTrue(pattern.match('MAURITS'))

    def testEmailMemberIdsAllowed(self):
        pattern = self.portal.portal_registration._ALLOWED_MEMBER_ID_PATTERN
        self.assertTrue(pattern.match('user@example.org'))
        self.assertTrue(pattern.match('user123@example.org'))
        self.assertTrue(pattern.match('user.name@example.org'))
        # PLIP9214: perhaps we should change the regexp so the next
        # test passes as well?
        #self.assertTrue(pattern.match('user+test@example.org'))

    def test_get_member_by_login_name(self):
        memship = self.portal.portal_membership
        context = self.portal
        member = memship.getMemberById(PloneTestCase.default_user)

        # Login name and user name start out the same
        found = get_member_by_login_name(context, PloneTestCase.default_user)
        self.assertEqual(member, found)

        # Change the login name:
        set_own_login_name(member, 'vanrees')
        # A member with this user name is still returned:
        found = get_member_by_login_name(context, PloneTestCase.default_user)
        self.assertEqual(member, found)
        # With the changed login name we can find the member:
        found = get_member_by_login_name(context, 'vanrees')
        self.assertEqual(member, found)

        # Demonstrate that we can find other members than just the
        # default user:
        found = get_member_by_login_name(context, 'portal_owner')
        member = memship.getMemberById('portal_owner')
        self.assertEqual(member, found)
