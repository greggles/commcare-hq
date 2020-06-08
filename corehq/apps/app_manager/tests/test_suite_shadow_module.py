from django.test import SimpleTestCase

from corehq.apps.app_manager.models import Application, Module, ShadowModule
from corehq.apps.app_manager.tests.util import patch_get_xform_resource_overrides, SuiteMixin, TestXmlMixin


@patch_get_xform_resource_overrides()
class ShadowModuleSuiteTest(SimpleTestCase, TestXmlMixin, SuiteMixin):
    file_path = ('data', 'suite')

    def test_shadow_module(self, *args):
        self._test_generic_suite('shadow_module')

    def test_shadow_module_forms_only(self, *args):
        self._test_generic_suite('shadow_module_forms_only')

    def test_shadow_module_cases(self, *args):
        self._test_generic_suite('shadow_module_cases')


@patch_get_xform_resource_overrides()
class ShadowModuleWithChildSuiteTest(SimpleTestCase, TestXmlMixin, SuiteMixin):
    file_path = ('data', 'suite')

    def setUp(self):
        self.app = Application.new_app('domain', "Untitled Application")

        self.parent = self.app.add_module(Module.new_module('Parent Module', None))
        self.app.new_form(self.parent.id, "Parent Form", None)

        self.child = self.app.add_module(Module.new_module('Child Module', None))
        self.child.root_module_id = self.parent.unique_id
        self.app.new_form(self.child.id, "Child Form", None)

        self.shadow = self.app.add_module(ShadowModule.new_module('Shadow Module', None))

    def test_shadow_module_source_parent(self, *args):
        self.shadow.source_module_id = self.parent.unique_id
        self.shadow_child = self.app.add_module(ShadowModule.new_module('Shadow Child Module', None))
        self.shadow_child.source_module_id = self.child.unique_id
        self.shadow_child.root_module_id = self.shadow.unique_id
        self.assertXmlPartialEqual(self.get_xml('shadow_module_families_source_parent'),
                                   self.app.create_suite(), "./menu")

    def test_shadow_module_source_parent_forms_only(self, *args):
        self.shadow.source_module_id = self.parent.unique_id
        self.shadow_child = self.app.add_module(ShadowModule.new_module('Shadow Child Module', None))
        self.shadow_child.source_module_id = self.child.unique_id
        self.shadow_child.root_module_id = self.shadow.unique_id
        for m in self.app.get_modules():
            m.put_in_root = True
        self.assertXmlPartialEqual(self.get_xml('shadow_module_families_source_parent_forms_only'),
                                   self.app.create_suite(), "./menu")

    def test_shadow_module_source_child(self, *args):
        self.shadow.source_module_id = self.child.unique_id
        self.assertXmlPartialEqual(self.get_xml('shadow_module_families_source_child'),
                                   self.app.create_suite(), "./menu")
