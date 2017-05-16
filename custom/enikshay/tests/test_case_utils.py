from datetime import datetime
from uuid import uuid4

import pytz

from django.test import TestCase, override_settings

from corehq.form_processor.interfaces.dbaccessors import CaseAccessors
from custom.enikshay.tests.utils import ENikshayCaseStructureMixin, ENikshayLocationStructureMixin
from custom.enikshay.exceptions import NikshayLocationNotFound
from corehq.form_processor.tests.utils import FormProcessorTestUtils

from custom.enikshay.case_utils import (
    get_open_episode_case_from_person,
    get_adherence_cases_between_dates,
    get_occurrence_case_from_episode,
    get_person_case_from_occurrence,
    get_person_case_from_episode,
    update_case,
    get_open_occurrence_case_from_person,
    get_open_episode_case_from_occurrence,
    get_person_locations,
    get_episode_case_from_adherence,
    get_open_referral_case_from_person)


@override_settings(TESTS_SHOULD_USE_SQL_BACKEND=True)
class ENikshayCaseUtilsTests(ENikshayCaseStructureMixin, TestCase):
    @classmethod
    def setUpClass(cls):
        super(ENikshayCaseUtilsTests, cls).setUpClass()
        FormProcessorTestUtils.delete_all_cases()

    def setUp(self):
        super(ENikshayCaseUtilsTests, self).setUp()
        self.cases = self.create_case_structure()

    def tearDown(self):
        super(ENikshayCaseUtilsTests, self).tearDown()
        FormProcessorTestUtils.delete_all_cases()

    def test_get_adherence_cases_between_dates(self):
        adherence_dates = [
            datetime(2005, 7, 10),
            datetime(2016, 8, 10),
            datetime(2016, 8, 11),
            datetime(2016, 8, 12),
            datetime(2017, 9, 10),
        ]
        self.create_adherence_cases(adherence_dates)
        fetched_cases = get_adherence_cases_between_dates(
            self.domain,
            self.person_id,
            start_date=datetime(2016, 7, 1, tzinfo=pytz.UTC),
            end_date=datetime(2016, 8, 13, tzinfo=pytz.UTC),
        )
        self.assertEqual(len(fetched_cases), 3)
        self.assertItemsEqual(
            ["2016-08-10-00-00", "2016-08-11-00-00", "2016-08-12-00-00"],
            [case.case_id for case in fetched_cases]
        )

        fetched_cases = get_adherence_cases_between_dates(
            self.domain,
            self.person_id,
            start_date=datetime(2010, 7, 1, tzinfo=pytz.UTC),
            end_date=datetime(2010, 8, 13, tzinfo=pytz.UTC),
        )
        self.assertEqual(len(fetched_cases), 0)

        fetched_cases = get_adherence_cases_between_dates(
            self.domain,
            self.person_id,
            start_date=datetime(2016, 8, 10, tzinfo=pytz.UTC),
            end_date=datetime(2016, 8, 10, tzinfo=pytz.UTC),
        )
        self.assertEqual(len(fetched_cases), 1)
        self.assertEqual(
            "2016-08-10-00-00",
            fetched_cases[0].case_id,
        )

    def test_get_episode(self):
        self.assertEqual(get_open_episode_case_from_person(self.domain, 'person').case_id, 'episode')

    def test_get_occurrence_case_from_episode(self):
        self.assertEqual(
            get_occurrence_case_from_episode(self.domain, self.episode_id).case_id,
            self.occurrence_id
        )

    def test_get_person_case_from_occurrence(self):
        self.assertEqual(
            get_person_case_from_occurrence(self.domain, self.occurrence_id).case_id,
            self.person_id
        )

    def test_get_person_case_from_episode(self):
        self.assertEqual(
            get_person_case_from_episode(self.domain, self.episode_id).case_id,
            self.person_id
        )

    def test_update_case(self):
        update_properties = {'age': 99}
        self.factory.create_or_update_cases([self.person])
        case_accessors = CaseAccessors(self.domain)
        person_case = case_accessors.get_case(self.person_id)
        self.assertEqual(person_case.dynamic_case_properties().get('age', None), '20')
        update_case(self.domain, self.person_id, update_properties)
        person_case = case_accessors.get_case(self.person_id)
        self.assertEqual(person_case.dynamic_case_properties()['age'], '99')

    def test_get_open_occurrence_case_from_person(self):
        self.assertEqual(
            get_open_occurrence_case_from_person(self.domain, self.person_id).case_id,
            self.occurrence_id
        )

    def test_get_open_episode_case_from_occurrence(self):
        self.assertEqual(
            get_open_episode_case_from_occurrence(self.domain, self.occurrence_id).case_id,
            self.episode_id
        )

    def test_get_episode_case_from_adherence(self):
        adherence_case = self.create_adherence_cases([datetime(2017, 2, 17)])[0]
        self.assertEqual(
            get_episode_case_from_adherence(self.domain, adherence_case.case_id).case_id,
            self.episode_id,
        )

    def test_get_referral_case_from_person(self):
        referral_case_id = uuid4().hex
        self.create_referral_case(referral_case_id)
        self.assertEqual(
            get_open_referral_case_from_person(self.domain, self.person_id).case_id,
            referral_case_id
        )


@override_settings(TESTS_SHOULD_USE_SQL_BACKEND=True)
class TestGetPersonLocations(ENikshayCaseStructureMixin, ENikshayLocationStructureMixin, TestCase):
    def setUp(self):
        super(TestGetPersonLocations, self).setUp()
        self.cases = self.create_case_structure()

    def test_get_person_locations(self):
        self.assign_person_to_location(self.phi.location_id)
        person_case = CaseAccessors(self.domain).get_case(self.person_id)
        expected_locations = {
            'sto': self.sto.metadata['nikshay_code'],
            'dto': self.dto.metadata['nikshay_code'],
            'tu': self.tu.metadata['nikshay_code'],
            'phi': self.phi.metadata['nikshay_code'],
        }
        self.assertEqual(expected_locations, get_person_locations(person_case)._asdict())

    def test_nikshay_location_not_found(self):
        self.assign_person_to_location("-")
        person_case = CaseAccessors(self.domain).get_case(self.person_id)
        with self.assertRaises(NikshayLocationNotFound):
            get_person_locations(person_case)
